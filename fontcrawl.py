import src.crawler as c
from src.sources import SOURCES
from src.analyser import analyse_css
import time
import matplotlib.pyplot as plt

# Loading in top website urls and prepending protocol
urls = ["https://{}".format(x) for x in SOURCES[:50]]

# Initialise timer
time1 = time.time()

if __name__ == '__main__':
    
    #Stage 1: GETting all websites, putting style from <style> tag into .css file, putting links from css <link> tag in .urls file
    results = c.do_css_scrape(urls, 20)
    print("Writing files")

    c.write_scrape(results)

    print(f"Stage 1 completed. Total time: {time.time()-time1:.2f}s")

    # Stage 2: gathering external styles from <link> tags, getting the css, and appending
    time2 = time.time()
    data = c.process_urls()

    results2 = c.do_url_scrape(data, 20)
    print("Writing files")
    c.write_external(results2)

    print(f"Stage 2 completed in {time.time()-time2:.2f}s")
    
    print()
    print("Analysing CSS and extracting fonts")
    results3 = analyse_css("res")
    print(f"All tasks completed. Total time elapsed: {time.time()-time1:.2f}")

    #manually tidy up some chinese font names that get messed up
    labels = []
    dl = []
    for k in results3.keys():
        if "5fae" in k:
            results3["microsoft yahei"] += results3[k]
            dl.append(k)
        else:
            labels.append(k)
    
    for d in dl:
        del results3[d]

    plt.pie(results3.values(),labels=labels)
    plt.show()
