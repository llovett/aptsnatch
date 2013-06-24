apartmentsnatcher
=================

Scraper that automatically scrapes apartment listings for appropriate apartments and notifies user of new listings

## Features to Include
- Scrape craigslist and perhaps other websites for apartment listings
- Save information about apartments in database or file somewhere
- Automatically notify user if a new listing appears that matches some set of criteria
- Be able to e-mail landlord from the app

## How to setup
1. Create a virtual environment with `virtualenv` and source the `activate` script:

        $ virtualenv aptsnatch_env
        $ cd aptsnatch_env
        $ source bin/activate

2. Install packages listed in `requirements.txt`:

        $ cd aptsnatch
        $ pip install -r requirements.txt

3. Add your searches from Craigslist to the URLS tuple at the top of scraper.py, your Google username & password to the GOOGLE_USERNAME and GOOGLE_PASSWORD variables

4. Run the scraper:

       $ python scraper.py
