"""Scrape BoligPortal website dependencies."""


import urllib
from bs4 import BeautifulSoup
import re
from datetime import datetime
from datetime import date
from typing import Dict, List
from tqdm import tqdm
from time import time

from dependencies.google_trans_new.google_trans_new import google_translator as ts


def make_soup(url: str) -> str:
    """Return an HTML body from an URL."""
    req = urllib.request.Request(url, headers={"User-Agent": "Magic Browser"})
    http = urllib.request.urlopen(req)

    return BeautifulSoup(http, features="html.parser")


def get_only_numbers(seq: str) -> str:
    """Return only the numbers in a string."""
    return re.sub(r"[^\d\.]", "", seq)


def remove_commas(seq: str) -> str:
    """Return a string with whitespace instead of commas."""
    return seq.replace(".", "")


def check_info(scrape_dict: Dict, key: str, placeholder="0") -> str:
    """Check if key in dictionary and return value, else 0."""
    if key in scrape_dict.keys():
        return scrape_dict[key]
    else:
        return placeholder


def convert_string_to_binary(seq: str) -> str:
    """Convert a string of Danish Ja or Nej to either 1 or 0."""
    if seq in ["Ja", "Yes"]:
        return 1
    elif seq in ["Nej", "No"]:
        return 0
    else:
        return 0


