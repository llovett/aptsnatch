from bs4 import BeautifulSoup
from urllib2 import urlopen
import sys

def scrape_craigslist():
    '''Craigslist scraper'''

    # Root URL (scraped href's will be appended to this to form absolute URLs)
    ROOT_URL = "http://sfbay.craigslist.org"

    # URLs to scrape
    URLS = (
        "/search/apa/sfc?zoomToPosting=&query=potrero+hill&srchType=A&minAsk=&maxAsk=4000&bedrooms=2",
    )

    results = []

    sys.stdout.write("Scraping craigslist...")
    for url in URLS:
        sys.stdout.write(".")
        page = urlopen(ROOT_URL + url).read()
        soup = BeautifulSoup(page)
        
        listings = soup.find_all('p', class_='row')
        
        for listing in listings:
            link = listing.find(class_="pl").a
            href = ROOT_URL + link.get("href")
            title = link.string
            try:
                price = listing.find(class_='price').string
            except AttributeError:
                price = "could not find price"
            date = listing.find(class_='date').string
            lat = listing.get("data-latitude")
            lng = listing.get("data-longitude")
            maps_link = "https://maps.google.com/maps?q=%s+%s"%(lat,lng) if lat and lng else "could not find location"

            results.append((title,href,price,date,maps_link))

    return results
