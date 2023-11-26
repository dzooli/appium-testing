import unittest

from appium import webdriver
from appium.webdriver.common.appiumby import AppiumBy

from . import TestBase


class TestDuoRegistration(TestBase):
    driver: webdriver.Remote | None

    @classmethod
    def get_driver(cls):
        return cls.driver or None

    def setUp(self) -> None:
        caps = {
            "platformName": "Android",
            "appium:automationName": "UiAutomator2",
            "appium:app": str(self.apk_path),
            # "appium:appPackage": self.appPackage,
            # "appium:appActivity": "com.duosecurity.duomobile.account_list.AccountListActivity",
            "appium:ensureWebviewsHavePages": True,
            "appium:nativeWebScreenshot": True,
            "appium:newCommandTimeout": 3600,
            "appium:connectHardwareKeyboard": True,
            "appium:noReset": True
        }
        self.driver = webdriver.Remote("http://127.0.0.1:4723/wd/hub", options=caps)
        self.driver.execute_script("shell", {
            "command": "pm",
            "args": ["grant", self.app_package, "android.permission.CAMERA"]
        })
        if self.driver.is_app_installed(self.app_package):
            self.driver.activate_app(self.app_package)
        else:
            self.fail("App is not installed!")

    def tearDown(self) -> None:
        self.driver.quit()

    def test_manual_account_addition_possible(self):
        self.wait_for_element_clickable(self.driver, (AppiumBy.ID, "add_account")).click()
        self.wait_for_element_clickable(self.driver, (AppiumBy.ID, "addManualButton")).click()
        self.wait_for_element_located(self.driver, (AppiumBy.ID, "account_type_label"))[0].click()
        self.assertIsNotNone(self.driver.find_element(value="key_field"))


if __name__ == '__main__':
    try:
        unittest.main()
    except:  # pylint: disable
        try:
            TestDuoRegistration.get_driver().quit()
        except AttributeError:
            pass
