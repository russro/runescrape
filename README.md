# TODO
## Backend (Scraper and DB)
* **DONE **- Func for scraping price data from URL (specific coin URL).
* **DONE **- JSON database for rune tokens.
## Frontend (Discord cmd)
* Return lowest price and average of lowest prices per token (and per X number of tokens, where X is the amt of tokens per mint). Present in satoshis and USD.
* Check and stores prices in last hour, every 5 mins. Check for +/-10% change every hour and alert channel if change occurs.
* Schedule message every 4 hours of status of all tokens and how they changed in the last 24 hours.
## Future features
* Format to " !scrape satoshi.nakamoto " or just semantic similarity in general
* Maybe a new db for nickname search instead of semantic similarity
* Scrape new rune URLs on marketplace frontpage and update db.
* Notification for block height pass
## Separate ideas
* Scraping for sheets integration
* Scraping and storing for later data analysis and modeling

# Callable functions
```
!add satoshi.nakamoto
>>> Adding rune to database...
>>> SATOSHI●NAKAMOTO added!

!add ebichfjsns
>>> Adding rune to database...
>>> Rune either lacks enough entries or does not exist on UniSat.

!status
>>> # Runes Prices
## Last updated: 03:14 PM Friday, May 03, 2024
**SATOSHI●NAKAMOTO**: X sats or $Y per token | $Z per A tokens

**WADDLE●WADDLE●PENGU**: X sats or $Y per token | $Z per A tokens

!status sat.n
>>> ## Last updated: 03:14 PM Friday, May 03, 2024
**SATOSHI●NAKAMOTO**: X sats or $Y per token | $Z per A tokens

**Note**: If you would like to update the database, send "!update".

!update
>>> Scraping UniSat...
>>> Database updated!

!schedule
>>> Database gets updated every X mins. The next update will be at 03:14 PM.

```
# Scheduled/conditional functions
```
>>> # Runes Prices
## Last updated: 03:14 PM Friday, May 03, 2024
**SATOSHI●NAKAMOTO**: X sats or $Y per token | $Z per A tokens

**WADDLE●WADDLE●PENGU**: X sats or $Y per token | $Z per A tokens

>>> # Price up! We're so back.
**SATOSHI●NAKAMOTO** is up 10.47% at X sats or $Y per token | $Z per A tokens (previously X_prev sats or $Y_prev per token | $Z_prev per A tokens).

**WADDLE●WADDLE●PENGU** is down 69.42% at X sats or $Y per token | $Z per A tokens (previously X_prev sats or $Y_prev per token | $Z_prev per A tokens).

@PRICE WATCH

>>> # Price down. It's over... :pepehands:
**SATOSHI●NAKAMOTO** is down 15.55% at X sats or $Y per token | $Z per A tokens (previously X_prev sats or $Y_prev per token | $Z_prev per A tokens).

**WALL●STREET●BETS** is down 69.42% at X sats or $Y per token | $Z per A tokens (previously X_prev sats or $Y_prev per token | $Z_prev per A tokens).

@PRICE WATCH
```
