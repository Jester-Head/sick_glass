import os
from time import sleep
from random import randint
import spacy
from better_profanity import profanity
import pandas as pd
import undetected_chromedriver.v2 as uc
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import ElementNotInteractableException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

def create_chrome_driver():
    options = uc.ChromeOptions()

    # setting profile
    options.add_argument('--user-data-dir=c:\\temp\\profile')
    
    # Change browser options
    options.add_argument('proxy-server = 106.122.8.54:3128')
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.5249 Safari/537.36')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--start-maximized')
    
    # options passing in to skip popups
    options.add_argument('--no-first-run --no-service-autorun --password-store=basic')
    driver = uc.Chrome(options=options)
    
    return driver




def file_exists(filename,headers):
    filename = 'data\\'+ filename +'.csv'
    # Create file if doesn't exist
    if not os.path.exists(filename):
        with open(filename, 'w',encoding='utf-8') as f:
            f.writelines(headers)
    # Add headers if file exists without headers
    else:
        with open (filename,'r+',encoding='utf-8') as f:
            if str(f.readline())=='':
                f.writelines(headers)
    return filename
    
    
def extract_insult_names(driver,url,insult_type,selector,button,count):
    insult = []
    with driver:
        driver.get(url)
        sleep(randint(1,5))
        for i in range(count):
            driver.find_element(By.CSS_SELECTOR,button).click()
            sleep(2)
            # Checks if page updated and waits to append if not
            if((i-1) == (driver.find_element(By.CSS_SELECTOR,selector).text)):
                sleep(5)
                insult.append(driver.find_element(By.CSS_SELECTOR,selector).text)
            else:
                insult.append(driver.find_element(By.CSS_SELECTOR,selector).text)
    df = pd.DataFrame(insult,columns=['insult'])
    df['type'] = insult_type
    df['link'] = url
    return df


def save_data(data,filename):
    data.to_csv(filename,mode='a',index=False,header=False,encoding='utf-8')

def clean_data(df):
    df.drop_duplicates(inplace=True)
    df['insult'] = [i.lower() for i in df['insult']]
    df['insult']=df['insult'].apply(lambda x: x.replace('0','o'))
    df['insult']=df['insult'].apply(lambda x: x.replace('5','s'))
    df['insult']=df['insult'].apply(lambda x: x.replace('1','i'))
    df['insult']=df['insult'].apply(lambda x: x.replace('3','e'))
    df['insult']=df['insult']=df['insult'].apply(lambda x: x.replace('**','uc'))
    df['insult']=df['insult']=df['insult'].apply(lambda x: x.replace('*','i'))
    df['insult']=df['insult']=df['insult'].apply(lambda x: x.replace('slvt','slut'))
    df['insult']=df['insult']=df['insult'].apply(lambda x: x.replace('!',''))
    df['insult']=df['insult']=df['insult'].apply(lambda x: x.replace('you',''))
    df['insult']=df['insult']=df['insult'].apply(lambda x: x.replace('thou',''))
    df['insult']=df['insult'].str.strip()
    return df
    
def nsfw_check(df):
    profanity.load_censor_words(whitelist_words=['fart','jerk','poop','vulgar','turd','scum','tampon','crap','stupid'])
    profanity_insults = df[df['insult'].apply(profanity.contains_profanity)]
    return profanity_insults
def main():

    driver = create_chrome_driver()
    headers = ['insult,','category,','link\n']
    file = file_exists('insult_names',headers)
    
    robie_robot_names = 'http://robietherobot.com/insult-generator.htm'
    button = 'tr:nth-child(1) td:nth-child(2) form:nth-child(4) center:nth-child(6) > input:nth-child(1)'
    selector = 'center td h1'
    insult_type = 'nsfw'
    count = 100
    df1 = extract_insult_names(driver=driver,url=robie_robot_names,insult_type=insult_type,selector=selector,button=button,count=count)
    
    rust_names = 'https://rusttips.com/insult-generator/'
    selector ='.wpb_content_element .wpb_wrapper h2'
    button = '.bklyn-btn-normal'
    insult_type = 'nsfw'
    count = 300
    df2 = extract_insult_names(driver=driver,url=rust_names,insult_type=insult_type,selector=selector,button=button,count=count)
    
    kids = 'https://fungenerators.com/random/insult/childish/'
    button = '.btn-home'
    selector='h2'
    insult_type = 'kid_friendly'
    count = 100
    
    df3 = extract_insult_names(driver=driver,url=kids,insult_type=insult_type,selector=selector,button=button,count=count)
    
        
    shakespeare = 'https://fungenerators.com/random/insult/shakespeare/'
    button = '.btn-home'
    selector='h2'
    insult_type = 'shakespeare'
    count = 50
    df4 = extract_insult_names(driver=driver,url=shakespeare,insult_type=insult_type,selector=selector,button=button,count=count)
    
    medieval_insult='https://fungenerators.com/random/insult/medieval-insult/'
    button = '.btn-home'
    selector='h2'
    insult_type = 'medieval'
    count = 50
    
    df5 = extract_insult_names(driver=driver,url=medieval_insult,insult_type=insult_type,selector=selector,button=button,count=count)
    
    
    df = pd.concat([df1,df2,df3,df4,df5], ignore_index=True, sort=False)
    df = clean_data(df)
    
    
    
    save_data(data = df,filename=file)
    driver.quit()
    

if __name__ == "__main__":
    main()
    