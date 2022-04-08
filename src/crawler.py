import requests
from sources import SOURCES
import time
from bs4 import BeautifulSoup as bs
import json
from urllib.parse import urljoin
import queue
from threading import Thread, Event
from requests.adapters import HTTPAdapter
import os

urls = ["https://{}".format(x) for x in SOURCES[:20]]

def load_url(session, url):
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

def do_web_request(urls, workers_amount):
    class Worker(Thread):
        def __init__(self, request_queue):
            Thread.__init__(self)
            self.queue = request_queue
            self.results = {}
            self.session = requests.Session()
            self.session.mount("https://", HTTPAdapter(max_retries=5))
            self.session.headers["User-Agent"] = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36"
        
        def run(self):
            while not self.queue.empty():
                content = self.queue.get()
                try:
                    response = load_url(self.session,content)
                    self.results[content] = response
                finally:
                    self.queue.task_done()
            
        def join(self,timeout=None):
            self.session.close()
            Thread.join(self, timeout)
        
    q = queue.Queue()
    for url in urls:
        q.put(url)
    
    workers = []
    for _ in range(workers_amount):
        worker = Worker(q)
        worker.start()
        workers.append(worker)

    for worker in workers:
        worker.join()
    
    r = {}
    for worker in workers:
        r |= worker.results
    return r

results = do_web_request(urls, 20)
os.chdir("res")
for res in results.items():
    with open(os.path.join(os.getcwd(),res[0][8:]+".urls"), "w+", encoding='utf-8') as f:
        f.writelines("\n".join(res[1][0]))
    with open(os.path.join(os.getcwd(),res[0][8:]+".css"), "w+", encoding='utf-8') as f:
        f.writelines("\n".join(res[1][1]))
