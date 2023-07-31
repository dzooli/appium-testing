import os
import unittest
from pathlib import Path

from appium.webdriver import WebElement
from appium.webdriver.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait


class TestBase(unittest.TestCase):
    def __init__(self, methodname: str = "runTest"):
        super().__init__(methodname)
        self.apkPath = Path(__file__).parents[2]
        self.apkPath = os.path.join(str(self.apkPath.resolve()), "install/DuoMobile-3.34.0.apk")
        self.appPackage = "com.duosecurity.duomobile"

    @staticmethod
    def wait_for_element_clickable(driver: WebDriver, element: tuple, timeout: int = 20) -> (WebElement |
                                                                                             list[WebElement] |
                                                                                             None):
        WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(element))
        el = driver.find_elements(element[0], element[1])
        if not el:
            return None
        if len(el) == 1:
            return el[0]
        else:
            return el

    @staticmethod
    def wait_for_element_located(driver: WebDriver, element: tuple, timeout: int = 20) -> (WebElement |
                                                                                           list[WebElement] |
                                                                                           None):
        WebDriverWait(driver, timeout).until(EC.presence_of_element_located(element))
        el = driver.find_elements(element[0], element[1])
        if not el:
            return None
        if len(el) == 1:
            return el[0]
        else:
            return el
