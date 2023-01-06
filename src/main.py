"""main.py"""


import argparse
import csv
import sys

from dependencies.general import *
from dependencies.scraper import *
from dependencies.filter import *


parser = argparse.ArgumentParser()

parser.add_argument(
    "--mode",
    type=str,
    required=True,
    help="Tells application if it should scrape or filter",
    default="scrape",
)

parser.add_argument(
    "--scraper_config",
    type=str,
    required=False,
    help="Tells application where to look for scraping configuration",
    default="../config/scraper_config.json",
)

parser.add_argument(
    "--filter_config",
    type=str,
    required=False,
    help="Tells application where to look for filtering configuration",
    default="../config/filter_config.json",
)


@timing
def main(args) -> None:
    """Main method to either scrape or filter scraped data."""

    if args.mode == "scrape":
        scraper_config_options = load_configuration_file(args.scraper_config)
        
        if scraper_config_options is False:
            print(
                "\nMissing, empty or wrongly named scraping config file. \
                Program will terminate."
            )
            sys.exit()
        else:
            print("\nFetching scraping options from configuration file: ")
            print("# -------------------------------------- #")
            for option in scraper_config_options.keys():
                print(f"\t* {option}: {scraper_config_options[option]}")
            print()
            main_url = scraper_config_options["MAIN_URL"]
            results_pages = scraper_config_options["RESULTS_PAGES"]
            scraper_output_path = scraper_config_options["OUTPUT_PATH"]
            
            # Scrape main page for URL list to parse
            # -------------------------------------- #
            urls_list = scrape_ads_urls(main_url, results_pages)

            # Iterate thorugh all the ads
            # -------------------------------------- #
            ads_list = []

            i = 1
            for url in tqdm(urls_list):
                print(f"No. {i}: {url}")
                ad = scrape_ad(url)
                ads_list.append(ad)
                i += 1

            # Can't save datetime properly. Make strings
            for ad in ads_list:
                creation_date = ad["creation_date"]
                ad["creation_date"] = creation_date.strftime("%m/%d/%Y")

                scraped_date = ad["scraped_date"]
                ad["scraped_date"] = scraped_date.strftime("%m/%d/%Y")

                available_from = ad["available_from"]
                ad["available_from"] = available_from.strftime("%m/%d/%Y")

            keys = ads_list[0].keys()

            # Save the output to a CSV file. You can view it in Excel later
            # -------------------------------------- #
            with open(scraper_output_path, "w", newline="", encoding="utf-8") as output_file:
                dict_writer = csv.DictWriter(output_file, keys)
                dict_writer.writeheader()
                dict_writer.writerows(ads_list)
    
    elif args.mode == "filter":
        filter_config_options = load_configuration_file(args.filter_config)
        
        if filter_config_options is False:
            print("\nMissing, empty or wrongly named filter config file. \
                Program will terminate.")
        else:
            print("\nFetching filter options from configuration file: ")
            print("# -------------------------------------- #")
            for option in filter_config_options.keys():
                print(f"\t* {option}: {filter_config_options[option]}")
            print()
        
            # FILTER and save to XLSX file
            # -------------------------------------- #
            filtered_data = filter_data(filter_config_options)    
            filter_output_path = filter_config_options["OUTPUT_PATH"]

            # Save the output to an Excel file
            # -------------------------------------- #
            with pd.ExcelWriter(filter_output_path) as writer:
                filtered_data.to_excel(writer, sheet_name='Filtered Data')

    else:
        print(f"Mode needs to be either 'scrape' or 'filter'. Detected '{args.mode}'.")
        sys.exit()


if __name__ == "__main__":
    args = parser.parse_args()
    main(args)
