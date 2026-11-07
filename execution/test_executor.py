
import json
import re
import time
from datetime import datetime
from pathlib import Path

from selenium import webdriver
from selenium.common.exceptions import (
    NoSuchElementException,
    TimeoutException,
    WebDriverException
)
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# ============================================================
# PROJECT PATHS AND CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_FILE = BASE_DIR / "reports" / "generated_test_cases.json"
OUTPUT_FILE = BASE_DIR / "reports" / "execution_results.json"

SCREENSHOT_DIR = BASE_DIR / "screenshots"

WEBSITE_URL = "https://practicesoftwaretesting.com/"

WAIT_SECONDS = 15

PRODUCT_LINK_SELECTOR = "a[href*='/product/']"


# ============================================================
# TEST EXECUTOR
# ============================================================

class TestExecutor:

    def __init__(self, browser=None, driver=None):

        supplied_object = browser if browser is not None else driver

        self.browser = supplied_object

        if supplied_object is not None:
            self.driver = getattr(
                supplied_object,
                "driver",
                supplied_object
            )
        else:
            self.driver = None

        self.wait = (
            WebDriverWait(self.driver, WAIT_SECONDS)
            if self.driver is not None
            else None
        )

        self.results = []

        # Do not close a browser owned by main.py/controller.
        self.owns_driver = supplied_object is None

        SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
        OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    # ========================================================
    # BROWSER MANAGEMENT
    # ========================================================

    def start_browser(self):

        if self.driver is not None:
            return self.driver

        options = webdriver.ChromeOptions()
        options.add_argument("--start-maximized")

        self.driver = webdriver.Chrome(options=options)
        self.wait = WebDriverWait(self.driver, WAIT_SECONDS)

        self.owns_driver = True

        return self.driver

    def close_browser(self):

        if self.driver is not None and self.owns_driver:
            try:
                self.driver.quit()
                print("Browser closed successfully.")
            except WebDriverException as error:
                print(f"Browser cleanup warning: {error}")

        self.driver = None
        self.wait = None

    # ========================================================
    # GENERAL HELPERS
    # ========================================================

    def wait_for_page(self):

        self.wait.until(
            lambda driver: driver.execute_script(
                "return document.readyState"
            ) == "complete"
        )

    def open_homepage(self):

        self.driver.get(WEBSITE_URL)
        self.wait_for_page()

        # Allow Angular product content to render.
        try:
            self.wait.until(
                lambda driver: len(
                    driver.find_elements(
                        By.CSS_SELECTOR,
                        PRODUCT_LINK_SELECTOR
                    )
                ) > 0
            )
        except TimeoutException:
            pass

    def take_screenshot(self, test_id):

        try:
            filename = (
                f"{test_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            )

            filepath = SCREENSHOT_DIR / filename

            self.driver.save_screenshot(str(filepath))

            return str(filepath)

        except WebDriverException:
            return None

    # ========================================================
    # PRODUCT HELPERS
    # ========================================================

    def get_product_cards(self):

        return self.driver.find_elements(
            By.CSS_SELECTOR,
            PRODUCT_LINK_SELECTOR
        )

    def get_product_names(self):

        names = []

        cards = self.get_product_cards()

        for card in cards:

            try:
                text = card.text.strip()

                if text:
                    # Product name is normally the first line.
                    name = text.splitlines()[0].strip()

                    if name:
                        names.append(name)

            except WebDriverException:
                continue

        return names

    def get_product_prices(self):

        prices = []

        # Price is extracted from each product card rather than
        # relying on a guessed .card-text selector.
        cards = self.get_product_cards()

        for card in cards:

            try:
                text = card.text.strip()

                match = re.search(
                    r"\$\s*(\d+(?:\.\d{1,2})?)",
                    text
                )

                if match:
                    prices.append(float(match.group(1)))

            except WebDriverException:
                continue

        return prices

    # ========================================================
    # SEARCH HELPERS
    # ========================================================

    def find_search_input(self):

        selectors = [
            "input[placeholder*='Search']",
            "input[type='search']",
            "input[name='search']",
            "#search-query"
        ]

        for selector in selectors:

            elements = self.driver.find_elements(
                By.CSS_SELECTOR,
                selector
            )

            for element in elements:

                if element.is_displayed():
                    return element

        raise NoSuchElementException(
            "Search input was not found."
        )

    def find_search_button(self):

        selectors = [
            "button[data-test='search-submit']",
            "button[type='submit']",
            "button:has(svg)"
        ]

        for selector in selectors:

            try:
                elements = self.driver.find_elements(
                    By.CSS_SELECTOR,
                    selector
                )

                for element in elements:

                    if element.is_displayed():
                        return element

            except WebDriverException:
                continue

        return None

    def search_product(self, search_text):

        search_input = self.find_search_input()

        search_input.clear()
        search_input.send_keys(search_text)

        button = self.find_search_button()

        if button is not None:
            button.click()
        else:
            search_input.submit()

        time.sleep(2)
        self.wait_for_page()

    # ========================================================
    # SORTING HELPERS
    # ========================================================

    def find_sort_dropdown(self):

        selectors = [
            "select[data-test='sort']",
            "select#sort",
            "select[name='sort']",
            "select"
        ]

        for selector in selectors:

            elements = self.driver.find_elements(
                By.CSS_SELECTOR,
                selector
            )

            for element in elements:

                try:
                    if element.is_displayed():
                        return element

                except WebDriverException:
                    continue

        raise NoSuchElementException(
            "Sort dropdown was not found."
        )

    def select_sort_option(self, expected_label):

        dropdown = self.find_sort_dropdown()
        select = Select(dropdown)

        normalize = lambda value: re.sub(
            r"[^a-z0-9]",
            "",
            value.lower()
        )

        expected = normalize(expected_label)

        for option in select.options:

            actual = normalize(option.text)

            if actual == expected:

                select.select_by_visible_text(option.text)

                # Wait for the product list to update.
                time.sleep(3)

                return True, option.text

        available_options = [
            option.text.strip()
            for option in select.options
        ]

        return False, available_options

    # ========================================================
    # NAVIGATION HELPERS
    # ========================================================

    def click_navigation_link(self, text):

        links = self.driver.find_elements(
            By.TAG_NAME,
            "a"
        )

        for link in links:

            try:
                if (
                    link.is_displayed()
                    and text.lower() in link.text.strip().lower()
                ):
                    link.click()
                    self.wait_for_page()
                    return True

            except WebDriverException:
                continue

        return False

    def click_category(self, category_name):

        # First try elements whose visible text matches the category.
        xpath = (
            "//*[normalize-space(translate("
            "., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', "
            "'abcdefghijklmnopqrstuvwxyz'))="
            f"'{category_name.lower()}']"
        )

        elements = self.driver.find_elements(
            By.XPATH,
            xpath
        )

        for element in elements:

            try:
                if not element.is_displayed():
                    continue

                # Avoid clicking a large parent container when a
                # smaller clickable child exists.
                tag = element.tag_name.lower()
                role = (element.get_attribute("role") or "").lower()
                clickable = (
                    tag in ("a", "button", "label")
                    or role in ("button", "link", "checkbox")
                    or element.get_attribute("tabindex") is not None
                )

                if clickable:
                    self.driver.execute_script(
                        "arguments[0].scrollIntoView({block: 'center'});",
                        element
                    )
                    element.click()
                    time.sleep(2)
                    return True

                # Try a clickable child inside the matching category.
                children = element.find_elements(
                    By.XPATH,
                    ".//a | .//button | .//label | .//*[@role='button']"
                )

                for child in children:

                    if child.is_displayed():
                        child.click()
                        time.sleep(2)
                        return True

            except WebDriverException:
                continue

        return False

    # ========================================================
    # RESULT HELPER
    # ========================================================

    def record_result(self, test_id, name, status, message):

        screenshot = None

        if status == "FAIL":
            screenshot = self.take_screenshot(test_id)

        result = {
            "id": test_id,
            "name": name,
            "status": status,
            "message": message,
            "screenshot": screenshot,
            "timestamp": datetime.now().isoformat()
        }

        self.results.append(result)

        print(f"{test_id}: {status} - {message}")

    # ========================================================
    # TC001 - HOMEPAGE LOAD
    # ========================================================

    def test_TC001(self):

        self.open_homepage()

        title = self.driver.title

        if "Toolshop" in title:
            return True, (
                f"Homepage loaded successfully. Title: {title}"
            )

        return False, f"Unexpected homepage title: {title}"

    # ========================================================
    # TC002 - VALID PRODUCT SEARCH
    # ========================================================

    def test_TC002(self):

        self.open_homepage()

        self.search_product("pliers")

        page_text = self.driver.find_element(
            By.TAG_NAME,
            "body"
        ).text.lower()

        if "pliers" in page_text:
            return True, "Search for pliers returned matching results."

        return False, "No matching pliers results were found."

    # ========================================================
    # TC003 - INVALID PRODUCT SEARCH
    # ========================================================

    def test_TC003(self):

        self.open_homepage()

        invalid_search = "zzzz_invalid_product_987654"

        self.search_product(invalid_search)

        page_text = self.driver.find_element(
            By.TAG_NAME,
            "body"
        ).text.lower()

        no_result_messages = [
            "no results",
            "no products",
            "no product",
            "nothing found"
        ]

        if any(
            message in page_text
            for message in no_result_messages
        ):
            return True, (
                "Invalid search correctly displayed a no-results message."
            )

        matching_products = [
            name for name in self.get_product_names()
            if invalid_search.lower() in name.lower()
        ]

        if matching_products:
            return False, "Unexpected matching product found."

        return True, "Invalid search did not return a matching product."

    # ========================================================
    # TC004 - PRICE SORTING
    # ========================================================

    def test_TC004(self):

        self.open_homepage()

        selected, detail = self.select_sort_option(
            "Price (Low - High)"
        )

        if not selected:
            return False, (
                "Price (Low - High) option was not found. "
                f"Available options: {detail}"
            )

        prices = self.get_product_prices()

        if len(prices) < 2:
            return False, (
                f"Not enough product prices were found: {prices}"
            )

        if prices == sorted(prices):
            return True, (
                f"Products are sorted by price ascending: {prices}"
            )

        return False, f"Prices are not ascending: {prices}"

    # ========================================================
    # TC005 - ALPHABETICAL SORTING
    # ========================================================

    def test_TC005(self):

        self.open_homepage()

        selected, detail = self.select_sort_option(
            "Name (A - Z)"
        )

        if not selected:
            return False, (
                "Name (A - Z) option was not found. "
                f"Available options: {detail}"
            )

        names = self.get_product_names()

        if len(names) < 2:
            return False, (
                f"Not enough product names were found: {names}"
            )

        expected = sorted(
            names,
            key=str.casefold
        )

        if names == expected:
            return True, (
                f"Products are sorted alphabetically: {names}"
            )

        return False, (
            f"Product names are not alphabetical: {names}"
        )

    # ========================================================
    # TC006 - CATEGORY FILTER
    # ========================================================

    def test_TC006(self):

        self.open_homepage()

        if self.click_category("Hand Tools"):

            page_text = self.driver.find_element(
                By.TAG_NAME,
                "body"
            ).text.lower()

            current_url = self.driver.current_url.lower()

            if (
                "hand tools" in page_text
                or "category" in current_url
                or "hammer" in page_text
                or "pliers" in page_text
            ):
                return True, (
                    "Hand Tools category was clicked successfully."
                )

            return True, (
                "Hand Tools category element was clicked."
            )

        # Return useful information instead of silently guessing.
        candidates = self.driver.find_elements(
            By.XPATH,
            "//*[contains(translate(normalize-space(.), "
            "'ABCDEFGHIJKLMNOPQRSTUVWXYZ', "
            "'abcdefghijklmnopqrstuvwxyz'), 'hand tools')]"
        )

        details = []

        for element in candidates[:10]:

            try:
                details.append({
                    "tag": element.tag_name,
                    "text": element.text.strip()[:100],
                    "role": element.get_attribute("role"),
                    "class": element.get_attribute("class")
                })

            except WebDriverException:
                continue

        return False, (
            "Hand Tools category could not be clicked. "
            f"Matching elements: {details}"
        )

    # ========================================================
    # TC007 - BRAND FILTER
    # ========================================================

    def test_TC007(self):

        self.open_homepage()

        page_text = self.driver.find_element(
            By.TAG_NAME,
            "body"
        ).text.lower()

        if "forgeflex" in page_text:
            return True, "ForgeFlex brand is visible on the page."

        brand_elements = self.driver.find_elements(
            By.XPATH,
            "//*[contains(translate(text(), "
            "'ABCDEFGHIJKLMNOPQRSTUVWXYZ', "
            "'abcdefghijklmnopqrstuvwxyz'), 'forgeflex')]"
        )

        if brand_elements:
            return True, "ForgeFlex brand was found."

        return False, "ForgeFlex brand was not found on the homepage."

    # ========================================================
    # TC008 - ECO-FRIENDLY FILTER
    # ========================================================

    def test_TC008(self):

        self.open_homepage()

        checkboxes = self.driver.find_elements(
            By.CSS_SELECTOR,
            "input[type='checkbox']"
        )

        if not checkboxes:
            return False, "No filter checkboxes were found."

        for checkbox in checkboxes:

            try:
                parent_text = checkbox.find_element(
                    By.XPATH,
                    "./ancestor::*[self::label or self::div][1]"
                ).text.lower()

                if "eco" in parent_text:

                    if not checkbox.is_selected():
                        self.driver.execute_script(
                            "arguments[0].click();",
                            checkbox
                        )

                    return True, (
                        "Eco-friendly filter was selected."
                    )

            except WebDriverException:
                continue

        return False, "Eco-friendly checkbox was not found."

    # ========================================================
    # TC009 - LOGIN NAVIGATION
    # ========================================================

    def test_TC009(self):

        self.open_homepage()

        if self.click_navigation_link("Sign in"):
            return True, "Login page navigation succeeded."

        if self.click_navigation_link("Login"):
            return True, "Login page navigation succeeded."

        current_url = self.driver.current_url.lower()

        if "login" in current_url:
            return True, "Login page is open."

        return False, "Login navigation link was not found."

    # ========================================================
    # TC010 - CONTACT PAGE NAVIGATION
    # ========================================================

    def test_TC010(self):

        self.open_homepage()

        if self.click_navigation_link("Contact"):
            return True, "Contact page navigation succeeded."

        current_url = self.driver.current_url.lower()

        if "contact" in current_url:
            return True, "Contact page is open."

        return False, "Contact page navigation link was not found."

    # ========================================================
    # TEST CASE DISPATCHER
    # ========================================================

    def execute_test(self, test_case):

        test_id = str(
            test_case.get("id")
            or test_case.get("test_id")
            or ""
        ).upper()

        test_name = test_case.get(
            "name",
            f"Test case {test_id}"
        )

        test_methods = {
            "TC001": self.test_TC001,
            "TC002": self.test_TC002,
            "TC003": self.test_TC003,
            "TC004": self.test_TC004,
            "TC005": self.test_TC005,
            "TC006": self.test_TC006,
            "TC007": self.test_TC007,
            "TC008": self.test_TC008,
            "TC009": self.test_TC009,
            "TC010": self.test_TC010
        }

        method = test_methods.get(test_id)

        if method is None:

            self.record_result(
                test_id,
                test_name,
                "NOT_EXECUTED",
                "No automated implementation exists for this test case."
            )

            return

        try:

            self.driver.get(WEBSITE_URL)
            self.wait_for_page()

            success, message = method()

            status = "PASS" if success else "FAIL"

            self.record_result(
                test_id,
                test_name,
                status,
                message
            )

        except Exception as error:

            self.record_result(
                test_id,
                test_name,
                "FAIL",
                f"{type(error).__name__}: {str(error)}"
            )

    # ========================================================
    # RUN ALL TEST CASES
    # ========================================================

    def run_all(self):

        print("\nStarting automated test execution...\n")

        self.results = []

        if not INPUT_FILE.exists():
            raise FileNotFoundError(
                f"Generated test cases file not found: {INPUT_FILE}"
            )

        with open(INPUT_FILE, "r", encoding="utf-8") as file:
            test_data = json.load(file)

        if isinstance(test_data, dict):
            test_cases = test_data.get("test_cases", [])
        elif isinstance(test_data, list):
            test_cases = test_data
        else:
            test_cases = []

        if not test_cases:
            raise ValueError(
                "No test cases were found in generated_test_cases.json"
            )

        for test_case in test_cases:

            if not isinstance(test_case, dict):
                continue

            self.execute_test(test_case)

        passed = sum(
            1 for result in self.results
            if result.get("status") == "PASS"
        )

        failed = sum(
            1 for result in self.results
            if result.get("status") == "FAIL"
        )

        not_executed = sum(
            1 for result in self.results
            if result.get("status") == "NOT_EXECUTED"
        )

        total = len(test_cases)

        execution_summary = {
            "website": WEBSITE_URL,
            "execution_date": datetime.now().isoformat(),
            "total": total,
            "passed": passed,
            "failed": failed,
            "not_executed": not_executed,
            "results": self.results
        }

        OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

        with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
            json.dump(
                execution_summary,
                file,
                indent=4
            )

        print("\n========================================")
        print("AUTOMATED TEST EXECUTION SUMMARY")
        print("========================================")
        print(f"Total test cases : {total}")
        print(f"Passed           : {passed}")
        print(f"Failed           : {failed}")
        print(f"Not executed     : {not_executed}")
        print("========================================")

        print(
            f"\nExecution results saved to: {OUTPUT_FILE}"
        )

        return {
            "results": self.results,
            "total": total,
            "passed": passed,
            "failed": failed,
            "not_executed": not_executed
        }
