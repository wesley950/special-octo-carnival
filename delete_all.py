import json
import time

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Login and settings
login_email = ""
login_password = ""

# Webdriver
driver = None

def load_config():
    global login_email, login_password

    with open("config.json", "r") as config_file:
        config_json = config_file.read()
        config = json.loads(config_json)
        login_email = config["login_email"]
        login_password = config["login_password"]
    
    print("Config loaded...")

def perform_login():
    global login_email, login_password, driver

    print("Logging in...")

    # initialization
    driver = webdriver.Chrome(executable_path="./chromedriver")
    driver.maximize_window()
    driver.get("https://app.warmupinbox.com/login")

    # find the login fields
    email_input = driver.find_element(By.ID, "input-19")
    password_input = driver.find_element(By.ID, "input-24")
    submit_btn = driver.find_element(By.TAG_NAME, "button")

    # send the credentials and submit
    email_input.send_keys(login_email)
    password_input.send_keys(login_password)
    submit_btn.click()

def delete_all_emails():
    while True:
        # wait for the emails to appear
        emails_table_body = WebDriverWait(driver, 1000).until(EC.presence_of_element_located((By.TAG_NAME, "tbody")))

        # get the table rows (<tr> elements)
        trs_on_tbody = emails_table_body.find_elements(By.TAG_NAME, "tr")

        if len(trs_on_tbody):
            # if there is still emails click the first that appears
            first_table_row = trs_on_tbody[0]
            first_table_row.click()

            # wait for settings tab to load
            settings_tab = WebDriverWait(driver, 1000).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "v-tab")))[-1]

             # wait until this crap is gone
            #WebDriverWait(driver, 1000).until(EC.invisibility_of_element_located((By.CLASS_NAME, "alert-wrapper")))
            alert_wrapper = driver.find_elements(By.CLASS_NAME, "alert-wrapper")
            if len(alert_wrapper):
                driver.execute_script("arguments[0].remove();", alert_wrapper[0])
            WebDriverWait(driver, 1000).until(EC.invisibility_of_element_located((By.CLASS_NAME, "v-overlay__scrim")))


            settings_tab.click()

            # wait for the delete link to appear
            delete_link = WebDriverWait(driver, 1000).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "settings__delete-link")))[-1]
            delete_link.click()
        else:
            break

def main():
    load_config()
    perform_login()
    delete_all_emails()

if __name__ == "__main__":
    main()