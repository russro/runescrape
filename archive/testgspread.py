
import gspread

from runescrape import rune_name_standardizer, read_json, PRICE_DATABASE_PATH


SHEETS_URL = r"https://docs.google.com/spreadsheets/d/1NGot3Ks3fbJL3ZRF7yCRSfBsqNKIjPXJWYMAftRkUgU/edit#gid=1484089764"

# Open sheet and retrieve standardized rune_names
gc = gspread.service_account()
book = gc.open_by_url(SHEETS_URL)
worksheet = book.worksheet("Accounting") # open sheet

rune_names = worksheet.col_values(1) # get rune names from first col
rune_names.pop(0), rune_names.pop(-1) # remove col title and 'totals'

rune_names_std = [rune_name_standardizer(name) for name in rune_names]

# Search database for the current prices of the runes
runes_db = read_json(PRICE_DATABASE_PATH)

## Construct list of latest prices with indices corresponding to rune in rune_names_std
runes_corresponding_prices = [0]*len(rune_names_std) # preallocate array
for i, name in enumerate(rune_names_std):
    try:
        runes_corresponding_prices[i] = [runes_db[name]['price_array'][-1]]
    except KeyError:
        runes_corresponding_prices[i] = ['RUNE NOT FOUND IN DB']
    except Exception as e:
        runes_corresponding_prices[i] = [e]

# Update the corresponding cells of the updated prices
range_end = len(rune_names_std) + 1
worksheet.update(runes_corresponding_prices, f"P2:P{range_end}")