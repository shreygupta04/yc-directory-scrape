import asyncio
import traceback
import gc  # Garbage collection

from scripts.scrape import get_company_urls_async
from scripts.extract import extract_company_information
from scripts.write import write_to_google_sheet
from scripts.progress import set_progress

async def run_scrape_async(batch):
    """Memory-optimized async main function"""
    
    try:
        set_progress(0, 1, 0, phase="discovering_urls", phase_detail="Scrolling YC directory to find companies...")
        print(f"Starting scrape for batch: {batch}")
        
        company_urls = await get_company_urls_async(batch)
        
        if not company_urls:
            print("ERROR: No company URLs found!")
            set_progress(0, 1, 1, phase="error", phase_detail="No company URLs found for this batch.")
            return False
            
        print(f"Found {len(company_urls)} company URLs")
        total_companies = len(company_urls)
        
        set_progress(0, total_companies, 0, phase="extracting_data", phase_detail=f"Extracting data for {total_companies} companies...")
        print("Phase 2: Processing companies in batches...")
        
        processed_count = 0
        error_count = 0
        all_companies_data = []
        
        try:
            all_companies_data = extract_company_information(
                company_urls,
                lambda p, t, e: set_progress(p, total_companies, e, phase="extracting_data", phase_detail=f"Extracting company {p}/{total_companies}...")
            )
            
            processed_count += len(all_companies_data)
            
            
        except Exception as e:
            print(f"Error processing batch: {e}")
            error_count += len(all_companies_data)
            processed_count += len(all_companies_data)
        
        set_progress(processed_count, total_companies, error_count, phase="extracting_data", phase_detail="Extraction complete.")
        
        if not all_companies_data:
            print("ERROR: No company information extracted!")
            set_progress(total_companies, total_companies, total_companies, phase="error", phase_detail="No company information could be extracted.")
            return False
            
        print(f"Successfully extracted information for {len(all_companies_data)} companies")
        
        set_progress(processed_count, total_companies, error_count, phase="writing_sheets", phase_detail="Writing data to Google Sheets...")
        print("Phase 3: Writing data to Google Sheets...")
        write_to_google_sheet(all_companies_data)
        print("Successfully wrote data to Google Sheets")
        
        del all_companies_data
        gc.collect()
        
        set_progress(total_companies, total_companies, 0, phase="completed", phase_detail="All data scraped and saved to the spreadsheet.")
        print("Scraping completed successfully!")
        
        return True
        
    except Exception as e:
        print(f"Scraping failed with error: {e}")
        print("Full traceback:")
        traceback.print_exc()
        
        set_progress(0, 1, 1, phase="error", phase_detail=f"Scraping failed: {str(e)}")
        return False

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
        set_progress(0, 1, 1, phase="error", phase_detail=f"Scraping failed: {str(e)}")
        return False