def scrape_ad(url: str) -> Dict:
    """Fully scrape an ad from Bolig Portal."""
    soup = make_soup(url)
    translator = ts()

    # Fetch the keys of the apartment details e.g. 'Pet Friendly'
    key_details_section = soup.find_all("span", {"class": "css-1218edi"})
    keys = [x.text for x in key_details_section]

    # Subsequently, fetch the values of the keys e.g. 'Yes'
    value_details_section = soup.find_all("span", {"class": "css-1e8e3fr"})
    values = [x.text for x in value_details_section]

    # This might mess up the key-value pairs if present
    if "Internet" in keys:
        keys.remove("Internet")

    # When this is present, it actually displays a PNG, not text.
    # I don't really want to deal with this. But otherwise, the name
    # of the energy mark is in the picture name e.g. 'D_str2.png'
    if len(keys) != len(values):
        keys.remove("Energimærke")

    scrape_dict = {}
    for i in range(0, len(keys)):
        scrape_dict[keys[i]] = values[i]

    # Retrieve info
    full_address = soup.find_all("div", {"class": "css-1bbi9fj"})[1].text
    summary = soup.find("div", {"class": "css-1oj64sa"}).text
    housing_type = check_info(scrape_dict, "Boligtype", "")
    size = check_info(scrape_dict, "Størrelse", "0")
    number_of_rooms = check_info(scrape_dict, "Værelser", "0")
    floor = check_info(scrape_dict, "Etage", "0")
    is_furnished = check_info(scrape_dict, "Møbleret", "Nej")
    is_shareable = check_info(scrape_dict, "Delevenlig", "Nej")
    pets_allowed = check_info(scrape_dict, "Husdyr tilladt", "Nej")
    has_elevator = check_info(scrape_dict, "Elevator", "Nej")
    students_only = check_info(scrape_dict, "Kun for studerende", "Nej")
    has_balcony = check_info(scrape_dict, "Balkon/altan", "Nej")
    has_parking = check_info(scrape_dict, "Parkering", "Nej")
    rental_period = check_info(scrape_dict, "Lejeperiode", "")
    available_from = check_info(scrape_dict, "Ledig fra", "")
    monthly_rent = check_info(scrape_dict, "Månedlig leje", "0")
    aconto = check_info(scrape_dict, "Aconto", "0")
    deposit = check_info(scrape_dict, "Depositum", "0")
    prepaid_rent = check_info(scrape_dict, "Forudbetalt husleje", "0")
    occupancy_price = check_info(scrape_dict, "Indflytningspris", "0")
    creation_date = check_info(scrape_dict, "Oprettelsesdato", "")

    # Cleaning
    # ----------------- #
    # Since the numerical values are all strings with added currency figures etc:
    numerical_values = [
        number_of_rooms,
        monthly_rent,
        aconto,
        deposit,
        prepaid_rent,
        occupancy_price,
    ]

    for i in range(0, len(numerical_values)):
        numerical_values[i] = int(remove_commas(get_only_numbers(numerical_values[i])))

    (
        number_of_rooms,
        monthly_rent,
        aconto,
        deposit,
        prepaid_rent,
        occupancy_price,
    ) = numerical_values

    size = float(get_only_numbers(size))
    try:
        floor = int(remove_commas(get_only_numbers(floor)))
    except ValueError:
        floor = translator.translate(floor, lang_src="da", lang_tgt="en").strip()

    # Binaries
    is_furnished = convert_string_to_binary(is_furnished)
    is_shareable = convert_string_to_binary(is_shareable)
    pets_allowed = convert_string_to_binary(pets_allowed)
    has_elevator = convert_string_to_binary(has_elevator)
    students_only = convert_string_to_binary(students_only)
    has_balcony = convert_string_to_binary(has_balcony)
    has_parking = convert_string_to_binary(has_parking)

    # Strings
    full_address_list = full_address.split(sep=",")
    if len(full_address_list) == 3:
        street = full_address_list[0]
        zip_code = get_only_numbers(full_address_list[1])
        district = full_address_list[2].split("-")[0].strip()
    else:
        street = full_address_list[0]
        zip_code = get_only_numbers(full_address_list[1].split("-")[0])
        district = full_address_list[1].split("-")[0].replace(zip_code, "").strip()

    summary = re.sub(r"\n", "", summary)
    summary = re.sub(r"\t", "", summary)

    # Dates
    creation_date = datetime.strptime(creation_date, "%d.%m.%Y").date()
    if available_from == "Snarest muligt":
        available_from = date.today()
    else:
        available_from = translator.translate(available_from, lang_src="da", lang_tgt="en").strip()
        available_from = remove_commas(available_from)
        try:
            available_from = datetime.strptime(available_from, "%d %B %Y").date()
        except ValueError:
            try:
                available_from = datetime.strptime(available_from, "%B %d %Y").date()
            except ValueError:
                try:
                    available_from = datetime.strptime(available_from, "%B %d, %Y").date()
                except ValueError:
                    available_from = None

    # Translations
    housing_type = translator.translate(housing_type, lang_src="da", lang_tgt="en").strip()
    rental_period = translator.translate(rental_period, lang_src="da", lang_tgt="en").strip()
    summary = translator.translate(summary, lang_src="da", lang_tgt="en").strip()

    # Calculated fields
    total_monthly_cost = monthly_rent + aconto
    months_of_prepaid_rent = int(prepaid_rent / monthly_rent)
    months_of_deposit = int(deposit / monthly_rent)

    ad = {
        "url": url,
        "creation_date": creation_date,
        "scraped_date": date.today(),
        "full_address": full_address,
        "street": street,
        "zip_code": zip_code,
        "district": district,
        "housing_type": housing_type,
        "size": size,
        "number_of_rooms": number_of_rooms,
        "floor": floor,
        "rental_period": rental_period,
        "available_from": available_from,
        "summary": summary,
        "monthly_rent": monthly_rent,
        "aconto": aconto,
        "deposit": deposit,
        "prepaid_rent": prepaid_rent,
        "occupancy_price": occupancy_price,
        "total_monthly_cost": total_monthly_cost,
        "months_of_prepaid_rent": months_of_prepaid_rent,
        "months_of_deposit": months_of_deposit,
        "is_furnished": is_furnished,
        "is_shareable": is_shareable,
        "pets_allowed": pets_allowed,
        "has_elevator": has_elevator,
        "students_only": students_only,
        "has_balcony": has_balcony,
        "has_parking": has_parking,
    }

    return ad


def scrape_ads_urls(main_url: str, pages: int) -> List:
    """
    Go to main results page, parse all susequent pages and
    retrieve links to all properties.
    """
    start_time = time()
    all_links = []

    for i in tqdm(range(0, pages)):
        if i != 0:
            next_page = f"&offset={18*i}"
            soup = make_soup(main_url + next_page)
        else:
            soup = make_soup(main_url)

        for div in soup.find_all("div", {"class": "css-1e7fg19"}):
            a = div.find("a", href=True)
            all_links.append("https://www.boligportal.dk" + a["href"])

    end_time = time()
    runtime = end_time - start_time
    print(f"Scraping for Ad URLs finished in {round(runtime,2):,}s")

    all_links = set(all_links)
    print(f"{len(all_links)} links found.")

    return all_links
