from selenium import webdriver
from time import sleep
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.remote.webelement import WebElement
from selenium_recaptcha_solver import RecaptchaSolver
from selenium.webdriver.chrome.service import Service
import csv
from dateutil.relativedelta import *
from dateutil.easter import *
from dateutil.rrule import *
from dateutil.parser import *
from datetime import *
from difflib import SequenceMatcher

from bs4 import BeautifulSoup

import os
import openai

from dotenv import load_dotenv
from idlelib.query import Goto

with open('KriterienV06.txt','r',encoding="utf8") as f:
    FirstInput = f.read()

csv_file_path = 'ForbiddenComments.csv'

with open(csv_file_path, 'r',encoding="utf8") as file:
    csv_reader = csv.reader(file)
    forbiddenComments = []
    for row in csv_reader:
        forbiddenComments.append(row)

            
#Creation of 2D Matrix with strings
commentBlock_Each = []
matrix_2 = []
            
testArray1 = ["blablabla", "Machen es bereits"]
          
for x in enumerate(testArray1):
    
    commentBlock_Each.append(x)
    
    matrix_2.append(commentBlock_Each)
    
this_year = datetime.today().year

for nonoComment in forbiddenComments:
    for comment in matrix_2:
        for commentData in commentBlock_Each:
            timeStampClx = commentBlock_Each[1]
            if len(timeStampClx) < 19:
                timeStampClxInterpr = datetime.strptime(commentBlock_Each[1], '%d.%m. um %H:%M').replace(year=this_year)
            else:
                timeStampClxInterpr = datetime.strptime(commentBlock_Each[1], '%d.%m.%Y um %H:%M')
            
            similarity = similar(str(nonoComment[0].lower()),str(commentBlock_Each[3].lower))
            if str(nonoComment[0].lower()) in str(commentBlock_Each[3].lower) and datetime.today() - timeStampClxInterpr < maxDaySinceFatalComment:
                driver.find_element(By.XPATH, '//*[@id="main_content"]/div/div[4]/div[2]/div/div[1]/div[1]/div[2]/div[2]/div[1]').click()
                sleep(1)
                continue