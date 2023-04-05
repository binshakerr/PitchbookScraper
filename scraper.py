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
    soup = get_soup(url)

    try:
        details['name'] = soup.find('h3').text.replace("Overview","").strip()
        details["description"] = soup.find("div",class_="pp-description").find("p",class_="pp-description_title").text.strip()
    except Exception as e:
        print(e)
        pass

    return details

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



### METHOD 1: BRUTE FORCE SEARCH

def scrape_search_results(keyword):
    url = "https://pitchbook.com/profiles/search?q=" + keyword
    print("scraping keyword: " + keyword) 
    soup = get_soup(url)
    results = []

    try:
        results_container = soup.find("ul", class_="profile-list")
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
        results = pool.map(scrape_search_results, keywords[:5]) # only 5 keywords for testing, remove this in production 
    results = [item for sublist in results for item in sublist] # flat map the results list
    results = list(set(results))                                # remove duplicates
    return results



# METHOD 2: SEARCH ENGINES 

def srcape_duckduckgo(keyword):
    url = "https://html.duckduckgo.com/html/?q=" + keyword
    print("scraping duckduckgo for keyword: " + keyword)
    soup = get_soup(url)
    result = []

    try:
        links_container = soup.find_all("a", class_="result__snippet")
        for link in links_container:
            profile_url = link["href"]
            result.append(profile_url)
    except Exception as e:
        print(e)
        pass
    
    return result


def scrape_all_duckduckgo_results():
    keywords = prepare_keywords()
    keywords = ["site:pitchbook.com/profiles " + keyword for keyword in keywords]
    with multiprocessing.Pool(processes=10) as pool:
        results = pool.map(srcape_duckduckgo, keywords[:5])         # only 5 keywords for testing, remove this in production 
    results = [item for sublist in results for item in sublist]     # flat map the results list
    results = list(set(results))                                    # remove duplicates
    results = [x for x in results if "pitchbook.com/profiles" in x] # filter actual profiles to exclude ads 
    return results



if __name__ == "__main__":
    result = scrape_all_duckduckgo_results()
    print(result)