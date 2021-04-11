#!/usr/bin/env python
# coding: utf-8
from selenium import webdriver 
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
import os
import platform
import time
import re
import datetime
import random
import pandas as pd

def StartSeleniumWindows(url):
    options = Options()
    options.headless = True
    options.binary = FirefoxBinary(r'.\Tools\Firefox\App\Firefox\firefox.exe')
    driver = webdriver.Firefox(executable_path=r".\Tools\geckodriver.exe",options=options)
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

# initial query to get total results page; addquery (optional) for more than 99 pages
def initialQuery(flattype, addquery=""):
    pageURL = "https://www.propertyguru.com.sg/property-for-sale?market=residential&property_type_code%5B%5D={0}&property_type=H{1}".format(flattype, addquery)
    #print(pageURL)
    if (platform.system() == "Windows"):
        driver = StartSeleniumWindows(pageURL)
    else:
        driver = StartSeleniumUbuntu(pageURL)
    elem = driver.find_elements_by_class_name("pagination")
    #print(elem[0].text)
    lastpage = int(elem[0].text.splitlines()[-2]) # usually «\n1\n2\n...\n441\n», hence get 2nd last element
    driver.quit()

    return lastpage


def scrapeType():
    column_names = ["listingID", "listingURL", "imgURL", "ListingName", "BuiltYear", "RemainingLease", "FlatType", "FloorArea", "Price"]
    results = pd.DataFrame(columns = column_names)

    residx = 0

    listFlattype= ["1R", "2A", "2I", "2S", "3A", "3NG", "3Am", "3NGm", "3I", "3Im", "3S", "3STD", "4A", "4NG", "4S", "4I", "4STD", "5A", "5I", "5S", "6J", "EA", "EM", "MG", "TE"]
    
    ticStart = time.perf_counter()

    for listIdx in range(len(listFlattype)):
        tic = time.perf_counter()
        lastpage = initialQuery(listFlattype[listIdx])
        print("Last Page: {0}".format(str(lastpage)))

        pageNum = 0

        # split data according to price if data is more than 99 pages, as captcha will be triggered at page 100
        if (lastpage > 99): 
            # split half
            addquery = ["&maxprice=500000", "&minprice=500001"]
            for addqueryIdx in range(0, 2):           
                lastpage = initialQuery(listFlattype[listIdx], addquery[addqueryIdx])                
                print("Last Page: {0}".format(str(lastpage)))

                pageNum = 0
                while pageNum < lastpage:
                    pageNum = pageNum+1
                    pageURL = "https://www.propertyguru.com.sg/property-for-sale/{0}?property_type_code%5B0%5D={1}&property_type=H&{2}".format(str(pageNum), listFlattype[listIdx], addquery[addqueryIdx])
                    print(pageURL)
                    print("Page {0}".format(pageNum))
                    timesleep = random.randrange(1, 3)
                    print("Sleep time: {0}".format(timesleep))
                    time.sleep(timesleep)
                    try:
                        if (platform.system() == "Windows"):
                            driver = StartSeleniumWindows(pageURL)
                        else:
                            driver = StartSeleniumUbuntu(pageURL)
                    except Exception as e:
                        pageNum = pageNum-1
                        print("Error {0}".format(e))    
                        driver.quit()
                        continue
                    time.sleep(2)

                    # Items Required: Listing Location, Floor Area, Listing URL, Price, ImageURL
                    listings = driver.find_elements_by_class_name("listing-location")
                    flrarea = driver.find_elements_by_xpath("//li[contains(@class, 'listing-floorarea') and contains(@class, 'pull-left') and contains(text(), 'sqft')]")
                    builtyear = driver.find_elements_by_xpath("//ul[contains(@class, 'clear-both') and contains(@class, 'listing-property-type')]/li[3]")
                    prices = driver.find_elements_by_css_selector("span.price")
                    
                    imgs = driver.find_elements_by_xpath("//div[contains(@class, 'col-xs-12') and contains(@class, 'col-sm-5') and contains(@class, 'image-container')]/div[1]/div[1]/a/ul/li[1]/img[1]")

                    # within sms_button
                    smsbutton = driver.find_elements_by_class_name("sms-button")

                    for i, (l, f, y, p, s, img) in enumerate(zip(listings, flrarea, builtyear, prices, smsbutton, imgs)):
                        residx = residx + 1

                        # floor area
                        # if floor area is smaller than 200sqft, it doesn't make sense for HDB (likely agent put wrongly as sqft). Hence, convert to sqm
                        # sqft to sqm: div by 10.7639
                        _floorarea = int(re.findall('[0-9]+',f.text)[0])
                        if _floorarea <= 200:
                            floorareaSqm = _floorarea
                        else:
                            floorareaSqm = _floorarea / 10.7639

                        print("Listing {0}: {1}, {2}, {3} at {4}".format(str(residx), l.text, y.text, floorareaSqm, p.text))

                        # calculate remaining lease = 99 - (current year - builtyear)
                        byear = int(re.findall('[0-9]+',y.text)[0])
                        remainlease = 99 - (datetime.date.today().year - byear)

                        # clean up format for price, remove comma
                        price = int(p.text.replace(",",""))

                        listingID = s.get_attribute("data-listing-id")
                        print(listingID)
                        listingURL = s.get_attribute("href").replace("#contact-agent", "")
                        print(listingURL)                
                        imgURL = img.get_attribute("data-original")
                        print(imgURL)

                        # OUTPUT: newrow contains new listing details. can be used to output to SQL/CSV
                        newrow = {"listingID": listingID, "listingURL": listingURL, "imgURL": imgURL, "ListingName": l.text, "BuiltYear": byear, "RemainingLease": remainlease, "FlatType": listFlattype[listIdx], "FloorArea": floorareaSqm, "Price": price}
                        results = results.append(newrow, ignore_index = True)

                    time.sleep(1)
                    driver.quit()
                    print(f"time {(time.perf_counter() - tic)} seconds")
                print("***************************************")
                results.to_csv(r".\Output.WebScrapingPG.csv", index=False, columns=column_names)
            continue

        while pageNum < lastpage:
            pageNum = pageNum+1
            pageURL = "https://www.propertyguru.com.sg/property-for-sale/{0}?property_type_code%5B0%5D={1}&property_type=H".format(str(pageNum), listFlattype[listIdx])
            print("Page {0}".format(pageNum))
            print(pageURL)
            timesleep = random.randrange(1, 3)
            print("Sleep time: {0}".format(timesleep))
            time.sleep(timesleep)
            try:
                if (platform.system() == "Windows"):
                    driver = StartSeleniumWindows(pageURL)
                else:
                    driver = StartSeleniumUbuntu(pageURL)
            except Exception as e:
                pageNum = pageNum-1
                print("Error {0}".format(e))    
                driver.quit()
                continue
            time.sleep(2)

            # Items Required: Listing Location, Floor Area, Remaining Lease, Listing URL, Price, ImageURL
            listings = driver.find_elements_by_class_name("listing-location")
            flrarea = driver.find_elements_by_xpath("//li[contains(@class, 'listing-floorarea') and contains(@class, 'pull-left') and contains(text(), 'sqft')]")
            builtyear = driver.find_elements_by_xpath("//ul[contains(@class, 'clear-both') and contains(@class, 'listing-property-type')]/li[3]")
            prices = driver.find_elements_by_css_selector("span.price")
            
            imgs = driver.find_elements_by_xpath("//div[contains(@class, 'col-xs-12') and contains(@class, 'col-sm-5') and contains(@class, 'image-container')]/div[1]/div[1]/a/ul/li[1]/img[1]")

            # within sms_button
            smsbutton = driver.find_elements_by_class_name("sms-button")

            for i, (l, f, y, p, s, img) in enumerate(zip(listings, flrarea, builtyear, prices, smsbutton, imgs)):
                residx = residx + 1

                # floor area
                # if floor area is smaller than 200sqft, it doesn't make sense for HDB (likely agent put wrongly as sqft). Hence, convert to sqm
                # sqft to sqm: div by 10.7639
                _floorarea = int(re.findall('[0-9]+',f.text)[0])
                if _floorarea <= 200:
                    floorareaSqm = _floorarea
                else:
                    floorareaSqm = _floorarea / 10.7639

                print("Listing {0}: {1}, {2}, {3} at {4}".format(str(residx), l.text, y.text, floorareaSqm, p.text))

                # calculate remaining lease = 99 - (current year - builtyear)
                byear = int(re.findall('[0-9]+',y.text)[0])
                remainlease = 99 - (datetime.date.today().year - byear)
                
                # clean up format for price, remove comma
                price = int(p.text.replace(",",""))

                listingID = s.get_attribute("data-listing-id")
                print(listingID)
                listingURL = s.get_attribute("href").replace("#contact-agent", "")
                print(listingURL)                
                imgURL = img.get_attribute("data-original")
                print(imgURL)

                # OUTPUT: newrow contains new listing details. can be used to output to SQL/CSV
                newrow = {"listingID": listingID, "listingURL": listingURL, "imgURL": imgURL, "ListingName": l.text, "BuiltYear": byear, "RemainingLease": remainlease, "FlatType": listFlattype[listIdx], "FloorArea": floorareaSqm, "Price": price}
                results = results.append(newrow, ignore_index = True)
                
            time.sleep(1)
            driver.quit()
            print(f"time {(time.perf_counter() - tic)} seconds")
        print("***************************************")
        results.to_csv(r".\HDBResaleWeb\dataset\propguru.csv", index=False, columns=column_names)
    
    print(f"Total time taken: {(time.perf_counter() - ticStart)/3600} hours")

def main():
    scrapeType()

if __name__ == "__main__":
    main()