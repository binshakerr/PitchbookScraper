import requests
import xml.etree.ElementTree as ET
import gzip
import io

def scrape_sitemap(url):
    # get the sitemap
    r = requests.get(url)
    # parse the xml
    tree = ET.fromstring(r.content)
    # get all urls
    urls = []
    for u in tree.iter('{http://www.sitemaps.org/schemas/sitemap/0.9}loc'):
        urls.append(u.text)
    # return the list of urls
    return urls

def download_and_extract_gz_file(url):
    # download the file
    r = requests.get(url)
    # open the file
    with gzip.open(io.BytesIO(r.content), 'rb') as f:
        # read the file
        content = f.read()
        # parse the file
        tree = ET.fromstring(content)
        # get all the urls
        urls = []
        for url in tree.iter('{http://www.sitemaps.org/schemas/sitemap/0.9}loc'):
            urls.append(url.text)
    # return the list of urls
    return urls