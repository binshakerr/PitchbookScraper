import os
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup
import string
import multiprocessing
import pandas as pd

load_dotenv()
PROXY = os.getenv('PROXY')
proxies = {
      "http": PROXY,
      "https": PROXY
}

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

def scrape_search_results(keyword):
    url = "https://pitchbook.com/profiles/search?q=" + keyword
    soup = get_soup(url)
    results_container = soup.find("ul", class_="profile-list")
    print("scraping keyword: " + keyword) 
    results = []
    
    try:
        li_container = results_container.find_all("li")
        for li in li_container:
            profile_url = "https://pitchbook.com" + li.find("a")["href"]
            results.append(profile_url)
    except Exception as e:
        print(e)
        pass 

    return results


def prepare_keywords():
    keywords = []
    keywords1 = list(string.ascii_lowercase)
    #product of combination of 2 letters
    keywords2 = [a+b for a in keywords1 for b in keywords1]
    keywords = keywords1 + keywords2
    return keywords


def scrape_all_search_results():
    keywords = prepare_keywords()
    with multiprocessing.Pool(processes=10) as pool:
        results = pool.map(scrape_search_results, keywords)
    results = [item for sublist in results for item in sublist] # flat map the results list
    results = list(set(results)) # remove duplicates
    return results


def scrape_all_profiles():
    df = pd.read_csv("pitchbook_profiles.csv")
    urls = df["url"].tolist()

    with multiprocessing.Pool(processes=12) as pool:
        results = pool.map(scrape_pitchbook_profile, urls[:4])
    save_profile_details(results)    
    

def save_profile_details(results):
    dff = pd.DataFrame(results)
    dff.to_csv("pitchbook_profiles_details.csv", index=False)


def save_profiles(result):
     df = pd.DataFrame(result, columns=["url"])
     df.to_csv("pitchbook_profiles.csv", index=False)


if __name__ == "__main__":
    scrape_all_profiles()