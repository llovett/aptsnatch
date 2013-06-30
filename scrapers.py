# -*- coding: utf-8
from bs4 import BeautifulSoup
from urllib2 import urlopen
import sys, re

# *** Set the search criteria ***
MAX_PRICE = 4200
# Must have this many bedrooms-
MIN_BDRM = 2
# -OR have at least this square footage
MIN_SQFT = 1000
# Search term
KEYWORD = "potrero hill"

# Regexps
SQFT_REGEXP = re.compile("[0-9]+ft", flags=re.MULTILINE)
BDRM_REGEXP = re.compile("[0-9]+br", flags=re.MULTILINE)

def scrape_craigslist():
    '''Craigslist scraper'''

    # Root URL (scraped href's will be appended to this to form absolute URLs)
    root_url = "http://sfbay.craigslist.org"

    # URL to scrape
    search_url = "/search/apa/sfc?zoomToPosting=&query=%s&srchType=A&minAsk=&maxAsk=%d&bedrooms=%d"%(
        '+'.join(KEYWORD.split()),
        MAX_PRICE,
        MIN_BDRM
    )
    sys.stdout.write("Scraping craigslist...")
    sys.stdout.write(".")
    page = urlopen(root_url + search_url).read()
    soup = BeautifulSoup(page)

    listings = soup.find_all('p', class_='row')

    results = []
    for listing in listings:
        link = listing.find(class_="pl").a
        href = root_url + link.get("href")
        title = link.string
        try:
            price = listing.find(class_='price').string
        except AttributeError:
            price = "could not find price"
        # Find square footage and bedroom count
        try:
            sqft = bdrm = None
            details = listing.find(class_='pnr')
            for s in details.strings:
                if not sqft:
                    sqft = re.search(SQFT_REGEXP, s)
                if not bdrm:
                    bdrm = re.search(BDRM_REGEXP, s)
        except AttributeError:
            pass
        # Check for fewer than minimum bedrooms, or unspecified
        if not bdrm or int(bdrm.group(0)[:-2]) < MIN_BDRM:
            # Check square-footage
            if sqft:
                # Filter out matches that have too little square footage
                if int(sqft.group(0)[:-2]) < MIN_SQFT:
                    continue
            else:
                # Too few details or does not meet specs
                continue
        bdrm = bdrm.group(0)[:-2] if bdrm else "could not find bedroom count"
        sqft = sqft.group(0)[:-2] if sqft else "could not find sqft count"
        date = listing.find(class_='date').string
        lat = listing.get("data-latitude")
        lng = listing.get("data-longitude")
        maps_link = "https://maps.google.com/maps?q=%s+%s"%(lat,lng) if lat and lng else "could not find location"

        results.append((title,href,price,date,maps_link,bdrm,sqft))

    return results

if __name__ == '__main__':
    '''for debugging'''
    print scrape_craigslist()
