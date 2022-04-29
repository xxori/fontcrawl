### Functions for processing data and organising workers and queues
import queue
import os
from src.worker import HTTPWorker, WorkerType
import re

def do_css_scrape(data: list, workers_amount: int):
    q = queue.Queue()
    for url in data:
        q.put(url)
    
    workers = []
    for _ in range(workers_amount):
        worker = HTTPWorker(q, WorkerType.CSS_SCRAPER)
        worker.start()
        workers.append(worker)
    ct = 1
    for worker in workers:
        ct+=1
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

def write_scrape(results):
    for file in os.listdir("res"):
        os.remove(os.path.join("res",file))
    for res in results.items():
        if len(res[1][0]):
            with open(os.path.join(os.getcwd(),"res",res[0][8:]+".urls"), "w+", encoding='utf-8') as f:
                f.writelines("\n".join(res[1][0]))
        with open(os.path.join(os.getcwd(),"res",res[0][8:]+".css"), "w+", encoding='utf-8') as f:
            
            # Erasing comments to save resources later
            f.writelines(re.sub(r"\/\*[^*]*\*+([^/*][^*]*\*+)*\/", "", "\n".join(res[1][1])))

def write_external(results):
    for website, css in results.items():
        with open(os.path.join("res",website+".css"), "a", encoding="utf-8") as f:
            f.write("\n"+"/*BEGIN EXTERNAL CSS*/")
            # Erasing comments to save resources later on
            f.write("\n"+re.sub(r"\/\*[^*]*\*+([^/*][^*]*\*+)*\/", "", css))
        os.remove(os.path.join(os.getcwd(),"res",website+".urls"))