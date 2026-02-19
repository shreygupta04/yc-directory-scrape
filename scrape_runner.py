import asyncio
import traceback
import gc  # Garbage collection

from scripts.extract import extract_company_information
from scripts.progress import add_error_detail, add_recent_item, set_phase, set_progress
from scripts.scrape import get_company_urls_async
from scripts.write import write_to_google_sheet

async def run_scrape_async(batch):
    """Memory-optimized async main function"""
    
    try:
        set_progress(0, 1, 0, phase=1, phase_name="discovering_urls", phase_message="Initializing...")
        print(f"Starting scrape for batch: {batch}")

        set_phase(1, "discovering_urls", "Searching YC directory...")
        company_urls = await get_company_urls_async(batch, progress_callback=_url_discovery_callback)

        if not company_urls:
            print("ERROR: No company URLs found!")
            set_progress(0, 1, 1, status="failed", phase=1, phase_name="discovering_urls", phase_message="No companies found")
            add_error_detail("No company URLs found for this batch")
            return False

        print(f"Found {len(company_urls)} company URLs")
        total_companies = len(company_urls)

        set_progress(0, total_companies, 0, phase=2, phase_name="extracting_data", phase_message="Starting extraction...")
        set_phase(2, "extracting_data", f"Extracting data from {total_companies} companies...")

        processed_count = 0
        error_count = 0
        all_companies_data = []

        def extraction_callback(p, t, e):
            nonlocal processed_count, error_count
            processed_count = p
            error_count = e
            company_num = min(p, t)
            set_progress(p, t, e, phase=2, phase_name="extracting_data", phase_message=f"Processing company {company_num}/{t}...")

        try:
            all_companies_data = extract_company_information(
                company_urls,
                extraction_callback
            )
            processed_count = len(all_companies_data)
        except Exception as e:
            print(f"Error processing batch: {e}")
            add_error_detail(f"Batch processing error: {str(e)[:100]}")
            error_count += len(all_companies_data)
            processed_count += len(all_companies_data)

        set_progress(processed_count, total_companies, error_count, phase=2, phase_name="extracting_data", phase_message="Extraction complete")

        if not all_companies_data:
            print("ERROR: No company information extracted!")
            set_progress(total_companies, total_companies, total_companies, status="failed", phase=2, phase_name="extracting_data", phase_message="No data extracted")
            add_error_detail("No company information could be extracted")
            return False

        print(f"Successfully extracted information for {len(all_companies_data)} companies")

        set_phase(3, "writing_sheets", "Writing data to Google Sheets...")
        set_progress(processed_count, total_companies, error_count, phase=3, phase_name="writing_sheets", phase_message="Saving to spreadsheet...")
        write_to_google_sheet(all_companies_data)
        print("Successfully wrote data to Google Sheets")

        del all_companies_data
        gc.collect()

        set_progress(total_companies, total_companies, error_count, status="completed", phase=3, phase_name="writing_sheets", phase_message="Done!")
        print("Scraping completed successfully!")

        return True

    except Exception as e:
        print(f"Scraping failed with error: {e}")
        print("Full traceback:")
        traceback.print_exc()
        add_error_detail(f"Fatal error: {str(e)[:100]}")
        set_progress(0, 1, 1, status="failed", phase_message="Scraping failed")
        return False


def _url_discovery_callback(scroll_attempt, max_attempts):
    set_phase(1, "discovering_urls", f"Scrolling directory ({scroll_attempt}/{max_attempts})...")
    set_progress(0, 1, 0, status="running", phase=1, phase_name="discovering_urls", phase_message=f"Scrolling directory ({scroll_attempt}/{max_attempts})...")

def run_scrape(batch):
    """Sync wrapper for async function"""
    try:
        print(f"Starting scrape runner for batch: {batch}")
        result = asyncio.run(run_scrape_async(batch))
        print(f"Scrape runner completed. Success: {result}")
        return result
    except Exception as e:
        print(f"Error in sync wrapper: {e}")
        traceback.print_exc()
        set_progress(0, 1, 1)
        return False
