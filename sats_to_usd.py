
import requests

def sats_to_usd(sats):
    """Convert sats to USD.
    """
    url = 'https://api.coingecko.com/api/v3/simple/price'
    params = {
	'ids': 'bitcoin',
	'vs_currencies': 'USD'
    }
    response = requests.get(url, params=params)
    # time.sleep() # TODO: consider this if I am getting timed out
    sats_to_usd_rate = response.json()['bitcoin']['usd'] / 100000000
    # return round(sats * sats_to_usd_rate, 2)
    return sats * sats_to_usd_rate

