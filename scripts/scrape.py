import time
import urllib.parse
import requests

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from bs4 import BeautifulSoup

def get_links(batch):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")


    driver = webdriver.Chrome(options=chrome_options)

    # Navigate to the URL
    batch = urllib.parse.quote_plus(batch)
    driver.get(f'https://www.ycombinator.com/companies?batch={batch}')
    time.sleep(2)

    # Sort by launch date
    dropdown_selector = (".w-full.rounded-md.border-gray-300.pl-3.pr-10.pr-6.text-base."
                        "focus\\:border-indigo-500.focus\\:outline-none.focus\\:ring-indigo-500.sm\\:text-sm")
    select_element = driver.find_element(By.CSS_SELECTOR, dropdown_selector)
    dropdown = Select(select_element)
    dropdown.select_by_value("YCCompany_By_Launch_Date_production")

    time.sleep(2)

    # Initial scroll height
    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)
        
        # Calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height


    soup = BeautifulSoup(driver.page_source, 'html.parser')


    results_div = soup.find("div", class_="_section_i9oky_163 _results_i9oky_343")
    links = []
    if results_div:
        for a in results_div.find_all("a", href=True):
            route = str(a.get('href'))
            if route.startswith('/companies/'):
                url = "https://www.ycombinator.com" + route
                if url not in links:
                    links.append(requests.get(url).text)
                    break
    driver.quit()
    return links
