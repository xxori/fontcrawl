import queue
import os
from src.worker import HTTPWorker, WorkerType

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

