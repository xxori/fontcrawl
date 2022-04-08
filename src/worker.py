from enum import Enum
from threading import Thread
import requests
from requests.adapters import HTTPAdapter
from bs4 import BeautifulSoup as bs
from urllib.parse import urljoin

class WorkerType(Enum):
    CSS_SCRAPER = 1
    CSS_GETTER = 2
    

class HTTPWorker(Thread):
    """Worker thread to send GET requests to all websites, gathering their styling"""
    def __init__(self, request_queue, type):
        Thread.__init__(self)
        # Request queue to store links
        self.queue = request_queue

        self.type = type
        if type == WorkerType.CSS_SCRAPER:
            self.payload = scrape_style
        elif type == WorkerType.CSS_GETTER:
            self.payload = scrape_urls
        else:
            raise TypeError("Invalid Worker Type")

        self.results = {}

        # Initialising HTTP session to get websites, with a real-looking useragent and 5 maximum retries to keep it quick
        self.session = requests.Session()
        self.session.mount("https://", HTTPAdapter(max_retries=3))
        self.session.headers["User-Agent"] = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36"
    
    def run(self):
        # Each worker thread remains alive until there are no links left
        while not self.queue.empty():
            content = self.queue.get()
            try:
                if self.type == WorkerType.CSS_SCRAPER:
                    response = self.payload(self.session,content)
                    self.results[content] = response
                elif self.type == WorkerType.CSS_GETTER:
                    response = self.payload(self.session, content)
                    self.results[content[0]] = response
            finally:
                # Mark the website as complete even if error occurs so other threads to not try to get it repeatedly
                self.queue.task_done()
    
    def join(self,timeout=None):
        # Sanely exit thread by closing http session, would probably be done automatically anyway
        self.session.close()
        Thread.join(self, timeout)


### BEGIN PAYLOADS ###

def scrape_style(session, url):
    print("Getting "+url)
    html = session.get(url).text
    soup = bs(html, 'html.parser')

    css_files = []
    css_tags = []

    for css in soup.find_all("style"):
        css_tags.append(css.text)

    for css in soup.find_all("link"):
        if css.attrs.get("href"):
            css_url=urljoin(url, css.attrs.get("href"))
            if "css" in css_url.lower():
                css_files.append(css_url)
    
    return (css_files,css_tags)

def scrape_urls(session,data):
    print("Getting external styles for "+data[0])
    res = ""
    for url in data[1]:
        res += session.get(url).text + "\n"
    return res

