# import libraries
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
from selenium.webdriver.chrome.service import Service
import csv
from dateutil.relativedelta import *
from dateutil.easter import *
from dateutil.rrule import *
from dateutil.parser import *
from datetime import *
from difflib import SequenceMatcher
from myconfig import *
from bs4 import BeautifulSoup

import os
import openai

from dotenv import load_dotenv
from idlelib.query import Goto

# External files: Kriterienkatalog & Forbidden comments:
with open('KriterienV06.txt','r',encoding="utf8") as f:
    FirstInput = f.read()

csv_file_path = 'ForbiddenComments.csv'

with open(csv_file_path, 'r',encoding="utf8") as file:
    csv_reader = csv.reader(file)
    forbiddenComments = []
    for row in csv_reader:
        forbiddenComments.append(row)

# adjustments to keep window visible
service = Service()
options = webdriver.ChromeOptions()
options.add_experimental_option('detach', True)
options.add_argument("--start-maximized")
driver = webdriver.Chrome(service=service, options=options)

#Variabeln:
website = "https://clusterix.io/companies"
forbiddenTitle = "gGmbH"
forbiddenTitle2 = "gemeinnützig"
forbiddenTitle3 = "e.V."
forbiddenTitle4 = "Rente"
forbiddenTitle5 = "Kliniken"
forbiddenTitle6 = "Klinikum"

similarityRatio = 0.89


# Funktionen:
def get_difference(startdate, enddate):
    diff = enddate - startdate
    return diff.days 

def similar(a, b):
    return SequenceMatcher(None, a, b).ratio() 

# Erstellen von Auswertungsdatei mit ansteigender Zahl:
z = 0
while os.path.exists("Auswertung%s.txt" % z):
    z += 1

#Und Zooooom
driver.get('chrome://settings/appearance')
sleep(2)
driver.execute_script('chrome.settingsPrivate.setDefaultZoom(0.7);')
sleep(2)
driver.get(website)
sleep(10)
'''
#CookieFenster
shadow_parent = driver.find_element(By.CSS_SELECTOR, '#usercentrics-root')
outer = driver.execute_script('return arguments[0].shadowRoot', shadow_parent)
outer.find_element(By.CSS_SELECTOR, "button[data-testid='uc-accept-all-button']").click()
'''
#Kontoanmeldung
email = driver.find_element(By.NAME,"email")
email.send_keys(emailadresse)

password = driver.find_element(By.NAME,"password")
password.send_keys(passwort)

# Captcha solver
# solver = RecaptchaSolver(driver=driver)
'''
frame_ref = driver.find_elements(By.TAG_NAME,"iframe")[0]
iframe = driver.switch_to.frame(frame_ref)

robot = driver.find_element(By.XPATH, '//*[@id="recaptcha-anchor"]/div[1]')
robot.click()
#solver.click_recaptcha_v2(iframe=robot)
'''
sleep(5)

# Anmeldung:
driver.switch_to.parent_frame()

anmelden = driver.find_element(By.XPATH, '//*[@id="login-form"]/div[3]/div[3]/button')
anmelden.click()

sleep(10)

# Kampagne wählen

campaignNavigationBar = driver.find_element(By.CLASS_NAME,'campaigns-navigation-header__part')
campaignNavigationBar.click()
sleep(1)
chooseKampagne = driver.find_element(By.CLASS_NAME,'ca-pr-yellow')
chooseKampagne.send_keys(Keys.CONTROL, "a")
chooseKampagne.send_keys(Keys.DELETE)
chooseKampagne.send_keys(kampagneVon)
chooseKampagne.send_keys(Keys.ENTER)
sleep(2)


# Einstellung der Firmenkriterien
mitarbeiter = driver.find_element(By.XPATH, '//*[@id="main_content"]/div/div[1]/div/div[3]/div[5]/div[1]')
mitarbeiter.click()
sleep(1)

ma_size = driver.find_element(By.XPATH,'//*[@id="main_content"]/div/div[1]/div/div[3]/div[5]/div[2]/div/div/div/div[1]/input[1]')
ma_size.send_keys(maMin)

sleep(1)

