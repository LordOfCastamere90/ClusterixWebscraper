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

from bs4 import BeautifulSoup

import os
import openai

from dotenv import load_dotenv
from idlelib.query import Goto

with open('KriterienV03.txt','r',encoding="utf8") as f:
    FirstInput = f.read()


#DRIVER_PATH = "C:\Program Files\Google\ChromeDriver\chromedriver.exe"

options = webdriver.ChromeOptions()
options.add_experimental_option('detach', True)
options.add_argument("--start-maximized")
driver = webdriver.Chrome(options=options)

solver = RecaptchaSolver(driver=driver)

#Variabeln:
website = "https://clusterix.io/companies"
emailadresse = "schnittger@innoscripta.com"
passwort = "ehz6afn"
maMin = '1701'
maMax = '1899'
kommentarMin = 5
forbiddenTitle = "gGmbH"
forbiddenTitle2 = "gemeinnützig"
AnzahlKommentare = 50
ApiKey = "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"

i = 0
while os.path.exists("Auswertung%s.txt" % i):
    i += 1

#Und Zooooom
driver.get('chrome://settings/appearance')
sleep(2)
driver.execute_script('chrome.settingsPrivate.setDefaultZoom(0.9);')
sleep(2)
driver.get(website)
sleep(20)

#WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.XPATH,"//*[@id='uc-center-container']/div[2]/div/div[1]/div/div/button[2]"))).click()

shadow_parent = driver.find_element(By.CSS_SELECTOR, '#usercentrics-root')
outer = driver.execute_script('return arguments[0].shadowRoot', shadow_parent)
outer.find_element(By.CSS_SELECTOR, "button[data-testid='uc-accept-all-button']").click()

email = driver.find_element(By.NAME,"email")
email.send_keys(emailadresse)

password = driver.find_element(By.NAME,"password")
password.send_keys(passwort)
'''
frame_ref = driver.find_elements(By.TAG_NAME,"iframe")[0]
iframe = driver.switch_to.frame(frame_ref)

robot = driver.find_element(By.XPATH, '//*[@id="recaptcha-anchor"]/div[1]')
robot.click()
#solver.click_recaptcha_v2(iframe=robot)
'''
sleep(5)

driver.switch_to.parent_frame()

anmelden = driver.find_element(By.XPATH, '//*[@id="root"]/div/div/div/div[5]/div/button')
anmelden.click()

sleep(15)

mitarbeiter = driver.find_element(By.XPATH, '//*[@id="main_content"]/div/div[1]/div/div[3]/div[5]/div[1]')
mitarbeiter.click()

sleep(1)

ma_size = driver.find_element(By.XPATH,'//*[@id="main_content"]/div/div[1]/div/div[3]/div[5]/div[2]/div/div/div/div[1]/input[1]')
ma_size.send_keys(maMin)

max_size = driver.find_element(By.CSS_SELECTOR,'#main_content > div > div.NewCompanySearch_filters__3-AZx.NewCompanySearch_animated-part__3tNLs > div > div.FiltersBar_filters__Ag5i6 > div:nth-child(5) > div.ca-h-auto.ca-origin-top-left.ca-ease-in-out.ca-duration-300.ca-hidden.ca-scale-y-0 > div > div > div > div.ca_rangeslider_v2__inputs > input[type=text]:nth-child(3)')
max_size.send_keys(Keys.BACKSPACE)
max_size.send_keys(maMax)


kommentare = driver.find_element(By.XPATH,'//*[@id="main_content"]/div/div[1]/div/div[3]/div[7]/div[1]')
kommentare.click()

sleep(1)

vierzehnTage = driver.find_element(By.XPATH, '//*[@id="main_content"]/div/div[1]/div/div[3]/div[7]/div[2]/div/div/div[2]')
vierzehnTage.click()
 
sleep(30)


pages = driver.find_elements(By.CLASS_NAME,'ca-whitespace-nowrap')
numberOfPages = pages[-1].text
actions = ActionChains(driver)

print (numberOfPages)

