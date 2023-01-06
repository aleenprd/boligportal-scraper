"""Utilities to filter your searches in the CSV coming from scraping."""


import pandas as pd
from datetime import datetime, timedelta, date
from typing import List, Union, Dict


def isin_list(df: pd.DataFrame, col: str, filter: List) -> pd.DataFrame:
    """Check if series values in list and return filtered df."""
    boolean_series = df[col].isin(filter)
    df = df[boolean_series]
    return df


def is_not_in_list(df: pd.DataFrame, col: str, filter: List) -> pd.DataFrame:
    """Check if series values is not in list and return filtered df."""
    boolean_series = df[col].isin(filter)
    df = df[~boolean_series]
    return df


def obj_to_date(creation_date: str) -> datetime.date:
    """Convert object/string to date."""
    return datetime.strptime(creation_date, '%m/%d/%Y').date()


def filter_data(config_options: Dict[str, Union[str, int]]) -> pd.DataFrame:
    """Apply user defined filters to dataframe."""
    # I/O
    input_path = config_options["INPUT_PATH"]

    # Listing time details
    max_days_since_creation = config_options["MAX_DAYS_SINCE_CREATION"]
    rental_period_filter = config_options["RENTAL_PERIOD_FILTER"]
    available_from_range = config_options["AVAILABLE_FROM_RANGE"]

    # Area
    use_zipcode_filter = config_options["USE_ZIPCODE_FILTER"]
    zipcode_filter_type = config_options["ZIPCODE_FILTER_TYPE"]
    zipcode_list_filter = config_options["ZIPCODE_LIST_FILTER"]
    zipcode_range_filter = config_options["ZIPCODE_RANGE_FILTER"]
    zipcode_exclude_filter = config_options["ZIPCODE_EXCLUDE_FILTER"]
    use_district_filter = config_options["USE_DISTRICT_FILTER"]
    district_filter = config_options["DISTRICT_FILTER"]

    # Money options
    total_rent_max = config_options["TOTAL_RENT_MAX"]
    deposit_max = config_options["DEPOSIT_MAX"]
    prepaid_rent = config_options["PREPAID_RENT"]
    prepaid_rent_max = config_options["PREPAID_RENT_MAX"]
    occupancy_price_max = config_options["OCCUPANCY_PRICE_MAX"]

    # Housing base characteristics'
    use_housing_type_filter = config_options["USE_HOUSING_TYPE_FILTER"]
    housing_type_filter = config_options["HOUSING_TYPE_FILTER"]
    num_rooms_filter = config_options["NUMBER_OF_ROOMS_FILTER"]
    size_filter = config_options["SIZE_FILTER"]
    is_furnished = config_options["FURNISHED"]
    is_shareable = config_options["SHAREABLE"]
    pets_allowed = config_options["PETS_ALLOWED"]
    has_elevator = config_options["HAS_ELEVATOR"]
    students_only = config_options["STUDENTS_ONLY"]
    has_balcony = config_options["HAS_BALCONY"]
    has_parking = config_options["HAS_PARKING"]

    # Load & pre-process the data
    # -------------------------------------- #
    df = pd.read_csv(input_path)

    print(f"\nInitial selection of: {df.shape[0]} listings.")

    df["creation_date"] = df["creation_date"].apply(lambda x: obj_to_date(x))
    df["available_from"] = df["available_from"].apply(lambda x: obj_to_date(x))
    df["scraped_date"] = df["scraped_date"].apply(lambda x: obj_to_date(x))

    # Filtering the data
    # -------------------------------------- #

    # Listing time details
    todays_date = date.today()
    earliest_creation_date = todays_date - timedelta(
        days=max_days_since_creation)
    df = df[df["creation_date"] >= earliest_creation_date]

    df = isin_list(df, "rental_period", rental_period_filter)

    available_from_start = obj_to_date(available_from_range[0])
    available_from_end = obj_to_date(available_from_range[1])

    df = df[df["available_from"] >= available_from_start]
    df = df[df["available_from"] <= available_from_end]

    # Area
    if use_zipcode_filter == "yes":
        if zipcode_filter_type == "range":
            df = df[df["zip_code"] >= zipcode_range_filter[0]]
            df = df[df["zip_code"] <= zipcode_range_filter[1]]
        elif zipcode_filter_type == "list":
            df = isin_list(df, "zip_code", zipcode_list_filter)
        elif zipcode_filter_type == "exclude":
            df = is_not_in_list(df, "zip_code", zipcode_exclude_filter)
        else:
            print("\nWrong filter type for ZIP codes. Retry.")

    if use_district_filter == "yes":
        df = isin_list(df, "district", district_filter)

    # Money options
    df = df[df["total_monthly_cost"] <= total_rent_max]
    df = df[df["months_of_deposit"] <= deposit_max]

    if prepaid_rent == "yes":
        df = df[df["months_of_prepaid_rent"] <= prepaid_rent_max]

    df = df[df["occupancy_price"] <= occupancy_price_max]

    # Housing base characteristics
    if use_housing_type_filter == "yes":
        df = isin_list(df, "housing_type", housing_type_filter)

    df = df[df["number_of_rooms"] >= num_rooms_filter[0]]
    df = df[df["number_of_rooms"] <= num_rooms_filter[1]]

    df = df[df["size"] >= size_filter[0]]
    df = df[df["size"] <= size_filter[1]]

    df = isin_list(df, "is_furnished", is_furnished)
    df = isin_list(df, "is_shareable", is_shareable)
    df = isin_list(df, "pets_allowed", pets_allowed)
    df = isin_list(df, "has_elevator", has_elevator)
    df = isin_list(df, "students_only", students_only)
    df = isin_list(df, "has_balcony", has_balcony)
    df = isin_list(df, "has_parking", has_parking)

    print(f"\nSelection reduced to: {df.shape[0]} listings.")

    return df
