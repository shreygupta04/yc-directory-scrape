from api.scrape import get_links
from api.extract import extract_company_information
from api.write import write_to_google_sheet
from api.progress import set_progress

def run_scrape(batch):
    set_progress(0, 1, 0)  # Init

    links = get_links(batch)
    set_progress(0, len(links), 0)

    def progress_callback(p, t, e):
        set_progress(p, t, e)

    data = extract_company_information(links, progress_callback)
    write_to_google_sheet(data)
    return True
