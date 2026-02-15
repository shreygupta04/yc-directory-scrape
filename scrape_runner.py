import asyncio
import traceback
import gc

from scripts.scrape import get_company_urls_async
from scripts.extract import extract_company_information
from scripts.write import write_to_google_sheet
from scripts.progress import set_progress, add_log


async def run_scrape_async(batch):
    try:
        set_progress(0, 1, 0, phase="discovering", phase_detail="Loading YC directory...")
        add_log(f"Starting scrape for batch: {batch}")
        print(f"Starting scrape for batch: {batch}")

        company_urls = await get_company_urls_async(batch)

        if not company_urls:
            print("ERROR: No company URLs found!")
            set_progress(0, 1, 1, phase="error", phase_detail="No companies found for this batch")
            add_log("No company URLs found. Check the batch name and try again.")
            return False

        total_companies = len(company_urls)
        add_log(f"Found {total_companies} companies to process")
        print(f"Found {total_companies} company URLs")

        set_progress(0, total_companies, 0, phase="extracting", phase_detail="Extracting company data...")
        add_log("Starting data extraction via AI...")

        processed_count = 0
        error_count = 0
        all_companies_data = []

        try:
            def extraction_callback(p, t, e):
                set_progress(p, total_companies, e, phase="extracting",
                             phase_detail=f"Extracting company {p} of {total_companies}...")

            all_companies_data = extract_company_information(
                company_urls,
                extraction_callback,
            )
            processed_count += len(all_companies_data)

        except Exception as e:
            print(f"Error processing batch: {e}")
            error_count += len(all_companies_data)
            processed_count += len(all_companies_data)

        set_progress(processed_count, total_companies, error_count, phase="extracting")

        if not all_companies_data:
            print("ERROR: No company information extracted!")
            set_progress(total_companies, total_companies, total_companies,
                         phase="error", phase_detail="Extraction failed for all companies")
            add_log("Extraction failed — no data was returned.")
            return False

        add_log(f"Extracted data for {len(all_companies_data)} companies")
        print(f"Successfully extracted information for {len(all_companies_data)} companies")

        set_progress(processed_count, total_companies, error_count,
                     phase="writing", phase_detail="Writing data to Google Sheets...")
        add_log("Writing results to Google Sheets...")
        print("Phase 3: Writing data to Google Sheets...")

        write_to_google_sheet(all_companies_data)
        print("Successfully wrote data to Google Sheets")
        add_log("Google Sheets updated successfully")

        del all_companies_data
        gc.collect()

        set_progress(total_companies, total_companies, error_count,
                     phase="completed", phase_detail="All done!")
        add_log("Scraping completed successfully!")
        print("Scraping completed successfully!")

        return True

    except Exception as e:
        print(f"Scraping failed with error: {e}")
        print("Full traceback:")
        traceback.print_exc()
        set_progress(0, 1, 1, phase="error", phase_detail=str(e))
        add_log(f"Error: {e}")
        return False


def run_scrape(batch):
    try:
        print(f"Starting scrape runner for batch: {batch}")
        result = asyncio.run(run_scrape_async(batch))
        print(f"Scrape runner completed. Success: {result}")
        return result
    except Exception as e:
        print(f"Error in sync wrapper: {e}")
        traceback.print_exc()
        set_progress(0, 1, 1, phase="error", phase_detail=str(e))
        add_log(f"Fatal error: {e}")
        return False
