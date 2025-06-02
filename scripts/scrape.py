import asyncio
from bs4 import BeautifulSoup
from urllib.parse import quote_plus
from playwright.async_api import async_playwright
from concurrent.futures import ThreadPoolExecutor
import time

async def get_company_urls_async(batch):
    """Get company URLs without loading HTML content - memory efficient"""
    batch = quote_plus(batch)
    listing_url = f'https://www.ycombinator.com/companies?batch={batch}'
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-dev-shm-usage']
        )
        
        try:
            page = await browser.new_page()
            await page.set_viewport_size({"width": 1920, "height": 1080})
            await page.set_extra_http_headers({
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            })
            
            await page.goto(listing_url, wait_until='networkidle', timeout=30000)

            try:
                dropdown_selector = "select, .w-full.rounded-md.border-gray-300"
                await page.wait_for_selector(dropdown_selector, timeout=10000)
                await page.select_option(dropdown_selector, value="YCCompany_By_Launch_Date_production")
                await page.wait_for_timeout(2000)
            except Exception as e:
                print(f"Dropdown select failed: {e}")

            # Scroll to load all companies
            prev_height = 0
            scroll_attempts = 0
            max_attempts = 20
            
            while scroll_attempts < max_attempts:
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                await page.wait_for_timeout(1500)
                
                curr_height = await page.evaluate("document.body.scrollHeight")
                if curr_height == prev_height:
                    break
                    
                prev_height = curr_height
                scroll_attempts += 1

            # Extract only URLs - don't load content yet
            company_urls = await page.evaluate('''
                () => {
                    const urls = new Set();
                    const links = document.querySelectorAll('a[href^="/companies/"]');
                    links.forEach(link => {
                        const href = link.getAttribute('href');
                        if (href && href.startsWith('/companies/') && !href.endsWith('/founders')) {
                            urls.add('https://www.ycombinator.com' + href);
                        }
                    });
                    return Array.from(urls);
                }
            ''')

        finally:
            await browser.close()

    print(f"Found {len(company_urls)} company URLs")
    return company_urls

async def process_company_batch(urls):
    """Process a small batch of company URLs and return HTML content"""
    html_contents = []
    semaphore = asyncio.Semaphore(3)  # Reduced concurrency for memory
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-dev-shm-usage']
        )
        
        try:
            async def fetch_company_page(url):
                async with semaphore:
                    try:
                        page = await browser.new_page()
                        await page.goto(url, wait_until='domcontentloaded', timeout=20000)
                        html = await page.content()
                        await page.close()
                        return html
                    except Exception as e:
                        print(f"Failed to load {url}: {e}")
                        return None

            tasks = [fetch_company_page(url) for url in urls]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            html_contents = [html for html in results if html and not isinstance(html, Exception)]
            
        finally:
            await browser.close()

    print(f"Loaded {len(html_contents)} pages for batch")
    return html_contents
