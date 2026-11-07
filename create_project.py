
from pathlib import Path
import textwrap

ROOT = Path(__file__).resolve().parent

FILES = {

    "requirements.txt": """
selenium>=4.20
pytest>=8.0
python-dotenv>=1.0
openai>=1.30
allure-pytest>=2.13
""",

    ".env.example": """
OPENAI_API_KEY=
OPENAI_MODEL=gpt-4.1-mini
TARGET_URL=https://practicesoftwaretesting.com/
HEADLESS=false
""",

    ".gitignore": """
.venv/
__pycache__/
.pytest_cache/
.env
screenshots/
logs/
reports/
*.pyc
""",

    "config.py": """
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent

BASE_URL = os.getenv(
    "TARGET_URL",
    "https://practicesoftwaretesting.com/"
)

HEADLESS = os.getenv("HEADLESS", "false").lower() == "true"

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")

SCREENSHOT_DIR = BASE_DIR / "screenshots"
LOG_DIR = BASE_DIR / "logs"
REPORT_DIR = BASE_DIR / "reports"

for folder in [SCREENSHOT_DIR, LOG_DIR, REPORT_DIR]:
    folder.mkdir(parents=True, exist_ok=True)
""",

    "browser/__init__.py": "",

    "browser/selenium_controller.py": """
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

from config import HEADLESS


class SeleniumController:

    def __init__(self):

        options = webdriver.ChromeOptions()

        if HEADLESS:
            options.add_argument("--headless=new")

        options.add_argument("--start-maximized")

        self.driver = webdriver.Chrome(options=options)

        self.wait = WebDriverWait(self.driver, 20)

    def open_website(self, url):

        self.driver.get(url)

        self.wait.until(
            lambda d: d.execute_script(
                "return document.readyState"
            ) == "complete"
        )

        return self.driver.title

    def discover_elements(self):

        result = {
            "headings": [],
            "buttons": [],
            "links": [],
            "inputs": []
        }

        selectors = {
            "headings": "h1, h2, h3",
            "buttons": "button",
            "links": "a",
            "inputs": "input, textarea, select"
        }

        for category, selector in selectors.items():

            elements = self.driver.find_elements(
                By.CSS_SELECTOR, selector
            )

            for element in elements:

                if not element.is_displayed():
                    continue

                if category == "links":

                    result[category].append({
                        "text": element.text.strip(),
                        "url": element.get_attribute("href")
                    })

                elif category == "inputs":

                    result[category].append({
                        "type": element.get_attribute("type"),
                        "name": element.get_attribute("name"),
                        "placeholder": element.get_attribute(
                            "placeholder"
                        )
                    })

                else:

                    value = element.text.strip()

                    if value:
                        result[category].append(value)

        return result

    def get_page_content(self):

        return self.driver.find_element(
            By.TAG_NAME, "body"
        ).text

    def screenshot(self, path):

        self.driver.save_screenshot(str(path))

    def close(self):

        if self.driver:
            self.driver.quit()
""",

    "ai_engine/__init__.py": "",

    "ai_engine/test_planner.py": """
import json
from openai import OpenAI

from config import OPENAI_API_KEY, OPENAI_MODEL


def generate_test_cases(discovery):

    if not OPENAI_API_KEY:
        print("OpenAI API key not configured.")
        return []

    client = OpenAI(api_key=OPENAI_API_KEY)

    prompt = f'''
    Analyze this website discovery data:

    {json.dumps(discovery, indent=2)[:12000]}

    Generate functional QA test cases.

    Return ONLY valid JSON in this format:

    {{
      "test_cases": [
        {{
          "id": "TC001",
          "name": "Homepage loads",
          "priority": "High",
          "description": "Verify homepage loads correctly",
          "expected_result": "Homepage is displayed"
        }}
      ]
    }}

    Do not invent functionality that is not supported
    by the discovery data.
    '''

    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {
                "role": "system",
                "content": "You are a professional QA test planner."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        response_format={"type": "json_object"}
    )

    return json.loads(
        response.choices[0].message.content
    )["test_cases"]
""",

    "execution/__init__.py": "",

    "execution/test_runner.py": """
from datetime import datetime


def run_basic_checks(discovery):

    results = []

    results.append({
        "test": "Homepage title exists",
        "status": "PASS" if discovery.get("title") else "FAIL",
        "details": discovery.get("title", "Missing title")
    })

    results.append({
        "test": "Homepage headings discovered",
        "status": "PASS" if discovery.get("elements", {}).get(
            "headings"
        ) else "FAIL",
        "details": "Heading discovery completed"
    })

    results.append({
        "test": "Website navigation discovered",
        "status": "PASS" if discovery.get("elements", {}).get(
            "links"
        ) else "FAIL",
        "details": "Link discovery completed"
    })

    return {
        "execution_time": datetime.now().isoformat(),
        "results": results
    }
""",

    "reporting/__init__.py": "",

    "reporting/report_generator.py": """
import json
from html import escape
from config import REPORT_DIR


def generate_report(discovery, execution):

    json_path = REPORT_DIR / "qa_results.json"

    with open(json_path, "w", encoding="utf-8") as file:

        json.dump({
            "discovery": discovery,
            "execution": execution
        }, file, indent=4)

    rows = ""

    for test in execution["results"]:

        rows += f'''
        <tr>
            <td>{escape(test["test"])}</td>
            <td>{escape(test["status"])}</td>
            <td>{escape(test["details"])}</td>
        </tr>
        '''

    passed = sum(
        x["status"] == "PASS"
        for x in execution["results"]
    )

    failed = len(execution["results"]) - passed

    html = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>AI QA Testing Report</title>
        <style>
            body {{
                font-family: Arial;
                margin: 40px;
                background: #f5f6fa;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                background: white;
            }}
            th, td {{
                padding: 12px;
                border: 1px solid #ddd;
                text-align: left;
            }}
            th {{
                background: #263859;
                color: white;
            }}
            .summary {{
                padding: 20px;
                background: white;
                margin-bottom: 20px;
            }}
        </style>
    </head>
    <body>
        <h1>AI QA Testing Report</h1>
        <div class="summary">
            <p>Website: {escape(discovery["url"])}</p>
            <p>Title: {escape(discovery["title"])}</p>
            <p>Passed: {passed}</p>
            <p>Failed: {failed}</p>
            <p>Executed: {execution["execution_time"]}</p>
        </div>
        <table>
            <tr>
                <th>Test</th>
                <th>Status</th>
                <th>Details</th>
            </tr>
            {rows}
        </table>
    </body>
    </html>
    '''

    html_path = REPORT_DIR / "qa_report.html"

    html_path.write_text(html, encoding="utf-8")

    print("HTML report:", html_path)
    print("JSON report:", json_path)

    return html_path
""",

    "tests/__init__.py": "",

    "tests/test_project.py": """
def test_project_configuration():

    from config import BASE_URL

    assert BASE_URL.startswith("https://")


def test_target_website():

    from config import BASE_URL

    assert "practicesoftwaretesting.com" in BASE_URL
""",

    "main.py": """
import json
import logging

from config import (
    BASE_URL,
    SCREENSHOT_DIR,
    LOG_DIR
)

from browser.selenium_controller import SeleniumController
from execution.test_runner import run_basic_checks
from reporting.report_generator import generate_report

logging.basicConfig(
    filename=LOG_DIR / "execution.log",
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)


def main():

    browser = None

    try:

        print("\\\\n===== AI QA AGENT =====")

        browser = SeleniumController()

        print("Opening:", BASE_URL)

        title = browser.open_website(BASE_URL)

        discovery = {
            "url": BASE_URL,
            "title": title,
            "page_content": browser.get_page_content()[:10000],
            "elements": browser.discover_elements()
        }

        screenshot = SCREENSHOT_DIR / "homepage.png"

        browser.screenshot(screenshot)

        discovery_path = LOG_DIR / "discovery.json"

        with open(
            discovery_path, "w", encoding="utf-8"
        ) as file:

            json.dump(discovery, file, indent=4)

        print("Website title:", title)
        print("Discovered elements:", {
            key: len(value)
            for key, value in discovery["elements"].items()
        })

        execution = run_basic_checks(discovery)

        report = generate_report(discovery, execution)

        print("\\\\n===== EXECUTION RESULTS =====")

        for result in execution["results"]:
            print(result["status"], result["test"])

        print("\\\\nReport generated:", report)

    except Exception:

        logging.exception("QA execution failed")
        raise

    finally:

        if browser:
            browser.close()


if __name__ == "__main__":
    main()
"""
}


def create_project():

    print("\\nCreating AI QA Agent project...")

    for relative_path, content in FILES.items():

        file_path = ROOT / relative_path

        file_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        if file_path.exists():

            print("Skipping existing file:", relative_path)
            continue

        file_path.write_text(
            textwrap.dedent(content).lstrip(),
            encoding="utf-8"
        )

        print("Created:", relative_path)

    for folder in [
        "screenshots",
        "logs",
        "reports"
    ]:

        (ROOT / folder).mkdir(
            parents=True,
            exist_ok=True
        )

    print("\\n================================")
    print("AI QA AGENT PROJECT CREATED!")
    print("================================")
    print("\\nNext steps:")
    print("1. Install dependencies.")
    print("2. Run pytest.")
    print("3. Run python main.py.")


if __name__ == "__main__":
    create_project()
