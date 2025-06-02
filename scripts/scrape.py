
from bs4 import BeautifulSoup
from urllib.parse import quote_plus
from playwright.sync_api import sync_playwright

def get_links(batch, progress_callback=None):
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
        progress_callback(0, len(company_urls), 0)
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
