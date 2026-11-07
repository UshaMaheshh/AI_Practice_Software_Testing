
import json
import logging
import traceback
from datetime import datetime

from config import (
    BASE_URL,
    SCREENSHOT_DIR,
    LOG_DIR,
    REPORT_DIR
)

from browser.selenium_controller import SeleniumController
from execution.test_runner import run_basic_checks
from execution.test_executor import TestExecutor
from reporting.report_generator import generate_report


# ============================================================
# DIRECTORY SETUP
# ============================================================

for directory in (
    SCREENSHOT_DIR,
    LOG_DIR,
    REPORT_DIR
):
    directory.mkdir(parents=True, exist_ok=True)


# ============================================================
# LOGGING CONFIGURATION
# ============================================================

logging.basicConfig(
    filename=LOG_DIR / "execution.log",
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    encoding="utf-8"
)


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def print_step(message):

    print("\n" + "=" * 60)
    print(message)
    print("=" * 60)


def save_discovery(discovery):

    discovery_path = LOG_DIR / "discovery.json"

    with open(
        discovery_path,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            discovery,
            file,
            indent=4,
            ensure_ascii=False,
            default=str
        )

    return discovery_path


def count_status(results, status):

    return sum(
        1
        for result in results
        if str(result.get("status", "")).upper() == status
    )


# ============================================================
# MAIN EXECUTION
# ============================================================

