
import requests

def sats_to_usd(sats):
    """Convert sats to USD.
    """
    response = requests.get('https://api.coindesk.com/v1/bpi/currentprice.json')
    # time.sleep() # TODO: consider this if I am getting timed out
    sats_to_usd_rate = response.json()['bpi']['USD']['rate_float'] / 100000000
    # return round(sats * sats_to_usd_rate, 2)
    return sats * sats_to_usd_rate

