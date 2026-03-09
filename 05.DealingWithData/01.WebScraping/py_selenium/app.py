from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import ChromeOptions

options = ChromeOptions()
options.add_argument("--start-maximized")
driver = webdriver.Chrome(options=options
                          )
driver.get("https://www.google.com")

element = driver.find_element(By.NAME, "q")  # Google search box uses name="q"
element.clear()
element.send_keys("Yasmin Muntaser")
element.send_keys(Keys.RETURN)