def main():

    browser = None

    try:

        print("\n")
        print("*" * 60)
        print("       AUTONOMOUS AI QA TESTING AGENT")
        print("*" * 60)

        # ----------------------------------------------------
        # STEP 1: LAUNCH BROWSER
        # ----------------------------------------------------

        print_step("STEP 1: Launching Chrome browser")

        browser = SeleniumController()

        print("Chrome launched successfully!")

        input(
            "\nPress ENTER to start website exploration..."
        )

        # ----------------------------------------------------
        # STEP 2: OPEN WEBSITE
        # ----------------------------------------------------

        print_step("STEP 2: Opening Practice Software Testing")

        print("Target website:", BASE_URL)

        title = browser.open_website(BASE_URL)

        print("Website loaded successfully!")
        print("Page title:", title)

        # ----------------------------------------------------
        # STEP 3: DISCOVER WEBSITE ELEMENTS
        # ----------------------------------------------------

        print_step("STEP 3: Discovering website elements")

        elements = browser.discover_elements()

        discovery = {
            "url": BASE_URL,
            "title": title,
            "execution_date": datetime.now().isoformat(),
            "page_content": browser.get_page_content()[:10000],
            "elements": elements
        }

        for category, values in elements.items():

            print(
                category.capitalize(),
                "discovered:",
                len(values)
            )

        # ----------------------------------------------------
        # STEP 4: CAPTURE SCREENSHOT
        # ----------------------------------------------------

        print_step("STEP 4: Capturing screenshot")

        screenshot_path = SCREENSHOT_DIR / "homepage.png"

        browser.screenshot(screenshot_path)

        print("Screenshot saved:", screenshot_path)

        # ----------------------------------------------------
        # STEP 5: SAVE DISCOVERY INFORMATION
        # ----------------------------------------------------

        print_step("STEP 5: Saving discovery information")

        discovery_path = save_discovery(discovery)

        print("Discovery saved:", discovery_path)

        # ----------------------------------------------------
        # STEP 6: EXECUTE BASIC QA CHECKS
        # ----------------------------------------------------

        print_step("STEP 6: Executing basic QA checks")

        basic_execution = run_basic_checks(discovery)

        basic_results = basic_execution.get("results", [])

        for result in basic_results:

            print(
                result.get("status", "UNKNOWN"),
                "-",
                result.get("test", result.get("name", "Unnamed check"))
            )

        # ----------------------------------------------------
        # STEP 7: EXECUTE SELENIUM TEST CASES
        # ----------------------------------------------------

        print_step("STEP 7: Executing Selenium test cases")

        input(
            "\nPress ENTER to start automated test execution..."
        )

        # Pass the SeleniumController.
        # TestExecutor accesses its actual WebDriver using
        # browser.driver.

        executor = TestExecutor(browser)

        automated_execution = executor.run_all()

        print("\nAutomated tests completed.")

        # ----------------------------------------------------
        # STEP 8: COMBINE RESULTS FOR REPORTING
        # ----------------------------------------------------

        print_step("STEP 8: Preparing QA report")

        automated_results = automated_execution.get(
            "results", []
        )

        combined_results = (
            basic_results + automated_results
        )

        # Calculate counts from the actual combined results.

        total_passed = count_status(
            combined_results,
            "PASS"
        )

        total_failed = count_status(
            combined_results,
            "FAIL"
        )

        total_not_executed = count_status(
            combined_results,
            "NOT_EXECUTED"
        )

        total_checks = len(combined_results)

        execution = {
            "execution_time": datetime.now().isoformat(),

            "total": total_checks,

            "passed": total_passed,

            "failed": total_failed,

            "not_executed": total_not_executed,

            "results": combined_results,

            "basic_summary": {
                "total": len(basic_results),
                "passed": count_status(
                    basic_results, "PASS"
                ),
                "failed": count_status(
                    basic_results, "FAIL"
                )
            },

            "automated_summary": {
                "total": automated_execution.get(
                    "total", len(automated_results)
                ),

                "passed": automated_execution.get(
                    "passed", 0
                ),

                "failed": automated_execution.get(
                    "failed", 0
                ),

                "not_executed": automated_execution.get(
                    "not_executed", 0
                )
            }
        }

        # ----------------------------------------------------
        # STEP 9: GENERATE HTML AND JSON REPORTS
        # ----------------------------------------------------

        print_step("STEP 9: Generating HTML report")

        report_path = generate_report(
            discovery,
            execution
        )

        print("\nHTML report generated successfully!")
        print("HTML report:", report_path)

        # ----------------------------------------------------
        # STEP 10: FINAL EXECUTION SUMMARY
        # ----------------------------------------------------

        print_step("FINAL QA EXECUTION SUMMARY")

        print("Website:", BASE_URL)
        print("Page title:", title)

        print("\nBasic QA checks:", len(basic_results))

        print(
            "Automated test cases:",
            len(automated_results)
        )

        print("\nTotal checks:", total_checks)
        print("Passed:", total_passed)
        print("Failed:", total_failed)
        print("Not executed:", total_not_executed)

        if total_checks > 0:

            pass_percentage = (
                total_passed / total_checks
            ) * 100

            print(
                "Pass percentage:",
                f"{pass_percentage:.2f}%"
            )

        print("\nGenerated files:")

        print("Screenshot:", screenshot_path)

        print("Discovery:", discovery_path)

        print(
            "Test results:",
            REPORT_DIR / "execution_results.json"
        )

        print(
            "HTML report:",
            report_path
        )

        print(
            "JSON report:",
            REPORT_DIR / "qa_results.json"
        )

        print_step("TESTING COMPLETED")

        input(
            "\nChrome will remain open. "
            "Press ENTER when you want to close the browser..."
        )

    except KeyboardInterrupt:

        print("\nExecution interrupted by user.")

        logging.warning(
            "QA execution interrupted by user."
        )

    except Exception as error:

        print_step("AN ERROR OCCURRED")

        print("Error:", str(error))

        logging.exception(
            "QA execution failed"
        )

        traceback.print_exc()

        input(
            "\nPress ENTER to close the program..."
        )

    finally:

        # ----------------------------------------------------
        # CLOSE BROWSER
        # ----------------------------------------------------

        if browser is not None:

            print("\nClosing Chrome browser...")

            try:

                browser.close()

                print("Browser closed successfully.")

            except Exception as close_error:

                print(
                    "Browser closing error:",
                    close_error
                )

                logging.exception(
                    "Browser cleanup failed"
                )

        print("\nAI QA Agent execution finished.")


# ============================================================
# APPLICATION ENTRY POINT
# ============================================================

if __name__ == "__main__":

    main()
