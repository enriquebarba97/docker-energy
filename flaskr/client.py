from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import uuid

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
driver.get("http://127.0.0.1:5000/")

for i in range(0, 10):
    driver.find_element(By.LINK_TEXT, "Flaskr").click()

    driver.find_element(By.LINK_TEXT, "Register").click()

    name = str(uuid.uuid4())
    username = driver.find_element(By.ID, "username")
    username.clear()
    username.send_keys(name)


    password = driver.find_element(By.ID, "password")
    password.clear()
    password.send_keys("test")
    password.send_keys(Keys.RETURN)


    driver.find_element(By.LINK_TEXT, "Log In").click()

    username = driver.find_element(By.ID, "username")
    username.clear()
    username.send_keys(name)


    password = driver.find_element(By.ID, "password")
    password.clear()
    password.send_keys("test")
    password.send_keys(Keys.RETURN)


    driver.find_element(By.LINK_TEXT, "New").click()

    title = driver.find_element(By.ID, "title")
    title.clear()
    title.send_keys("test")

    body = driver.find_element(By.ID, "body")
    body.clear()
    body.send_keys("test test test test")
    body.send_keys(Keys.RETURN)

    driver.find_element(By.XPATH, '//input[@type="submit" and @value="Save"]').click()


    driver.find_element(By.LINK_TEXT, "Edit").click()

    title = driver.find_element(By.ID, "title")
    title.clear()
    title.send_keys("test 2")

    body = driver.find_element(By.ID, "body")
    body.clear()
    body.send_keys("test 2 test 2 test 2 test 2")
    body.send_keys(Keys.RETURN)


    driver.find_element(By.XPATH, '//input[@type="submit" and @value="Save"]').click()


    driver.find_element(By.LINK_TEXT, "Edit").click()


    driver.find_element(By.XPATH, '//input[@type="submit" and @value="Delete"]').click()
    driver.switch_to.alert.accept()


    driver.find_element(By.LINK_TEXT, "Log Out").click()


driver.close()

    # driver.find_element(By.LINK_TEXT, "Flaskr").click()



