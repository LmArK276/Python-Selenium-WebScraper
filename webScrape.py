#conda install -c conda-forge selenium
#conda install -c conda-forge webdriver-manager
#pip intall srtools

import sys

try:
    sys.stdout.reconfigure(encoding='utf-8')
except AttributeError:
    pass

from selenium import webdriver 
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
    
options = Options()
options.add_argument("--headless")

browser = webdriver.Chrome(options=options) 
browser.implicitly_wait(1)

def getSchoolScore(link, schoolName):
    print("SKOLA:",schoolName)
    browser.get(link)
    
    tables = browser.find_elements(By.TAG_NAME, 'table')

    try:
        table2019 = tables[1].find_element(By.TAG_NAME, 'tbody')
    except IndexError:
        browser.get("https://srednjeskole.edukacija.rs/drzavne-srednje-skole/svi-gradovi")
        return -1
    
    rows = table2019.find_elements(By.TAG_NAME, 'tr')
    rows.pop(0) #skini header
   
    sum = 0
    iter = 0 

    for row in rows:
        try:
            td3 = row.find_element(By.XPATH, ".//td[3]//strong")
        except NoSuchElementException:
            td3 = row.find_element(By.XPATH, ".//td[3]")
            
        td3Val = td3.get_attribute("textContent").strip("&nbsp")
        try:
            minPoints = float(td3Val)
        except ValueError:
            print("INVALID VALUE FOR SCHOOL",schoolName)
            print("Invalid value:", td3Val)
            continue
        
        sum = sum + minPoints
        iter = iter + 1
        
    
    
    if(iter != 0 ):
        browser.get("https://srednjeskole.edukacija.rs/drzavne-srednje-skole/svi-gradovi")
        return sum / iter
    else:
        #probaj da sidjes u tableu za 2018
        try:
            table2019 = tables[2].find_element(By.TAG_NAME, 'tbody')
        except IndexError:
            browser.get("https://srednjeskole.edukacija.rs/drzavne-srednje-skole/svi-gradovi")
            return -1
        
        rows = table2019.find_elements(By.TAG_NAME, 'tr')
        rows.pop(0) #skini header        
        
        for row in rows:
            try:
                td3 = row.find_element(By.XPATH, ".//td[3]//strong")
            except NoSuchElementException:
                td3 = row.find_element(By.XPATH, ".//td[3]")
                
            td3Val = td3.get_attribute("textContent").strip("&nbsp")
            try:
                minPoints = float(td3Val)
            except ValueError:
                print("INVALID VALUE FOR SCHOOL",schoolName)
                print("Invalid value:", td3Val)
                continue
        
            sum = sum + minPoints
            iter = iter + 1
        
        #give up
        if(iter == 0):
            browser.get("https://srednjeskole.edukacija.rs/drzavne-srednje-skole/svi-gradovi")
            return -1    
        
        browser.get("https://srednjeskole.edukacija.rs/drzavne-srednje-skole/svi-gradovi")
        return sum / iter
    
    
        
        

browser.get("https://srednjeskole.edukacija.rs/drzavne-srednje-skole/svi-gradovi")

elements = browser.find_elements(By.CLASS_NAME, 'accordion')

allSchools = []

for index, nazivGrada in enumerate(elements):
    try:
        links = nazivGrada.find_elements(By.XPATH, ".//li//a")
        
    except StaleElementReferenceException:
        # Handle the exception by re-locating the elements
        try:
            nazivGrada = browser.find_elements(By.CLASS_NAME, 'accordion')[index]
        except IndexError:
            continue
        links = nazivGrada.find_elements(By.XPATH, ".//li//a")

    for index2, link in enumerate(links):
        try:
            link_url = link.get_attribute("href")
        except StaleElementReferenceException:
            nazivGrada = browser.find_elements(By.CLASS_NAME, 'accordion')[index]
            link = nazivGrada.find_elements(By.XPATH, ".//li//a")[index2]
            link_url = link.get_attribute("href")
            
        try:    
            schoolName = link.find_element(By.TAG_NAME, "strong").get_attribute("textContent")
        except NoSuchElementException:
            schoolName = link.get_attribute("textContent")
            
        schoolCity = nazivGrada.find_element(By.XPATH, "./div/a").text
        schoolScore = getSchoolScore(link_url, schoolName)

        allSchools.append((schoolName, schoolCity, schoolScore))

       
import pandas as pd

from srtools import latin_to_cyrillic

df = pd.DataFrame(allSchools, columns =['Naziv', 'Grad', 'Score'])
df['Naziv'] = df['Naziv'].apply( lambda x : latin_to_cyrillic(x))
df['Grad'] = df['Grad'].apply( lambda x : latin_to_cyrillic(x))

df.to_excel("schoolsScored.xlsx")
