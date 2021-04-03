#!/usr/bin/env python
# coding: utf-8
from selenium import webdriver 
from selenium.webdriver.firefox.options import Options
import os
import time
import random

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
def initialQuery(flattype):
    pageURL = "https://www.propertyguru.com.sg/property-for-sale?market=residential&property_type_code%5B%5D={0}&property_type=H".format(flattype)
    print(pageURL)
    driver = StartSeleniumUbuntu(pageURL)
    elem = driver.find_elements_by_class_name("pagination")
    #print(elem[0].text)
    lastpage = int(elem[0].text.splitlines()[-2]) # usually «\n1\n2\n...\n441\n», hence get 2nd last element
    print(lastpage)
    driver.quit()

    return lastpage


def scrapeType():

    results = []
    residx = 0

    listFlattype= ["1R", "2A", "2I", "2S", "3A", "3NG", "3Am", "3NGm", "3I", "3Im", "3S", "3STD", "4A", "4NG", "4S", "4I", "4STD", "5A", "5I", "5S", "6J", "EA", "EM", "MG", "TE"]

    for listIdx in range(len(listFlattype)):
        lastpage = initialQuery(listFlattype[listIdx])
        print("Last Page: {0}".format(str(lastpage)))
        tic = time.perf_counter()
        pageNum = 0
        while pageNum < lastpage:
            pageNum = pageNum+1
            pageURL = "https://www.propertyguru.com.sg/property-for-sale/{0}?property_type_code%5B0%5D={1}&property_type=H".format(str(pageNum), listFlattype[listIdx])
            print(pageURL)
            print("Page {0}".format(pageNum))
            timesleep = random.randrange(0, 10)
            print("Sleep time: {0}".format(timesleep))
            time.sleep(timesleep)
            try:
                driver = StartSeleniumUbuntu(pageURL)
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
                time.sleep(100)
                continue
            for i, (l, p) in enumerate(zip(listings, prices)):
                residx = residx + 1
                print("Listing {0}: {1} at {2}".format(str(residx), l.text, p.text))
                results.append([l.text, p.text])
            time.sleep(1)
            driver.quit()
            print(f"time {(time.perf_counter() - tic)/60} minutes")

scrapeType()