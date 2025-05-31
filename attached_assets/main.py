import sys

from scrape import get_links
from extract import extract_company_information
from write import write_to_google_sheet


batch = sys.argv[1]
scraped_links = get_links(batch)
extracted_data = extract_company_information(scraped_links)
write_to_google_sheet(extracted_data)