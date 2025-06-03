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
        # Initialize progress
        set_progress(0, 1, 0)
        print(f"Starting scrape for batch: {batch}")
        
        # Phase 1: Get company URLs (not HTML content)
        print("Phase 1: Getting company URLs...")
        company_urls = await get_company_urls_async(batch)
        
        if not company_urls:
            print("ERROR: No company URLs found!")
            set_progress(0, 1, 1)
            return False
            
        print(f"Found {len(company_urls)} company URLs")
        total_companies = len(company_urls)
        
        # Phase 2: Process companies in small batches to manage memory
        print("Phase 2: Processing companies in batches...")
        
        processed_count = 0
        error_count = 0
        all_companies_data = []
        
        try:
            # Extract information from this batch
            all_companies_data = extract_company_information(
                company_urls,
                lambda p, t, e: set_progress(processed_count + p, total_companies, error_count + e)
            )
            
            # Add to results
            processed_count += len(all_companies_data)
            
            
        except Exception as e:
            print(f"Error processing batch: {e}")
            error_count += len(all_companies_data)
            processed_count += len(all_companies_data)
        
        # Update progress
        set_progress(processed_count, total_companies, error_count)
        
        if not all_companies_data:
            print("ERROR: No company information extracted!")
            set_progress(total_companies, total_companies, total_companies)
            return False
            
        print(f"✓ Successfully extracted information for {len(all_companies_data)} companies")
        
        # Phase 3: Write to Google Sheets
        print("Phase 3: Writing data to Google Sheets...")
        write_to_google_sheet(all_companies_data)
        print("✓ Successfully wrote data to Google Sheets")
        
        # Final cleanup
        del all_companies_data
        gc.collect()
        
        set_progress(total_companies, total_companies, 0)
        print("🎉 Scraping completed successfully!")
        
        return True
        
    except Exception as e:
        print(f"❌ Scraping failed with error: {e}")
        print("Full traceback:")
        traceback.print_exc()
        
        set_progress(0, 1, 1)
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
        set_progress(0, 1, 1)
        return False