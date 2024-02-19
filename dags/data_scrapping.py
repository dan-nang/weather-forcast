import requests
from bs4 import BeautifulSoup
import pandas as pd
from selenium import webdriver
import time

from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

url = "https://www.tiket.com/pesawat/search?d=BDJ&a=CGK&date=2024-04-15&adult=1&child=0&infant=0&class=economy&dType=AIRPORT&aType=AIRPORT&dLabel=Banjarmasin&aLabel=Jakarta&type=depart&flexiFare=true"

page = requests.get(url)

options = webdriver.ChromeOptions()
# options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

# Use ChromeDriverManager to automatically download and manage the appropriate ChromeDriver
driver_manager = ChromeDriverManager()
driver_path = driver_manager.install()
service = Service(driver_path)  # Initialize the Service with the ChromeDriver path
driver = webdriver.Chrome(service=service, options=options)  # Pass the Service instance

driver.get(url)
time.sleep(1)

# data = BeautifulSoup(driver.page_source, 'lxml')
# driver.execute_script("arguments[0].click()", driver.find_element(By.XPATH, "/html/body/div[1]/main/div[3]/section/div/div/div[1]/div/div/div[2]/div/div[3]/div/span[1]"))
# time.sleep(5)

# declare list variable
price_list = []
maskapai_list = []
depature_list = []
arrival_list = []

# get HTML of the page
data = BeautifulSoup(driver.page_source, 'html.parser')

# looping to get all card in the page
for area in data.find_all('div', {'class': 'VirtualizedFlightList_card__SNNpv'}):
    try:
        # get maskapai 
        maskapai = area.find(class_="Text_text__DSnue Text_size_b2__y3Q2E Text_weight_bold__m4BAY").text.strip()    
        # get price 
        price = area.find(class_="Text_text__DSnue Text_variant_alert__7jMF3 Text_size_h3__qFeEO Text_weight_bold__m4BAY").text.strip()
        # get depature time 
        depature = area.find(class_="FlightCard_schedule_time__HSyGO").find_next('span').text.strip()
        # get arrival time
        arrival = area.find_all('div', class_='FlightCard_time__ssfW4')[-1].find('span', class_='Text_text__DSnue Text_size_h3__qFeEO Text_weight_bold__m4BAY').text.strip()

    except:
         continue
    # store data to the list
    maskapai_list.append(maskapai)
    price_list.append(price)
    depature_list.append(depature)
    arrival_list.append(arrival)

to_dict = {"price":price_list,
           "maskapai":maskapai_list,
           "depature":depature_list,
           "arrival":arrival_list
           }
df_hasil = pd.DataFrame.from_dict(to_dict, orient='index')
df_transform = df_hasil.T
print(df_transform)
try:
    df_transform.to_csv('Flight_list.csv')
    print("success")
except:
    print("gagal")