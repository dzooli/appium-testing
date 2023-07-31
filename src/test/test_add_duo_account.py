import unittest

from appium import webdriver
from appium.webdriver.common.appiumby import AppiumBy

from . import TestBase

driver: webdriver.Remote = None


class TestDuoRegistration(TestBase):
    def setUp(self) -> None:
        global driver
        caps = {
            "platformName": "Android",
            "appium:automationName": "UiAutomator2",
            "appium:app": str(self.apkPath),
            # "appium:appPackage": self.appPackage,
            # "appium:appActivity": "com.duosecurity.duomobile.account_list.AccountListActivity",
            "appium:ensureWebviewsHavePages": True,
            "appium:nativeWebScreenshot": True,
            "appium:newCommandTimeout": 3600,
            "appium:connectHardwareKeyboard": True,
            "appium:noReset": True
        }
        driver = webdriver.Remote("http://127.0.0.1:4723/wd/hub", caps)
        driver.execute_script("mobile: shell", {
            "command": "pm",
            "args": ["grant", self.appPackage, "android.permission.CAMERA"]
        })
        if driver.is_app_installed(self.appPackage):
            driver.activate_app(self.appPackage)
        else:
            self.fail("App is not installed!")

    def tearDown(self) -> None:
        driver.quit()

    def test_manual_account_addition_possible(self):
        self.wait_for_element_clickable(driver, (AppiumBy.ID, "add_account")).click()
        self.wait_for_element_clickable(driver, (AppiumBy.ID, "addManualButton")).click()
        self.wait_for_element_located(driver, (AppiumBy.ID, "account_type_label"))[0].click()
        self.assertIsNotNone(driver.find_element(value="key_field"))


if __name__ == '__main__':
    try:
        unittest.main()
    except:
        driver.quit()
