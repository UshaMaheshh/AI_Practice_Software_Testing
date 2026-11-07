from selenium.common.exceptions import (
    StaleElementReferenceException,
    WebDriverException
)
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException

from config import HEADLESS


class SeleniumController:

    def __init__(self):

        options = webdriver.ChromeOptions()

        if HEADLESS:
            options.add_argument("--headless=new")

        options.add_argument("--start-maximized")
        options.add_argument("--disable-notifications")

        service = Service()

        self.driver = webdriver.Chrome(
            service=service,
            options=options
        )

        self.wait = WebDriverWait(self.driver, 30)

        print("Chrome started successfully!")

        print(
            "Chrome version:",
            self.driver.capabilities.get("browserVersion")
        )

    def open_website(self, url):

        print("Opening:", url)

        self.driver.get(url)

        self.wait.until(
            lambda driver: driver.execute_script(
                "return document.readyState"
            ) == "complete"
        )

        # Wait for the Angular application and product area.
        try:
            self.wait.until(
                lambda driver: driver.find_elements(
                    By.CSS_SELECTOR,
                    "app-root"
                )
            )

            self.wait.until(
                lambda driver: len(
                    driver.find_elements(
                        By.CSS_SELECTOR,
                        "a[href*='/product/'], .card"
                    )
                ) > 0
            )

        except TimeoutException:
            print(
                "Product area was not detected within 30 seconds."
            )

        return self.driver.title

    def discover_elements(self):

        elements = {
            "headings": [],
            "buttons": [],
            "links": [],
            "inputs": []
        }

        selectors = {
            "headings": "h1, h2, h3, h4, h5, h6",
            "buttons": "button",
            "links": "a",
            "inputs": "input, textarea, select"
        }

        for category, selector in selectors.items():

            try:
                # Get fresh elements for each category
                found_elements = self.driver.find_elements(
                    By.CSS_SELECTOR, selector
                )

                for index in range(len(found_elements)):

                    try:
                        # Re-fetch the element instead of using
                        # an old WebElement reference
                        current_elements = self.driver.find_elements(
                            By.CSS_SELECTOR, selector
                        )

                        if index >= len(current_elements):
                            continue

                        element = current_elements[index]

                        if not element.is_displayed():
                            continue

                        if category == "links":
                            value = {
                                "text": element.text.strip(),
                                "url": element.get_attribute("href")
                            }

                        elif category == "inputs":
                            value = {
                                "type": element.get_attribute("type"),
                                "name": element.get_attribute("name"),
                                "placeholder": element.get_attribute(
                                    "placeholder"
                                )
                            }

                        else:
                            value = element.text.strip()

                        if value and value not in elements[category]:
                            elements[category].append(value)

                    except StaleElementReferenceException:
                        continue

                    except WebDriverException:
                        continue

            except WebDriverException as error:
                print(
                    f"Could not discover {category}: {error}"
                )

        return elements

    def get_page_content(self):

        return self.driver.find_element(
            By.TAG_NAME,
            "body"
        ).text

    def screenshot(self, path):

        self.driver.save_screenshot(str(path))

    def close(self):

        if self.driver:
            self.driver.quit()
