# -*- coding: utf-8
from bs4 import BeautifulSoup
from urllib2 import urlopen, quote, unquote
import sys, re, datetime

# *** General search options ***
MAX_SCRAPED_PAGES = 10

# *** Set the search criteria ***
MAX_PRICE = 5000
# Must have this many bedrooms-
MIN_BDRM = 1
# -OR have at least this square footage
MIN_SQFT = 800
# Search terms
KEYWORDS = ("potrero hill", "dogpatch",)

# Regexps
SQFT_REGEXP = re.compile("[0-9]+ft", flags=re.MULTILINE)
TRULIA_SQFT_REGEXP = re.compile("[0-9]+ sqft", flags=re.MULTILINE)
BDRM_REGEXP = re.compile("[0-9]+br", flags=re.MULTILINE)
TRULIA_BDRM_REGEXP = re.compile("[0-9]+bd", flags=re.MULTILINE)
TCODE_REGEXP = re.compile("{{(.*)}}", flags=re.MULTILINE)
CL_ES_REGEXP = re.compile("subject=(.*?)&")
CL_ER_REGEXP = re.compile("(mailto:(.*?)\?)|(mailto:(.*))")

def scrape_craigslist():
    '''Craigslist scraper'''

    # Root URL (scraped href's will be appended to this to form absolute URLs)
    root_url = "http://sfbay.craigslist.org"

    sys.stdout.write("Scraping craigslist...")
    results = []
    for keyword in KEYWORDS:
        # URL to scrape
        search_url = "/search/apa/sfc?zoomToPosting=&query=%s&srchType=A&minAsk=&maxAsk=%d&bedrooms=%d"%(
            '+'.join(keyword.split()),
            MAX_PRICE,
            MIN_BDRM
        )
        page = urlopen(root_url + search_url).read()
        soup = BeautifulSoup(page)

        listings = soup.find_all('p', class_='row')

        for listing in listings:
            sys.stdout.write(".")
            sys.stdout.flush()
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

            ##############################
            # Scrape reply-to email and construct a new mailto link with given template
            lpage = urlopen(href).read()
            lsoup = BeautifulSoup(lpage)

            # Craigslist doesn't seem to be consistent with displaying the reply-to link,
            # so this is the best I could come up with
            email = lsoup.find(lambda x:x.has_attr("href") and x.get("href").startswith("mailto"))
            if email:
                email = email.get("href")
                email_subj = re.search(CL_ES_REGEXP, email)
                if email_subj:
                    email_subj = "Interest in your apartment: %s"%unquote(email_subj.group(1)).strip()
                else:
                    email_subj = "Interested in your apt, as listed on Craigslist"
                email_rcpt = re.search(CL_ER_REGEXP, email)
                email_rcpt = email_rcpt.group(2) or email_rcpt.group(4)

                # Evaluate python code in the template surrounded by {{ }}'s
                # This way, we can fill in blanks in the template that reference var names
                with open("email_template.txt","r") as template:
                    replacements = {}
                    contents = template.read()
                    for item in re.finditer(TCODE_REGEXP, contents):
                        replacements[item.group(1)] = eval(item.group(1))
                    newstring = None
                    for orig, new in replacements.iteritems():
                        newstring = (newstring or contents).replace('{{%s}}'%orig, str(new))

                # Set new mailto link
                mailto = "mailto:%s?subject=%s&body=%s"%(
                    email_rcpt,
                    quote(email_subj),
                    quote(newstring)
                )
            else:
                mailto = "no email address?"

            results.append((title,href,price,date,maps_link,bdrm,sqft,mailto))

    print
    return results

def scrape_trulia():
    root_url = "http://www.trulia.com"
    search_url = "/for_rent/1453_nh/%dp_beds/0-%d_price/date;d_sort/"%(
        MIN_BDRM,
        MAX_PRICE
    )

    sys.stdout.write("Scraping trulio...")
    page = urlopen(root_url + search_url).read()
    soup = BeautifulSoup(page)

    listings = soup.find_all('li', class_='property-data-elem')

    results = []
    for listing in listings:
        sys.stdout.write(".")
        sys.stdout.flush()
        link = listing.find(class_='h4').a
        href = root_url + link.get("href")
        title = link.strong.string.strip()
        pricediv = listing.find(class_='lastCol')
        price = pricediv.strong.string
        price = re.search('\d,\d\d\d', price).group()
        sqft = re.search(TRULIA_SQFT_REGEXP, str(pricediv))
        sqft = sqft.group() if sqft else "could not find sqft count"
        bdrm = re.search(TRULIA_BDRM_REGEXP, title).group()
        address = listing.find('p', class_='man').a.get("alt")
        # Never lists the date, so use today (date scraped)
        date = datetime.datetime.now().strftime("%m/%d/%Y")

        results.append((title,href,price,date,address,bdrm,sqft))

    print
    return results


if __name__ == '__main__':
    '''for debugging'''
    print scrape_craigslist()
    #print scrape_trulia()
