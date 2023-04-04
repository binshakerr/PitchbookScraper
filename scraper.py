import os
from dotenv import load_dotenv
load_dotenv()
PROXY = os.getenv('PROXY')
proxies = {
                "http": PROXY,
                "https": PROXY
    }
import requests
from bs4 import BeautifulSoup


def get_soup(url):
    headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36"}
    r = requests.get(url, headers=headers, proxies=proxies)
    soup = BeautifulSoup(r.text, 'html.parser')
    return soup

def scrape_pitchbook_profile(url):
    details = {}
    details["url"] = url

    try:
        soup = get_soup(url)
        details['name'] = soup.find('h3').text.replace("Overview","").strip()
        details["description"] = soup.find("div",class_="pp-description").find("p",class_="pp-description_title").text.strip()
    except:
        pass
    return details


### METHOD 1: BRUTE FORCE SEARCH

if __name__ == "__main__":
    print(scrape_pitchbook_profile("https://pitchbook.com/profiles/company/167175-28"))