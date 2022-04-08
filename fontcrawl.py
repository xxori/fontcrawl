import src.crawler as c
from src.sources import SOURCES
import time
import os
import re

# Loading in top website urls and prepending protocol
urls = ["https://{}".format(x) for x in SOURCES[:20]]

# Initialise timer
time1 = time.time()

if __name__ == '__main__':
    results = c.do_css_scrape(urls, 20)
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
    data = c.process_urls()
    results = c.do_url_scrape(data, 16)
    print("Writing files")
    for website, css in results.items():
        with open(os.path.join("res",website+".css"), "a", encoding="utf-8") as f:
            f.write("\n"+"/*BEGIN EXTERNAL CSS*/")
            # Erasing comments to save resources later on
            f.write("\n"+re.sub(r"\/\*[^*]*\*+([^/*][^*]*\*+)*\/", "", css))
        os.remove(os.path.join(os.getcwd(),"res",website+".urls"))
    print(f"Gathering external styling completed in {time.time()-time2:.2f}s")

    print()
    print(f"All tasks completed. Total time elapsed: {time.time()-time1:.2f}s")