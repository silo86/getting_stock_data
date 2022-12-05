#importing required packages
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
from datetime import datetime
current_date = datetime.now().date().strftime('%Y-%m-%d')

#adding options on chrome
chromeOptions = Options()

tickers = ['F','CMCSA','AAPL', 'ORCL', 'XRX', 'WOR', 'WSM', 'JNJ', 'WCC', 'MMM']
class Scrapper:
    def get_climate_change_score(self,tickers:list,url:str)->list:
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--user-agent="Mozilla/5.0 (Windows Phone 10.0; Android 4.2.1; Microsoft; Lumia 640 XL LTE) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Mobile Safari/537.36 Edge/12.10166"')
        chrome_options.add_argument('headless')
        driver = webdriver.Chrome(chrome_options=chrome_options)
        #driver.get('https://www.google.com/finance/')
        driver.get(url)
        climate_list = []
        for i,ticker in enumerate(tickers):
            if i == 0:
                search_box = driver.find_element('xpath','/html/body/c-wiz/div/div[3]/div[3]/div/div/div/div[1]/input[2]')
            else:
                search_box = driver.find_element('xpath','//*[@id="gb"]/div[2]/div[2]/div/form/div/div/span/div/div/div/div[1]/input[2]')
                #the following button clear the search box to enter a new ticker
                button = driver.find_element('xpath','//body[@id="yDmH0d"]//button[@class="gb_uf gb_wf"]')
                button.click()
            search_box.send_keys(ticker)
            search_box.send_keys(Keys.RETURN)
            time.sleep(2)
            elements = driver.find_elements(By.CLASS_NAME,'P6K39c')
            elements = [element.text for element in elements]
            while('' in elements):
                elements.remove('')
            climate_score = elements[8]
            climate_dict = {'ticker': ticker,
                            'date': current_date,
                            'climate_change_score': climate_score
                            }
            climate_list.append(climate_dict)
        return climate_list