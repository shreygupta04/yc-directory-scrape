from scripts.scrape import get_links
from scripts.extract import extract_company_information
from scripts.write import write_to_google_sheet
from scripts.progress import set_progress

def run_scrape(batch):
    set_progress(0, 1, 0)  # Init

    def progress_callback(p, t, e):
        set_progress(p, t, e)

    links = get_links(batch, progress_callback)

    data = extract_company_information(links, progress_callback)
    write_to_google_sheet(data)
    return True
