import requests

from bs4 import BeautifulSoup

def test_scrape():
    URL = r"https://unisat.io/runes/market?tick=SATOSHI%E2%80%A2NAKAMOTO"
    page = requests.get(URL)

    soup = BeautifulSoup(page.content, "html.parser")

    # paragraphs = soup.find_all('p')
    # for paragraph in paragraphs:
    #     print(paragraph.text)

    print(soup)
    print('hello')