import time
from bs4 import BeautifulSoup
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from tqdm import tqdm

ids = [10, 17, 205, 52, 200, 4, 204, 60, 53, 48, 214, 38, 11, 62, 335, 22, 9, 47, 209, 63, 124, 23, 106, 59, 50, 193,
       73, 3, 24, 375, 8, 34]
driver = webdriver.Chrome()

links = []
titles = []
topics = []
dates = []
for i in tqdm(range(len(ids))):
    driver.get(
        f"https://cbr.ru/na/?la.Search=&la.TagId={ids[i]}&la.VidId=&la.Date.Time=Custom&la.Date.DateFrom=12.2014&la.Date.DateTo=03.2024")
    time.sleep(2)
    while True:
        try:
            driver.find_element(By.ID, 'la_load').click()
            time.sleep(0.1)
        except Exception:

            html = driver.page_source
            soup = BeautifulSoup(html, 'html.parser')
            topic = soup.find('button', 'filter_title')
            topic = topic.get_text()

            for link in soup.find_all('div', 'title'):
                # print(link)
                links.append(link.find('a').get('href'))
                titles.append(link.find('a').get('data-zoom-title'))
                topics.append(topic)


            for date in soup.find_all('span', 'date col-md-2'):
                dates.append(date.get_text())
            break
    #break

    # driver.find_element(By.ID, 'la_load').click()
    # elements = driver.find_elements(By.CLASS_NAME, 'filter-select_option')
    # elements = driver.find_elements(By.NAME, 'la_TagId')

    # print(elements[1])
df = pd.DataFrame(data={'title': titles, 'url': links, 'topic': topics, 'date': dates})
print(df.head())

df.to_csv('law_acts.csv', index=False)
driver.quit()
