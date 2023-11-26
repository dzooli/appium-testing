# Motivation

I'd like to eliminate external dependencies for running Android test suites or use Android cloud testing
services just for some tools like "Duo Mobile" to test MFA authentication. Externally managed services 
are hard to maintain and could be expensive.

Secondary goal is to use only CLI tools and run the test in a CI pipeline.

# Idea

Using an **emulated Android** device for the required tasks.

## Requirements

This process has been tested on Windows 10, for Linux we need to investigate the possibilities later.

- JDK
- NodeJs
- Android cmdline tools
- Android SDK (partially)
- Android emulator
- a running Android Virtual Device
- Appium
- Appium-Inspector (optional, from [this GitHub repo](https://github.com/appium/appium-inspector/releases))
- Test framework
  - unittest
  - appium-python-client

## Setup

### Android Emulator

#### Android SDK

```shell
# Download JDK
curl --output jdk-20.exe https://download.oracle.com/java/20/latest/jdk-20_windows-x64_bin.exe

# Install JDK before continue
# and set JAVA_HOME
export JAVA_HOME=/d/programs/Java/jdk-20  # example path, use your own

# Install Android SDK
mkdir -p install/asdk
cd install/asdk
curl --output asdk-cmdline.zip https://dl.google.com/android/repository/commandlinetools-win-9477386_latest.zip
unzip asdk-cmdline.zip

# Move the tools to its standard directory
mv cmdline-tools latest
mkdir cmdline-tools
mv latest cmdline-tools
```

#### Android SDK packages

```shell
export ANDROID_HOME=$(pwd)
export ANDROID_SDK_ROOT=$ANDROID_HOME
./cmdline-tools/latest/bin/sdkmanager.bat --licenses
./cmdline-tools/latest/bin/sdkmanager.bat "system-images;android-30;google_apis;x86_64" "platforms;android-30" "emulator" "platform-tools" "build-tools;33.0.2"
```

#### AVD (Android Virtual Device) creation

We are going to use Android v11 since this version is the most popular nowadays.

```shell
./cmdline-tools/latest/bin/avdmanager.bat create avd -k "system-images;android-30;google_apis;x86_64" --name Android4Testing_001 -c 512M -d pixel_xl
# verify
./cmdline-tools/latest/bin/avdmanager.bat list avd
```

#### Start the emulator

```shell
./emulator/emulator.exe -avd Android4Testing_001 -detect-image-hang
```

#### Install your "App under test"

This is an optional step since Appium is able to install APKs for you programmatically.

Use another terminal because the emulator is running.

```shell
./platform-tools/adb.exe install -g -r <MyApp.apk>
```

### Appium Server

#### Install

```shell
cd ..
mkdir src
cd src
npm init
npm install appium
# Drivers and plugins
npx appium driver install uiautomator2
npx appium plugin install execute-driver
npx appium plugin install --source=npm appium-device-farm
npx appium plugin install --source=npm appium-dashboard
```

#### Configure

The configuration below is suitable for well protected servers since some insecure features are enabled.

Create your Appium server configuration file ```appium-server-config.json``` like this:

```json
{
  "server": {
    "address": "127.0.0.1",
    "keep-alive-timeout": 800,
    "base-path": "/wd/hub",
    "allow-insecure": [
      "adb_shell",
      "execute_driver_script"
    ],
    "use-plugins": [
      "appium-dashboard",
      "device-farm",
      "execute-driver"
    ],
    "plugin": {
      "device-farm": {
        "platform": "android",
        "skipChromeDownload": true,
        "androidDeviceType": "simulated",
        "iosDeviceType": "simulated",
        "maxSessions": 3
      }
    }
  }
}
```

_More configuration options available from the Appium documentation._

#### Start the server

```shell
# Use your own sdk root !!!
npx appium server --config appium-server-config.json
```

If everything is fine at this point you can access **your Appium and the detected emulated device** on [http://localhost:4723/device-farm/](http://localhost:4723/device-farm/)

## Start testing

### Requirements

Use a new terminal since the Appium server is running on the last used.

- Create and activate a Python virtualenv
- Install ```appium-python-client``` with pip

### Write tests

#### Example test

```python
import unittest
from appium.webdriver import webdriver


driver: webdriver.Remote = None


class TestAnAppWithAppium(unittest.TestCase):
    def setUp(self) -> None:
        global driver
        self.apkPath = "YOUR_PATH_TO_APK"
        self.appPackage = "com.yourdomain.yourpackage"
        caps = {
            "platformName": "Android",
            "appium:automationName": "UiAutomator2",
            "appium:app": str(self.apkPath),
            "appium:ensureWebviewsHavePages": True,
            "appium:nativeWebScreenshot": True,
            "appium:newCommandTimeout": 3600,
            "appium:connectHardwareKeyboard": True,
            "appium:noReset": True
        }
        driver = webdriver.Remote("http://127.0.0.1:4723/wd/hub", caps)
        driver.execute_script("mobile: shell", {
            "command": "pm",
            "args": ["grant", self.appPackage, "android.permission.CAMERA"]  # Example programmatic permission grant
        })
        if driver.is_app_installed(self.appPackage):
            driver.activate_app(self.appPackage)
        else:
            self.fail("App is not installed!")

    def tearDown(self) -> None:
        driver.quit()

    def test_one_function(self):
        driver.find_element(value="aButton")  # Default: Find by ID


if __name__ == '__main__':
    try:
        unittest.main()
    except:
        driver.quit()
```

### Run tests

```shell
python -m unittest
```

## Epilog

### Conclusions

The concept is working, by using emulated mobile devices external mobile testing service is no longer
needed. The setup is relative easy and could run in a CI pipeline with little modifications
(like ```sdkmanager --licenses``` automatic acceptance).

The solution is suitable when no mass of automated mobile testing is necessary and scalable by
connecting more emulated devices to an Appium server and connecting multiple Appium servers to a
Selenium Grid.

### Useful tricks

#### Grant App permissions

From the host:
```shell
cd $ANDROID_SDK_ROOT
./platform-tools/adb.exe shell pm grant "com.your.package" android.permission.your_permission
```

From the test _(needs execute-script plugin for Appium)_:

```python
driver.execute_script("mobile: shell", {
    "command": "pm",
    "args": ["grant", self.app_package, "android.permission.CAMERA"]
})

```

#### Activity and package info

List 3rd-party packages:
```shell
cd $ANDROID_SDK_ROOT
./platform-tools/adb.exe shell pm list packages -3
```

Get the launchable activities:
```shell
cd $ANDROID_SDK_ROOT
./build-tools/33.0.2/aapt d --values badging <path-to-apk-name>
```

Dump running activities:
```shell
cd $ANDROID_SDK_ROOT
./platform-tools/adb.exe shell dumpsys window windows | grep Activity
```

#### Appium selectors (By.*)

- XPATH
- ID
- CLASS_NAME
- ACCESSIBILITY_ID
- CSS_SELECTOR
- ANDROID_UIAUTOMATOR

### Further readings

- [Android in Docker](https://github.com/budtmo/docker-android)
