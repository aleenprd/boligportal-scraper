# BoligPortal Scraper

## How to use 
You can use the `main.py` script to go to a seach page, with whatever filters you want applied. E.g.: I want all apartments in Copenhagen, whose rent is below 15000kr per month and have at least 3 rooms. Subsequently, the script will proceed to scrape all lings to all ads and create a list of links to parse. In the next step, it visits each ad and extracts the information we want. It also does some processing such as translating the summaries from Danish to English using the code in `goog_trans`. Then, you can save your results to a CSV file. There are a few parameters which need to be set in the `scraper_config.json` file which should be present in the `config` folder. In order to directly use the Python filter on the scraper data, use the script in `filter.py`, with the configuration options in `filter_config.py`, found, again, in the `config` folder.

## Dependencies 
The code makes use of google_trans_new, which was cloned from their Github, into the folder `goog_trans` because it still has some errors. The code needed to be modified as [per this answer](https://stackoverflow.com/questions/68214591/python-google-trans-new-translate-raises-error-jsondecodeerror-extra-data) on StackOverflow i.e. change line 151 in `google_trans_new.py`. Additionally, the scraper makes use of BeautifulSoup. Disclaimer: have problems with venv and freeze on Windows, so my requirements.txt was empty, and couldn't manage to troubleshoot it. Sorry for the missing file though. :) 