# import time
# import urllib.parse
# import requests

# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.support.ui import Select, WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.common.exceptions import StaleElementReferenceException

# from bs4 import BeautifulSoup

# def get_links(batch):
#     chrome_options = Options()
#     chrome_options.add_argument("--headless")
#     chrome_options.add_argument("--no-sandbox")
#     chrome_options.add_argument("--disable-dev-shm-usage")
#     chrome_options.add_argument("--disable-gpu")
#     chrome_options.add_argument("--window-size=1920x1080")



#     driver = webdriver.Chrome(options=chrome_options)

#     # Navigate to the URL
#     batch = urllib.parse.quote_plus(batch)
#     driver.get(f'https://www.ycombinator.com/companies?batch={batch}')

#     # Sort by launch date
#     dropdown_selector = (".w-full.rounded-md.border-gray-300.pl-3.pr-10.pr-6.text-base."
#                         "focus\\:border-indigo-500.focus\\:outline-none.focus\\:ring-indigo-500.sm\\:text-sm")
    
#     wait = WebDriverWait(driver, 10)
#     for _ in range(3):
#         try:
#             # Wait for element to be present again
#             select_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, dropdown_selector)))
#             dropdown = Select(select_element)
#             dropdown.select_by_value("YCCompany_By_Launch_Date_production")
#             break  # success
#         except StaleElementReferenceException:
#             continue  # retry if DOM shifted

#     time.sleep(2)

#     # Initial scroll height
#     last_height = driver.execute_script("return document.body.scrollHeight")

#     while True:
        
#         driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
#         time.sleep(1)
        
#         # Calculate new scroll height and compare with last scroll height
#         new_height = driver.execute_script("return document.body.scrollHeight")
#         if new_height == last_height:
#             break
#         last_height = new_height


#     soup = BeautifulSoup(driver.page_source, 'html.parser')


#     results_div = soup.find("div", class_="_section_i9oky_163 _results_i9oky_343")
#     links = []
#     if results_div:
#         for a in results_div.find_all("a", href=True):
#             route = str(a.get('href'))
#             if route.startswith('/companies/'):
#                 url = "https://www.ycombinator.com" + route
#                 if url not in links:
#                     links.append(requests.get(url).text)
#                     break
#     driver.quit()
#     return links

from bs4 import BeautifulSoup
from urllib.parse import quote_plus
from playwright.sync_api import sync_playwright

def get_links(batch: str):
    batch = quote_plus(batch)
    listing_url = f'https://www.ycombinator.com/companies?batch={batch}'
    html_contents = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(listing_url, wait_until='networkidle')

        # Try selecting "By Launch Date" if dropdown is stable
        try:
            dropdown_selector = (
                ".w-full.rounded-md.border-gray-300.pl-3.pr-10.pr-6.text-base."
                "focus\\:border-indigo-500.focus\\:outline-none.focus\\:ring-indigo-500.sm\\:text-sm"
            )
            page.wait_for_selector(dropdown_selector, timeout=5000)
            page.select_option(dropdown_selector, value="YCCompany_By_Launch_Date_production")
            page.wait_for_timeout(2000)
        except Exception as e:
            print("Dropdown select failed:", e)

        # Scroll to load all company cards
        prev_height = 0
        while True:
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            page.wait_for_timeout(1000)
            curr_height = page.evaluate("document.body.scrollHeight")
            if curr_height == prev_height:
                break
            prev_height = curr_height

        # Extract links
        soup = BeautifulSoup(page.content(), "html.parser")
        results_div = soup.find("div", class_="_section_i9oky_163 _results_i9oky_343")
        company_urls = []

        if results_div:
            for a in results_div.find_all("a", href=True):
                route = str(a.get("href"))
                if route.startswith("/companies/"):
                    full_url = "https://www.ycombinator.com" + route
                    if full_url not in company_urls:
                        company_urls.append(full_url)

        # Fetch each company page HTML
        for url in company_urls:
            try:
                page.goto(url, wait_until='networkidle')
                html = page.content()
                html_contents.append(html)
            except Exception as e:
                print(f"Failed to load {url}: {e}")
                continue

        browser.close()

    return html_contents
