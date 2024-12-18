
"""
Before using this script, please follow the instructions
at https://docs.gspread.org/en/latest/oauth2.html
to enable gspread to edit the specified sheet.
"""

import schedule
import time
import gspread

from runescrape import rune_name_standardizer, read_json
from runescrape import PRICE_DATABASE_PATH
from sats_to_usd import sats_to_usd


SHEETS_URL = r"https://docs.google.com/spreadsheets/d/1NGot3Ks3fbJL3ZRF7yCRSfBsqNKIjPXJWYMAftRkUgU/edit#gid=1484089764"

def init_worksheet_and_runes(sheets_url):
    """Open sheet and retrieve standardized rune_names
    """
    gc = gspread.service_account()
    book = gc.open_by_url(SHEETS_URL)
    worksheet = book.worksheet("Accounting") # open sheet

    rune_names = worksheet.col_values(1) # get rune names from first col
    rune_names.pop(0), rune_names.pop(-1) # remove col title and 'totals'

    rune_names_std = [rune_name_standardizer(name) for name in rune_names]

    return worksheet, rune_names_std

def construct_runes_corresponding_prices(rune_names_std, runes_db):
    """Construct list of latest prices with indices corresponding to rune in rune_names_std
    """
    runes_corresponding_prices = [0]*len(rune_names_std) # preallocate array
    for i, name in enumerate(rune_names_std):
        try:
            token_price_usd = sats_to_usd(runes_db[name]['price_array'][-1])
            runes_corresponding_prices[i] = [token_price_usd]
        except KeyError:
            runes_corresponding_prices[i] = ['RUNE NOT FOUND IN DB']
        except Exception as e:
            print(e)
            runes_corresponding_prices[i] = [e]

    return runes_corresponding_prices

def update_worksheet(rune_names_std, worksheet, runes_corresponding_prices):
    """Update the corresponding cells of the updated prices
    """
    range_end = len(rune_names_std) + 1
    worksheet.update(runes_corresponding_prices, f"P2:P{range_end}")

def main():
    """Retrieves rune names and updates corresponding rune prices in Google Sheets.
    """
    print("Updating sheet...")

    # Open sheet and retrieve standardized rune_names
    worksheet, rune_names_std = init_worksheet_and_runes(SHEETS_URL)

    # Search database for the current prices of the runes
    runes_db = read_json(PRICE_DATABASE_PATH)

    ## Construct list of latest prices with indices corresponding to rune in rune_names_std
    runes_corresponding_prices = construct_runes_corresponding_prices(rune_names_std, runes_db)

    # Update the corresponding cells of the updated prices
    update_worksheet(rune_names_std, worksheet, runes_corresponding_prices)
    
    return

schedule.every(2.5).minutes.do(main)

if __name__ == "__main__":
    while True:
        try:
            schedule.run_pending()
        except Exception as e:
            print(e)
        time.sleep(1)