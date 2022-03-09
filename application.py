from argparse import Action
import json
import time

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

# Login and settings
login_email = ""
login_password = ""
change_settings = []

# Webdriver
driver = None

def load_config():
    global login_email, login_password, change_settings

    with open("config.json", "r") as file:
        config_json = json.loads(file.read())
        login_email = config_json["login_email"]
        login_password = config_json["login_password"]
        change_settings = config_json["change_settings"]
    
    print("Settings loaded...")

def init_and_login():
    global driver

    driver = webdriver.Chrome(executable_path="./chromedriver")

    # Go to login page
    driver.get("https://app.warmupinbox.com/login")

    # Find login fields and submit
    email_field = driver.find_element_by_id("input-19")
    password_field = driver.find_element_by_id("input-24")
    submit_btm = driver.find_element_by_tag_name("button")

    email_field.send_keys(login_email)
    password_field.send_keys(login_password)
    submit_btm.click()

    print("Logged in...")

def list_emails():
    global driver

    # wait for table body
    table_body = WebDriverWait(driver, 1000).until(EC.presence_of_element_located((By.TAG_NAME, "tbody")))

    # get table rows
    table_rows = WebDriverWait(driver, 1000).until(EC.visibility_of_all_elements_located((By.TAG_NAME, "tr")))
    return table_rows

def get_email_from_table_row(tr):
    return tr.find_elements_by_tag_name("div")[-1].text # the div with the email string is the last

def get_first_email(emails):
    for email in emails:
        return get_email_from_table_row(email)
    return None

def navigate_next_on_pagination():
    global driver
    pagination_nxt_btn = WebDriverWait(driver, 1000).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "v-pagination__navigation")))[-1]
    pagination_nxt_btn.click()

def begin_changes():
    last_changed_email = None
    current_page = 1

    while True:
        for i in range(current_page):
            navigate_next_on_pagination()

        # do the first email
        current_email = 0
        emails_in_page = list_emails()
        email_count = len(emails_in_page)
        

        while current_email != email_count:
            driver.execute_script("document.body.scrollIntoView(true);")
            email_tr = emails_in_page[current_email]
            email_tr.click()

            # find the settings tab and click it
            settings_tab = WebDriverWait(driver, 1000).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "v-tab")))[1] # the settings tab is the second
            settings_tab.click()

            # wait for the edit schedule link and click it
            edit_schedule_link = WebDriverWait(driver, 1000).until(EC.presence_of_element_located((By.XPATH, "//*[@id=\"app\"]/div[1]/main/div/div[2]/div/div/div[2]/div/div[2]/div/div[2]/div/div[1]/div/div[1]/button")))
            edit_schedule_link.click()

            # wait for the panel where the fields are located (this is easier and less error prone)
            fields_panel = WebDriverWait(driver, 1000).until(EC.presence_of_element_located((By.CLASS_NAME, "v-card")))

            # wait for the 4 fields and save button
            field_1 = fields_panel.find_elements_by_tag_name("input")[0]
            field_2 = fields_panel.find_elements_by_tag_name("input")[1]
            field_3 = fields_panel.find_elements_by_tag_name("input")[2]
            field_4 = fields_panel.find_elements_by_tag_name("input")[3]
            save_btn = fields_panel.find_element_by_tag_name("button")

            # clear and send the new values
            field_1_str = "%d" % (change_settings[0], )
            field_2_str = "%d" % (change_settings[1], )
            field_3_str = "%d" % (change_settings[2], )
            field_4_str = "%d" % (change_settings[3], )

            field_1.send_keys(Keys.CONTROL, "a")
            field_1.send_keys(field_1_str)
            
            field_2.send_keys(Keys.CONTROL, "a")
            field_2.send_keys(field_2_str)
            
            field_3.send_keys(Keys.CONTROL, "a")
            field_3.send_keys(field_3_str)
            
            field_4.send_keys(Keys.CONTROL, "a")
            field_4.send_keys(field_4_str)
            
            save_btn.click()

            # wait until the labels are visible to go back
            running_label = WebDriverWait(driver, 1000).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "inbox-control__paused")))[-1]
            if running_label.text == "Running":
                parent_of_label = running_label.find_element_by_xpath("./..")
                toggle_element = parent_of_label.find_element_by_tag_name("input")
                toggle_element.click()
                time.sleep(1)

            driver.execute_script("window.history.go(-1)")

            current_email += 1
            emails_in_page = list_emails()
            email_count = len(emails_in_page)

        current_page += 1
        current_email = 0
        
    # list all accounts
    # for each account:
    #   click and wait for "settings" to load, then click it
    #   wait for "edit schedule" to load, then click it
    #   wait for inputs to load and send the new values
    #   click "save", then click "inbox"
    #   wait for elements to load and keep navigating until the page is correct
    # navigate to next page if there is another one

def main():
    global driver

    load_config()
    init_and_login()
    begin_changes()
    driver.quit()

if __name__ == '__main__':
    main()