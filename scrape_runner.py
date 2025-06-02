import asyncio
import traceback

from scripts.scrape import get_links_async
from scripts.extract import extract_company_information
from scripts.write import write_to_google_sheet
from scripts.progress import set_progress

async def run_scrape_async(batch):
    """Async main function with better error handling and monitoring"""
    
    try:
        # Initialize progress
        set_progress(0, 1, 0)
        print(f"Starting scrape for batch: {batch}")
        
        # Phase 1: Get HTML content from company pages
        print("Phase 1: Scraping company pages...")
        
        def scrape_progress_callback(processed, total, errors):
            # During scraping phase, this represents the full progress
            set_progress(processed, total, errors)
            print(f"Scraping progress: {processed}/{total} (errors: {errors})")
        
        html_contents = await get_links_async(batch, scrape_progress_callback)
        
        if not html_contents:
            print("ERROR: No company pages found!")
            set_progress(0, 1, 1)
            return False
            
        print(f"✓ Successfully scraped {len(html_contents)} company pages")
        
        # Phase 2: Extract company information using AI
        print("Phase 2: Extracting company information with AI...")
        
        def extract_progress_callback(processed, total, errors):
            # For extraction phase, we need to adjust the total to account for both phases
            # Assume scraping was first half, extraction is second half
            total_work = len(html_contents) * 2  # scraping + extraction
            current_progress = len(html_contents) + processed  # scraping done + current extraction
            set_progress(current_progress, total_work, errors)
            print(f"Extraction progress: {processed}/{total} (errors: {errors})")
        
        companies_data = extract_company_information(html_contents, extract_progress_callback)
        
        if not companies_data:
            print("ERROR: No company information extracted!")
            set_progress(len(html_contents), len(html_contents) * 2, len(html_contents))
            return False
            
        print(f"✓ Successfully extracted information for {len(companies_data)} companies")
        
        # Phase 3: Write to Google Sheets
        print("Phase 3: Writing data to Google Sheets...")
        write_to_google_sheet(companies_data)
        print("✓ Successfully wrote data to Google Sheets")
        
        # Mark as completed - all phases done
        total_work = len(html_contents) * 2
        set_progress(total_work, total_work, 0)
        print("🎉 Scraping completed successfully!")
        
        return True
        
    except Exception as e:
        print(f"❌ Scraping failed with error: {e}")
        print("Full traceback:")
        traceback.print_exc()
        
        # Set error state
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