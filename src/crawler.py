from typing import Tuple
import requests
from sources import SOURCES
import time
from bs4 import BeautifulSoup as bs
from urllib.parse import urljoin
import queue
from threading import Thread
from requests.adapters import HTTPAdapter
import os
from enum import Enum
import re

# Loading in top website urls and prepending protocol
urls = ["https://{}".format(x) for x in SOURCES[:20]]

# Initialise timer
time1 = time.time()

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


def do_css_scrape(data: list, workers_amount: int):
    q = queue.Queue()
    for url in data:
        q.put(url)
    
    workers = []
    for _ in range(workers_amount):
        worker = HTTPWorker(q, WorkerType.CSS_SCRAPER)
        worker.start()
        workers.append(worker)

    for worker in workers:
        worker.join()
    
    r = {}
    for worker in workers:
        r |= worker.results
    return r

def do_url_scrape(data: list, workers_amount: int):
    q = queue.Queue()
    for urls in data:
        q.put(urls)
    
    workers = []
    for _ in range(workers_amount):
        worker = HTTPWorker(q, WorkerType.CSS_GETTER)
        worker.start()
        workers.append(worker)
    
    for worker in workers:
        worker.join()
    
    r = {}
    for worker in workers:
        r |= worker.results
    return r

def process_urls():
    res = []
    for file in os.listdir(os.path.join(os.getcwd(),"res")):
        if file.endswith("urls"):
            website_name = file[:-5]
            with open(os.path.join("res",file),"r") as f:
                res.append((website_name,f.read().split("\n")))
    return res



if __name__ == '__main__':
    results = do_css_scrape(urls, 20)
    print(f"Requests completed in {time.time()-time1:.2f}s")
    print("Writing files")

    for res in results.items():
        if len(res[1][0]):
            with open(os.path.join(os.getcwd(),"res",res[0][8:]+".urls"), "w+", encoding='utf-8') as f:
                f.writelines("\n".join(res[1][0]))
        with open(os.path.join(os.getcwd(),"res",res[0][8:]+".css"), "w+", encoding='utf-8') as f:
            
            # Erasing comments to save resources later
            f.writelines(re.sub(r"\/\*[^*]*\*+([^/*][^*]*\*+)*\/", "", "\n".join(res[1][1])))

    print(f"Scraping completed. Total time: {time.time()-time1:.2f}s")
    time2 = time.time()
    data = process_urls()
    results = do_url_scrape(data, 16)
    print("Writing files")
    for website, css in results.items():
        with open(os.path.join("res",website+".css"), "a", encoding="utf-8") as f:
            f.write("\n"+"/*BEGIN EXTERNAL CSS*/")
            # Erasing comments to save resources later on
            f.write("\n"+re.sub(r"\/\*[^*]*\*+([^/*][^*]*\*+)*\/", "", css))
        os.remove(os.path.join(os.getcwd(),"res",website+".urls"))
    print(f"Gathering external styling completed in {time.time()-time2:.2f}")