n = 1
while n <= int(numberOfPages):
    
    #input ('Enter to continue...') 
    sleep(5)
    
    kommentarElements = driver.find_elements(By.CLASS_NAME,'CompanyBox_comments__FGxdx.CompanyBox_part__27YQc.CompanyBox_button__1n4E5')
    kampagnenElements = driver.find_elements(By.CSS_SELECTOR, ".ca-text-theme.ca-fill-theme.hover\:ca-bg-theme-10.hover\:ca-text-theme.hover\:ca-fill-theme.focus-visible\:ca-outline.ca-outline-offset-2.ca-outline-theme-dark.active\:ca-bg-theme-dark.active\:ca-text-white.active\:ca-fill-white.ca-flex.ca-items-center.ca-justify-center.ca-rounded.ca-py-aqua.ca-px-yellow.hover\:ca-cursor-pointer.ca-w-fit, .ca-text-grey-dark.ca-fill-grey-dark.CompanyBox_disabled__2ewk5.ca-flex.ca-items-center.ca-justify-center.ca-rounded.ca-py-aqua.ca-px-yellow.hover\:ca-cursor-not-allowed.ca-w-fit")
 
    for idx, x in enumerate(kommentarElements):
        
        tries = 1;
        
        actions.move_to_element(x).perform()
        
        html = x.get_attribute('innerHTML')
        soup = BeautifulSoup(html, 'html.parser')
        span_text = soup.find('span').text
        
        if span_text == '-' or span_text == '' or "@" in span_text:
            continue
        
        if span_text == '99+':
            span_text = '99'
            
        if int(span_text) < kommentarMin:
            continue
        
        # Clicks on a company
        if int(span_text) >= kommentarMin and kampagnenElements[idx].get_attribute("class") == "ca-text-theme ca-fill-theme hover:ca-bg-theme-10 hover:ca-text-theme hover:ca-fill-theme focus-visible:ca-outline ca-outline-offset-2 ca-outline-theme-dark active:ca-bg-theme-dark active:ca-text-white active:ca-fill-white ca-flex ca-items-center ca-justify-center ca-rounded ca-py-aqua ca-px-yellow hover:ca-cursor-pointer ca-w-fit":
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable(x)).click()
            #input ('Enter to continue...') 
            sleep(10)
            
            title = driver.find_element(By.XPATH, '//*[@id="main_content"]/div/div[4]/div[2]/div/div[1]/div[1]/div[1]/h3')
            if forbiddenTitle in title.text or forbiddenTitle2 in title.text:
                driver.find_element(By.CLASS_NAME, 'ca_button.content-panel_content-panel__header__close-button__ZsuHV.size3.variant3.hasicon').click()
                sleep(1)
                continue
            
            globaleMutterTitle = driver.find_elements(By.CLASS_NAME,'tree__company-name')  
            if len(globaleMutterTitle) != 0:
                if forbiddenTitle in globaleMutterTitle[0].text:
                    driver.find_element(By.CLASS_NAME, 'ca_button.content-panel_content-panel__header__close-button__ZsuHV.size3.variant3.hasicon').click()
                    sleep(1)
                    continue
            
            websites = driver.find_elements(By.CLASS_NAME, 'website')
            if len(websites) != 0:
                website = driver.find_element(By.CLASS_NAME, 'website').text
            
            checkboxVisible = driver.find_element(By.XPATH,'//*[@id="main_content"]/div/div[4]/div[2]/div/div[2]/div[2]/div[1]/div[1]/div[2]')
            test = driver.find_element(By.XPATH,'//*[@id="main_content"]/div/div[4]/div[2]/div/div[2]/div[2]/div[1]/div[1]/div[2]/div/div/label')
            
            if test.get_attribute("class") == "ca-relative ca-flex ca-justify-center ca-items-center ca-overflow-hidden ca-appearance-none ca-m-0 ca-w-[var(--size)] ca-h-[var(--size)] ca-border ca-border-solid ca-rounded ca-bg-theme ca-border-theme group-hover:ca-border-theme-dark group-hover:ca-bg-theme-dark ca-box-border ca-gap-red ca-font-semibold ca-flex ca-items-center ca-m-0 ca-cursor-pointer":
                #clicking several times because of bug
                sleep(20)
                checkboxVisible.click() 
                sleep(3)
            else:
                sleep(20)
                
            
            companyInGroupComplete = []
            maZahl = driver.find_element(By.CLASS_NAME,'number_of_employee').text
                
            nameTokens = driver.find_elements(By.CLASS_NAME,'comment_comment__name__2ROAL')
            companyInGroup = driver.find_elements(By.CLASS_NAME,'comment_comment__header__3iTZo')
            for x in companyInGroup:
                html2 = x.get_attribute('innerHTML')
                soup2 = BeautifulSoup(html2, 'html.parser')
                span_text2 = soup2.find_all('span', {'class' : 'comment_comment__info_badge_company__lZ6r-'})
                
                if (len(span_text2) == 0):
                    companyInGroupComplete.append(title.text)
                else:
                    companyInGroupComplete.append(span_text2[0].text)
            
                
            dateTokens = driver.find_elements(By.CLASS_NAME,'comment_comment__date__3xJTk')
            commentTokens = driver.find_elements(By.CLASS_NAME,'comment_comment__content__2BFjV')
            
            
            
            ContentInput = ""
            
            for idx, x in enumerate(nameTokens):
                ContentInput = ContentInput + "\n" + "Vertriebsmitarbeiter: " + x.text + "\n" + "Datum: " + dateTokens[idx].text + "\n" + "Unternehmen innerhalb des Konzerns: " + companyInGroupComplete[idx] + "\n" + commentTokens[idx].text + "\n"
            
            print (ContentInput)
              
            #print("\n" + title.text + ": \n" + ContentInput)
            f = open("Kommentare.txt", "a", encoding='utf-8')
            f.write("\n" + title.text + ": \n" + ContentInput)
            f.close()
            
        
                                                       
            Intro = "Hallo ChatGpt! Ich habe eine Aufgabe für dich. Bitte bewerte folgendes Unternehmen: \n"
            UDaten = title.text + "(" + maZahl + ') \n'
            ChatWebsite = 'Website:' + website + '\n'
            ContentInput50 = "Kommentare der Vertriebsmitarbeiter: " + ContentInput[-AnzahlKommentare:]
            
            load_dotenv()
    
            openai.api_key = ApiKey
            
            while True:
                
                try:
                    
                    completion = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=[{"role": "user", "content": Intro + UDaten + ChatWebsite + FirstInput + ContentInput50}])
        
                except openai.error.RateLimitError as e:
                # Handle the rate limit error
                    print("Rate limit exceeded. Please wait and try again later.")
                    print("Error message:", e)
                    if tries == 10:
                        break
                    sleep(5+tries^2)
                    tries+=1
                    continue
                    
                except openai.error.OpenAIError as e:
                # Handle other OpenAI API errors
                    print("An error occurred with the OpenAI API.")
                    print("Error message:", e)
                    if tries == 10:
                        break
                    sleep(300)
                    tries+=1
                    continue
                
                break
            
            print(title.text)
            print(completion.choices[0].message.content)
            
                
            f = open("Auswertung%s.txt" % i, "a")
            f.write(title.text + ": "+ completion.choices[0].message.content + "\n")
            f.close()
            
            rating = completion.choices[0].message.content.split(',')[0]
            
            try:    
                if int(rating) >= 60:
                    driver.find_element(By.XPATH,'//*[@id="main_content"]/div/div[4]/div[2]/div/div[1]/div[1]/div[1]/div').click()
                    sleep(3)
            except ValueError as ve:
                print("Fehlerhafte Analyse: " + title.text)
            
            
            driver.find_element(By.CLASS_NAME, 'ca_button.content-panel_content-panel__header__close-button__ZsuHV.size3.variant3.hasicon').click()
            sleep(1)
    
    # Close button
    #closeWindowOption = driver.find_elements(By.XPATH,'//*[@id="main_content"]/div/div[4]/div[2]/div/div[1]/div[1]/div[2]/div[2]/div[1]')
    
    pageSelector = driver.find_elements(By.CLASS_NAME,'ca_paginationbar_page-selector')
    pageSelector[-1].click()
    sleep(30)
    n+=1


print("All done, Sir.")
