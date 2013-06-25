from bs4 import BeautifulSoup
from urllib2 import urlopen
import gspread
import sys

# IMPORTANT: Set these to your Google acct username and password
GOOGLE_USER = "username"
GOOGLE_PW = "password"

# Root URL (scraped href's will be appended to this to form absolute URLs)
ROOT_URL = "http://sfbay.craigslist.org"

# URLs to scrape
URLS = (
    "/search/apa/sfc?zoomToPosting=&query=potrero+hill&srchType=A&minAsk=&maxAsk=4000&bedrooms=2",
)

def parse_listing(row):
    link = row.find(class_="pl").a
    href = ROOT_URL + link.get("href")
    title = link.string
    try:
        price = row.find(class_='price').string
    except AttributeError:
        price = "could not find price"
    date = row.find(class_='date').string
    lat = row.get("data-latitude")
    lng = row.get("data-longitude")
    maps_link = "https://maps.google.com/maps?q=%s+%s"%(lat,lng) if lat and lng else "could not find location"
    return title, href, price, date, maps_link

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
    results = []

    sys.stdout.write("Scraping craigslist...")
    for url in URLS:
        sys.stdout.write(".")
        page = urlopen(ROOT_URL + url).read()
        soup = BeautifulSoup(page)
        
        listings = soup.find_all('p', class_='row')
        
        for listing in listings:
            results.append(parse_listing(listing))
    print 
    post_listings(results)
