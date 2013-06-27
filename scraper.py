from bs4 import BeautifulSoup
from urllib2 import urlopen
import gspread
import sys
import scrapers

# IMPORTANT: Set these to your Google acct username and password
GOOGLE_USER = "username"
GOOGLE_PW = "password"

def post_listings(listings):
    google = gspread.login(GOOGLE_USER, GOOGLE_PW)
    spread = google.open("Snatched Apartments").sheet1

    # Retrieve listings already in the spreadsheet, and use these to
    # filter current <listings> to prevent duplicates. We consider two
    # listings different from each other if their links don't match
    cur_listings = spread.col_values(2)
    listings = [l for l in listings if l[1] not in cur_listings]

    if len(listings) > 0:
        plural = "listing" if len(listings) == 1 else "listings"
        print "Found %d new %s!"%(len(listings), plural)
    else:
        print "No new listings were found."
        return

    print "Posting results to Google Drive... this may take awhile"

    # Start at row 2, so we can keep the title row
    # Note that rows/columns are indexed starting at 1
    for row, listing in enumerate(listings, len(cur_listings)+1):
        for col, datum in enumerate(listing, 1):
            spread.update_cell(row, col, datum)
        
if __name__ == '__main__':
    scrape_funcs = [f for f in dir(scrapers) if f.startswith('scrape_')]
    listings = [getattr(scrapers,scrape_func)() for scrape_func in scrape_funcs]

    print listings
#    post_listings(listings)
