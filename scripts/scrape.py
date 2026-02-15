from urllib.parse import quote_plus
from playwright.async_api import async_playwright

from scripts.progress import set_progress, add_log


async def get_company_urls_async(batch):
    batch = quote_plus(batch)
    listing_url = f'https://www.ycombinator.com/companies?batch={batch}'

    set_progress(0, 1, 0, phase="discovering", phase_detail="Launching browser...")
    add_log("Launching headless browser...")

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

            set_progress(0, 1, 0, phase="discovering", phase_detail="Loading YC directory page...")
            add_log(f"Navigating to {listing_url}")
            await page.goto(listing_url, wait_until='networkidle', timeout=30000)

            try:
                dropdown_selector = "select, .w-full.rounded-md.border-gray-300"
                await page.wait_for_selector(dropdown_selector, timeout=10000)
                await page.select_option(dropdown_selector, value="YCCompany_By_Launch_Date_production")
                await page.wait_for_timeout(2000)
            except Exception as e:
                print(f"Dropdown select failed: {e}")

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

                current_count = await page.evaluate('''
                    () => {
                        const links = document.querySelectorAll('a[href^="/companies/"]');
                        const urls = new Set();
                        links.forEach(link => {
                            const href = link.getAttribute('href');
                            if (href && href.startsWith('/companies/') && !href.endsWith('/founders')) {
                                urls.add(href);
                            }
                        });
                        return urls.size;
                    }
                ''')
                set_progress(0, 1, 0, phase="discovering",
                             phase_detail=f"Scrolling page... {current_count} companies found so far")
                add_log(f"Scroll {scroll_attempts}/{max_attempts} — {current_count} companies visible")

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
    set_progress(0, 1, 0, phase="discovering",
                 phase_detail=f"Found {len(company_urls)} companies!")
    add_log(f"Directory scan complete — {len(company_urls)} company URLs collected")
    return company_urls
