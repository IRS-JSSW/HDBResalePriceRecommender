#!/usr/bin/env python
# coding: utf-8
from selenium import webdriver 
from selenium.webdriver.firefox.options import Options
import os
import time
import random
import threading

def StartSeleniumWindows(url):
    options = Options()
    options.headless = True
    #assert options.headless
    options.binary_location = r"C:\Users\yeewl\AppData\Local\Mozilla Firefox\firefox.exe"
    #options.binary_location = r"C:\Program Files\Mozilla Firefox\firefox.exe"
    driver = webdriver.Firefox(executable_path=r".\geckodriver.exe",options=options)
    driver.get(url)
    return driver

def StartSeleniumUbuntu(url):
    path = os.path.join(os.path.expanduser('~'), 'irs', 'HDBResalePriceRecommender', 'geckodriver-v0.29.0', 'geckodriver')
    options = Options()
    options.headless = True
    assert options.headless
    driver = webdriver.Firefox(executable_path=path, options=options)
    driver.get(url)
    return driver 

# initial query to get total results page
pageURL = "https://www.propertyguru.com.sg/property-for-sale?market=residential&property_type_code%5B%5D=1R&property_type_code%5B%5D=2A&property_type_code%5B%5D=2I&property_type_code%5B%5D=2S&property_type_code%5B%5D=3A&property_type_code%5B%5D=3NG&property_type_code%5B%5D=3Am&property_type_code%5B%5D=3NGm&property_type_code%5B%5D=3I&property_type_code%5B%5D=3Im&property_type_code%5B%5D=3S&property_type_code%5B%5D=3STD&property_type_code%5B%5D=4A&property_type_code%5B%5D=4NG&property_type_code%5B%5D=4S&property_type_code%5B%5D=4I&property_type_code%5B%5D=4STD&property_type_code%5B%5D=5A&property_type_code%5B%5D=5I&property_type_code%5B%5D=5S&property_type_code%5B%5D=6J&property_type_code%5B%5D=EA&property_type_code%5B%5D=EM&property_type_code%5B%5D=MG&property_type_code%5B%5D=TE&property_type=H"
driver = StartSeleniumWindows(pageURL)
elem = driver.find_elements_by_class_name("pagination")
#print(elem[0].text)
lastpage = int(elem[0].text.splitlines()[-2]) # usually «\n1\n2\n...\n441\n», hence get 2nd last element
print(lastpage)
driver.quit()


def scrape_logic(idx):    
    results = []
    residx = 0
    tic = time.perf_counter()
    pageNum = idx * 100
    pageLimit = min(((idx + 1) * 100), lastpage)
    while pageNum <= pageLimit:
        pageNum = pageNum+1
        pageURL = "https://www.propertyguru.com.sg/property-for-sale/{0}?property_type_code%5B0%5D=1R&property_type_code%5B1%5D=2A&property_type_code%5B2%5D=2I&property_type_code%5B3%5D=2S&property_type_code%5B4%5D=3A&property_type_code%5B5%5D=3NG&property_type_code%5B6%5D=3Am&property_type_code%5B7%5D=3NGm&property_type_code%5B8%5D=3I&property_type_code%5B9%5D=3Im&property_type_code%5B10%5D=3S&property_type_code%5B11%5D=3STD&property_type_code%5B12%5D=4A&property_type_code%5B13%5D=4NG&property_type_code%5B14%5D=4S&property_type_code%5B15%5D=4I&property_type_code%5B16%5D=4STD&property_type_code%5B17%5D=5A&property_type_code%5B18%5D=5I&property_type_code%5B19%5D=5S&property_type_code%5B20%5D=6J&property_type_code%5B21%5D=EA&property_type_code%5B22%5D=EM&property_type_code%5B23%5D=MG&property_type_code%5B24%5D=TE&property_type=H".format(str(pageNum))
        #print(pageURL)
        print("Page {0}".format(pageNum))
        timesleep = random.randrange(5,15)
        print("Sleep time: {0}".format(timesleep))
        time.sleep(timesleep)
        try:
            driver = StartSeleniumWindows(pageURL)
        except Exception as e:
            pageNum = pageNum-1
            print("Error {0}".format(e))    
            driver.quit()
            continue
        time.sleep(2)
        listings = driver.find_elements_by_class_name("listing-location")
        prices = driver.find_elements_by_css_selector("span.price")
        if len(listings)==0:
            pageNum = pageNum-1
            print("Sleep to avoid captcha")
            driver.quit()
            time.sleep(1)
            continue
        for i, (l, p) in enumerate(zip(listings, prices)):
            residx = residx + 1
            print("Listing {0}: {1} at {2}".format(str(residx), l.text, p.text))
            results.append([l.text, p.text])
        time.sleep(1)
        driver.quit()
        print(f"time {(time.perf_counter() - tic)/60} minutes")

N = 4   # Number of browsers to spawn
thread_list = list()

# Start test
for threadidx in range(N):
    t = threading.Thread(name='Scrape {}'.format(threadidx), target=scrape_logic, args=(threadidx,))
    t.start()
    time.sleep(1)
    print(t.name + ' started!')
    thread_list.append(t)

# Wait for all thre<ads to complete
for thread in thread_list:
    thread.join()

print('Test completed!')