max_size = driver.find_element(By.CSS_SELECTOR,'#main_content > div > div.NewCompanySearch_filters__Vtst8.NewCompanySearch_animated-part__5r31H > div > div.FiltersBar_filters__g\+caY > div:nth-child(5) > div.FilterItem_closable-box__zGgzT.FilterItem_open__tNqpL > div > div > div > div.ca_rangeslider_v2__inputs > input[type=text]:nth-child(3)')
max_size.send_keys(Keys.BACKSPACE)
max_size.send_keys(maMax)

# Wann wurde das letzte mal kommentiert:
#kommentare = driver.find_element(By.XPATH,'//*[@id="main_content"]/div/div[1]/div/div[3]/div[7]/div[1]')
#kommentare.click()

#sleep(1)

#vierzehnTage = driver.find_element(By.XPATH, '//*[@id="main_content"]/div/div[1]/div/div[3]/div[7]/div[2]/div/div/div[2]')
#vierzehnTage.click()
 
sleep(5)

pages = driver.find_elements(By.CLASS_NAME,'ca-whitespace-nowrap')
numberOfPages = pages[-1].text
actions = ActionChains(driver)

# loop over pages:
n = 1
while n <= int(numberOfPages):
    
    sleep(5)
    
    #identifiing comment and "add to campaign"- elements
    kommentarElements = driver.find_elements(By.CSS_SELECTOR,'div.CompanyBox_comments__NJXr\+.CompanyBox_part__RF7W2.CompanyBox_button__9y6iA')
    kampagnenElements = driver.find_elements(By.CLASS_NAME,'CompanyBox_campaign__2lYMS.CompanyBox_part__RF7W2')
    kampagnenElementsAvailableOrNot = []
    
    # array of "add to campaign elemenents" available or not:
    for y in kampagnenElements:
                html5 = y.get_attribute('innerHTML')
                soup5 = BeautifulSoup(html5, 'html.parser')
                div_text5class1 = soup5.find_all('div', {'class' : 'ca-text-theme ca-fill-theme hover:ca-bg-theme-10 hover:ca-text-theme hover:ca-fill-theme focus-visible:ca-outline ca-outline-offset-2 ca-outline-theme-dark active:ca-bg-theme-dark active:ca-text-white active:ca-fill-white ca-flex ca-items-center ca-justify-center ca-rounded ca-py-aqua ca-px-yellow hover:ca-cursor-pointer ca-w-fit'})
                div_text5class2 = soup5.find_all('div', {'class' : 'ca-text-grey-dark ca-fill-grey-dark CompanyBox_disabled__bgjoQ ca-flex ca-items-center ca-justify-center ca-rounded ca-py-aqua ca-px-yellow hover:ca-cursor-not-allowed ca-w-fit'})
                
                if (len(div_text5class1) == 0):
                    kampagnenElementsAvailableOrNot.append(div_text5class2[0])
                else:
                    kampagnenElementsAvailableOrNot.append(div_text5class1[0])
                    
                    
    # loop over companies with enough comments:
    for idx, x in enumerate(kommentarElements):
        
        tries = 1;
        
        # scroll to element
        actions.move_to_element(x).perform()
        
        html = x.get_attribute('innerHTML')
        soup = BeautifulSoup(html, 'html.parser')
        span_text = soup.find('span').text
        span_text = str(span_text)      
        
        numberList =[]
        # how many comments?
        for element in span_text:
            if element.isnumeric():
                numberList.append(element)
                numberFromSpanText = ''.join(numberList)
                numberFromSpanText = int(numberFromSpanText)
        
        if span_text == '-' or span_text == '':
            continue
        
        if '@' in span_text:
            numberFromSpanText = 10
            
        if numberFromSpanText < kommentarMin:
            continue
        
        # Clicks on a company
        if numberFromSpanText >= kommentarMin and kampagnenElementsAvailableOrNot[idx].get('class')[0] == "ca-text-theme":
            
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable(x)).click() 
            sleep(10)
            
            # if company name is invalid continue:
            title = driver.find_elements(By.XPATH, '//*[@id="main_content"]/div/div[4]/div[2]/div/div[1]/div[1]/div[1]/h3')
            if len(title) == 0:
                continue
            if forbiddenTitle in title[0].text or forbiddenTitle2 in title[0].text or forbiddenTitle3 in title[0].text or forbiddenTitle4 in title[0].text or forbiddenTitle5 in title[0].text or forbiddenTitle6 in title[0].text:
                driver.find_element(By.XPATH, '//*[@id="main_content"]/div/div[4]/div[2]/div/div[1]/div[1]/div[2]/div[2]/div[1]').click()
                sleep(1)
                continue
            
            globaleMutterTitle = driver.find_elements(By.CLASS_NAME,'tree__company-name')  
            if len(globaleMutterTitle) != 0:
                if forbiddenTitle in globaleMutterTitle[0].text:
                    driver.find_element(By.XPATH, '//*[@id="main_content"]/div/div[4]/div[2]/div/div[1]/div[1]/div[2]/div[2]/div[1]').click()
                    sleep(1)
                    continue
            
            # get website of company:
            websites = driver.find_elements(By.CLASS_NAME, 'website')
            if len(websites) != 0:
                website = driver.find_element(By.CLASS_NAME, 'website').text
            
            # get comments only from company or also from concern?:
            checkboxVisible = driver.find_element(By.XPATH,'//*[@id="main_content"]/div/div[4]/div[2]/div/div[2]/div[2]/div[1]/div[1]/div[2]')
            test = driver.find_element(By.XPATH,'//*[@id="main_content"]/div/div[4]/div[2]/div/div[2]/div[2]/div[1]/div[1]/div[2]/div/div/label')
            sleep(2)
            if test.get_attribute("class") == "ca-relative ca-flex ca-justify-center ca-items-center ca-overflow-hidden ca-appearance-none ca-m-0 ca-w-[var(--size)] ca-h-[var(--size)] ca-border ca-border-solid ca-rounded ca-bg-theme ca-border-theme group-hover:ca-border-theme-dark group-hover:ca-bg-theme-dark ca-box-border ca-gap-red ca-font-semibold ca-flex ca-items-center ca-m-0 ca-cursor-pointer":
                checkboxVisible.click()
                sleep(3)
                           
            # Mitarbeiteranzahl    
            maZahl = driver.find_element(By.CLASS_NAME,'number_of_employee').text
            
            # Token creation: Vertriebsmitarbeiter, firma im Verbund, Kommentar
            nameTokens = driver.find_elements(By.CLASS_NAME,'comment_comment__name__iUAMK')
            companyInGroupComplete = []
            commentsComplete = []
            companyInGroup = driver.find_elements(By.CLASS_NAME,'common-card-with-avatar_card-with-avatar__body__U0ol3.comment_comment__body__9HVG2')
            
            for y in companyInGroup:
                html2 = y.get_attribute('innerHTML')
                soup2 = BeautifulSoup(html2, 'html.parser')
                span_text2 = soup2.find_all('span', {'class' : 'comment_comment__info_badge_company__qGIy6'})
                div_text2 = soup2.find_all('div', {'class' : 'comment_comment__content__rB5+D'})
                
                if (len(span_text2) == 0):
                    companyInGroupComplete.append(title[0].text)
                else:
                    companyInGroupComplete.append(span_text2[0].text)
                    
                if (len(div_text2) == 0):
                    commentsComplete.append('Kommentar nicht lesbar')
                else:
                    commentsComplete.append(div_text2[0].text)
            
            # Token creation: Date   
            dateTokens = driver.find_elements(By.CLASS_NAME,'comment_comment__date__Gn93j')
            
            commentTokensComplete = []
            commentBlock = driver.find_elements(By.CSS_SELECTOR, 'div.comment_comment__content__rB5\+D')
            
            #Creation of 2D Matrix with strings
            matrix_2 = []
            
            # Creation of complete comment token:
            
            for idz, z in enumerate(nameTokens):
                commentBlock_Each = []
                commentBlock_Each.append(z.text)
                commentBlock_Each.append(dateTokens[idz].text)
                commentBlock_Each.append(companyInGroup[idz])
                commentBlock_Each.append(commentsComplete[idz])
                
                matrix_2.append(commentBlock_Each)
            
            # Current time definition    
            this_year = datetime.today().year
            
            nonoTrue = False
            # forbidden comments in comments (ignoring caps):
            for nonoComment in forbiddenComments:
                if nonoTrue:
                    break
                for comment in matrix_2:
                    timeStampClx = comment[1]
                    if len(timeStampClx) < 19:
                        timeStampClxInterpr = datetime.strptime(comment[1], '%d.%m. um %H:%M').replace(year=this_year)
                    else:
                        timeStampClxInterpr = datetime.strptime(comment[1], '%d.%m.%Y um %H:%M')
                    
                    #similarity = similar(str(nonoComment[0].lower()),str(commentBlock_Each[3].lower))
                    
                    timeDelta = datetime.today() - timeStampClxInterpr
                    if str(nonoComment[0].lower()) in str(comment[3].lower()) and timeDelta.days < maxDaySinceFatalComment:
                        driver.find_element(By.XPATH, '//*[@id="main_content"]/div/div[4]/div[2]/div/div[1]/div[1]/div[2]/div[2]/div[1]').click()
                        sleep(1)
                        nonoTrue = True
                        break
                    
            if nonoTrue:
                break
            #Creation of 1D Matrix with strings
            ContentInputArray = []
            ContentInput = ""
            ContentInputSingleString = ""
            for idw, w in enumerate(nameTokens):
                
                ContentInput = ContentInput + "\n" + "Vertriebler: " + w.text + "\n" + "Datum: " + dateTokens[idw].text + "\n" + "Firma: " + companyInGroupComplete[idw] + "\n" + commentsComplete[idw] + "\n"
                ContentInputSingleString = "\n" + "Vertriebler: " + w.text + "\n" + "Datum: " + dateTokens[idw].text + "\n" + "Firma: " + companyInGroupComplete[idw] + "\n" + commentsComplete[idw] + "\n"
                ContentInputArray.append(ContentInputSingleString)
            
            # saving the comment data to a file 
            f = open("Kommentare.txt", "a", encoding='utf-8')
            f.write("\n" + title[0].text + ": \n" + ContentInput)
            f.close()
            
        
            # Chat GPT input:                                          
            Intro = "Hallo ChatGpt! Ich habe eine Aufgabe für dich. Bitte bewerte folgendes Unternehmen: \n"
            UDaten = title[0].text + "(" + maZahl + ') \n'
            ChatWebsite = 'Website:' + website + '\n'
            ContentInput50 = ContentInputArray[-AnzahlKommentare:]
            ContentInput50String = ' '.join(ContentInput50)        
            ChatGPTInput = Intro + UDaten + ChatWebsite + FirstInput + "Kommentare der Vertriebsmitarbeiter (max. die letzten 20): " + ContentInput50String
            
            load_dotenv()
            openai.api_key = ApiKey
            
            while True:
                
                try:
                    
                    completion = openai.ChatCompletion.create(model="gpt-4", messages=[{"role": "user", "content": ChatGPTInput}])
        
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
            
            print("ChatGPT-Antwort: " + completion.choices[0].message.content)
            
            
            fileNumber = 0
            f = open("Auswertung%s.txt" % fileNumber, "a")
            f.write(title[0].text + ": "+ completion.choices[0].message.content + "\n")
            f.close()
            
            # getting the evaluation from chatGPT (only Number):
            chatGPTOutput = completion.choices[0].message.content
            rating_als_liste = chatGPTOutput.split(' ')
            
            for i in rating_als_liste:
                if i.isdigit():
                    rating = i
            
            print(title[0].text)
            print(completion.choices[0].message.content)
            print('Extrahierte Bewertung: ' + rating)
            try:    
                if int(rating) >= ratingMinimum:
                #if rating == "JA":
                    driver.find_element(By.XPATH,'//*[@id="main_content"]/div/div[4]/div[2]/div/div[1]/div[1]/div[1]/div').click()
                    sleep(3)
            except ValueError as ve:
                print("Fehlerhafte Analyse: " + title[0].text)
            
            # close company window
            driver.find_element(By.XPATH, '//*[@id="main_content"]/div/div[4]/div[2]/div/div[1]/div[1]/div[2]/div[2]/div[1]').click()
            
            sleep(1)

    # go to nex page:
    pageSelector = driver.find_elements(By.CLASS_NAME,'ca_paginationbar_page-selector')
    pageSelector[-1].click()
    sleep(10)
    n+=1


print("All done, Sir.")