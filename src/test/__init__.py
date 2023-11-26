import os
import unittest
from pathlib import Path

from appium.webdriver import WebElement
from appium.webdriver.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait


class TestBase(unittest.TestCase):
    def __init__(self, method_name: str = "runTest"):
        super().__init__(method_name)
        self.apk_path = Path(__file__).parents[2]
        self.apk_path = os.path.join(str(self.apk_path.resolve()), "install/DuoMobile-3.34.0.apk")
        self.app_package = "com.duosecurity.duomobile"

    @staticmethod
    def wait_for_element_clickable(driver: WebDriver, element: tuple, timeout: int = 20) -> (WebElement |
                                                                                             list[WebElement] |
                                                                                             None):
        WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(element))
        found_elements: list[WebElement] | list = driver.find_elements(element[0], element[1])
        if not found_elements:
            return None
        if len(found_elements) == 1:
            return found_elements[0]
        return found_elements

    @staticmethod
    def wait_for_element_located(driver: WebDriver, element: tuple, timeout: int = 20) -> (WebElement |
                                                                                           list[WebElement] |
                                                                                           None):
        WebDriverWait(driver, timeout).until(EC.presence_of_element_located(element))
        found_elements: list[WebElement] | list = driver.find_elements(element[0], element[1])
        if not found_elements:
            return None
        if len(found_elements) == 1:
            return found_elements[0]
        return found_elements
