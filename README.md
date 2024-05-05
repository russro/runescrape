# Discord Commands
## Callable Commands
### !add
```
!add satoshi.nakamoto
>>> Adding rune to database...
>>> SATOSHI●NAKAMOTO added!

!add satoshi.nakamoto
>>> Adding rune to database...
>>> SATOSHI●NAKAMOTO already added.

!add ebichfjsns
>>> Adding rune to database...
>>> Rune either lacks enough entries or does not exist on UniSat.
```
### !status
```
!status
>>> # Runes Prices
## Last updated: 03:14 PM Friday, May 03, 2024
**SATOSHI●NAKAMOTO**: X sats or $Y per token | $Z per A tokens

**WADDLE●WADDLE●PENGU**: X sats or $Y per token | $Z per A tokens

**Note**: If you would like to update the database, send "!update" or "!update [RUNE_NAME]".

!status sat.n
>>> ## Last updated: 03:14 PM Friday, May 03, 2024
**SATOSHI●NAKAMOTO**: X sats or $Y per token | $Z per A tokens

**Note**: If you would like to update the database, send "!update" or "!update [RUNE_NAME]".
```
### !update
```
!update
>>> Scraping UniSat...
>>> Database updated!

**Tip**: To save time, you can update a specific rune by sending "!update [RUNE_NAME]".

!update sat.n
>>> Scraping UniSat...
>>> SATOSHI●NAKAMOTO 
updated!

*Note*: If you meant to update SAT●N (instead of SATOSHI●NAKAMOTO), please add the specific rune by sending "!add [RUNE_NAME]".
```
### !schedule
```
!schedule
>>> Database gets updated every X mins. The next update will be at 03:14 PM.
```
### !help
```
!help
>>> ... # prints from help.md
```

## Conditional Functions
### Every X hours
```
>>> # Runes Prices
## Last updated: 03:14 PM Friday, May 03, 2024
**SATOSHI●NAKAMOTO**: X sats or $Y per token | $Z per A tokens

**WADDLE●WADDLE●PENGU**: X sats or $Y per token | $Z per A tokens
```
### Price movements
```
>>> # Price up! We're so back.
**SATOSHI●NAKAMOTO** is up 10.47% in the last hour at X sats or $Y per token | $Z per A tokens (previously X_prev sats or $Y_prev per token | $Z_prev per A tokens).

**WADDLE●WADDLE●PENGU** is up 42.69% in the last hour at X sats or $Y per token | $Z per A tokens (previously X_prev sats or $Y_prev per token | $Z_prev per A tokens).

@PRICE WATCH

>>> # Price down. It's over... :pepehands:
**SATOSHI●NAKAMOTO** is down 15.55% in the last hour at X sats or $Y per token | $Z per A tokens (previously X_prev sats or $Y_prev per token | $Z_prev per A tokens).

**WALL●STREET●BETS** is down 69.42% in the last hour at X sats or $Y per token | $Z per A tokens (previously X_prev sats or $Y_prev per token | $Z_prev per A tokens).

@PRICE WATCH
```

# TODO
## Backend (Scraper and DB)
* **DONE** - Func for scraping price data from URL (specific coin URL).
* **DONE** - JSON database for rune tokens.
## Frontend (Discord Coommands)
* Refer to contents below section 'Discord Commands'.
## Future features
* Maybe add a new db for nickname storage and search (instead of semantic similarity search).
* Scrape new rune URLs on marketplace frontpage and update db.
* Notification for block height pass.
## Separate ideas
* Scraping for sheets integration.
* Scraping and storing for later data analysis and modeling.
