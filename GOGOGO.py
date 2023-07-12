from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


# Establish chrome driver and go to report site URL
url = "https://clusterix.io/companies"


options = webdriver.ChromeOptions()
options.add_experimental_option('detach', True)
driver = webdriver.Chrome(options=options)
driver.get(url)

# Find the ‘Find’ button, then click it
driver.find_element(By.XPATH,"/html/body/div[5]//div/div/div[2]/div/div[2]/div/div[2]/div/div[1]/div/button[2]").click()
