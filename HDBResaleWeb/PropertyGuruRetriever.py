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
from HDBResaleWeb.functions import map_postal_district, railtransit, shoppingmalls, hawkercentre, supermarket
from HDBResaleWeb.addfeatureslib import geographic_position, get_nearest_railtransit, get_nearest_shoppingmall, get_orchard_distance, get_nearest_hawkercentre, get_nearest_supermarket
from sqlalchemy import create_engine, desc


def StartSeleniumWindows(url):
    options = Options()
    options.headless = True
    options.binary = FirefoxBinary(r'.\Tools\Firefox\App\Firefox\firefox.exe')
    driver = webdriver.Firefox(executable_path=r".\Tools\geckodriver.exe",options=options)
    driver.get(url)
    return driver

def StartSeleniumUbuntu(url):
    #path = os.path.join(os.path.expanduser('~'), 'irs', 'HDBResalePriceRecommender', 'geckodriver-v0.29.0', 'geckodriver')
    path = r"./Tools/geckodriver"
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

def addfeaturesPG(full_address):
    #Retrieve amenities data and CPI index
    df_railtransit = railtransit()
    df_shoppingmalls = shoppingmalls()
    df_hawkercentre = hawkercentre()
    df_supermarket = supermarket()

    onemap_postal_sector, onemap_latitude, onemap_longitude = geographic_position(full_address)

    #If latitude and longitude is found
    if (onemap_latitude != 0):
        mrt_nearest, mrt_distance = get_nearest_railtransit(onemap_latitude, onemap_longitude, df_railtransit)
        mall_nearest, mall_distance = get_nearest_shoppingmall(onemap_latitude, onemap_longitude, df_shoppingmalls)
        orchard_distance = get_orchard_distance(onemap_latitude, onemap_longitude)
        hawker_distance = get_nearest_hawkercentre(onemap_latitude, onemap_longitude, df_hawkercentre)
        market_distance = get_nearest_supermarket(onemap_latitude, onemap_longitude, df_supermarket)
        postal_district = map_postal_district(onemap_postal_sector)
    #If latitude and longitude is not found, fill with null values
    if (onemap_latitude == 0):
        mrt_nearest = "null"
        mrt_distance = 0
        mall_nearest = "null"
        mall_distance = 0
        orchard_distance = 0
        hawker_distance = 0
        market_distance = 0
        postal_district = 0

    #Connect to database
    engine = create_engine("sqlite:///HDBResaleWeb/resaleproject.db")

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
                    time.sleep(1)

                    # Items Required: Listing Location, Floor Area, Built Year, Remaining Lease, Listing URL, Price, ImageURL
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
            time.sleep(1)

            # Items Required: Listing Location, Floor Area, Built Year, Remaining Lease, Listing URL, Price, ImageURL
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
                
            driver.quit()
            print(f"time {(time.perf_counter() - tic)} seconds")
        print("***************************************")
        results.to_csv(r".\HDBResaleWeb\dataset\propguru.csv", index=False, columns=column_names)
    
    print(f"Total time taken: {(time.perf_counter() - ticStart)/3600} hours")

def scrapeSearchListing(searchurl):
    """This function scrape the information required for user's search

    Args:
        searchurl (string): Query URL (PropertyGuru)
    

    Returns:
        listingDetails (dict): ListingID, ImageURL, Street Address, Postal Code, Built Year, Remaining Lease, FlatType, Floor Area, Price
    """
    ticStart = time.perf_counter()

    try:
        if (platform.system() == "Windows"):
            driver = StartSeleniumWindows(searchurl)
        else:
            driver = StartSeleniumUbuntu(searchurl)
    except Exception as e:
        print("Error {0}".format(e))    
        driver.quit()
    time.sleep(1)

    # Items Required: ListingID, ImageURL, Street Address, Postal Code, Built Year, Remaining Lease, FlatType, Floor Area, Price
    listingT = driver.find_element_by_class_name("listing-title")
    staddrT = driver.find_element_by_xpath("//span[contains(@itemprop, 'streetAddress')]")
    postalcodeT = driver.find_element_by_xpath("//span[contains(@itemprop, 'postalCode')]")
    priceT = driver.find_element_by_xpath("//span[contains(@itemprop, 'price') and contains(@class, 'price')]")    
    flrareaT = driver.find_element_by_xpath("//div[contains(@itemprop, 'floorSize')]/span[1]")
    builtyearT = driver.find_element_by_xpath("//div[contains(@class, 'completion-year')]/div[2]")
    flatTypeT = driver.find_element_by_xpath("//div[contains(@class, 'property-attr') and contains(@class, 'property-type')]/div[2]")
    imgT = driver.find_element_by_xpath("//div[contains(@class, 'carousel-inner') and contains(@class, 'infinite')]/div[1]/span[1]/img[1]")

    imgURL = imgT.get_attribute("data-original")
    print(imgURL)
    
    # Various cleanup functions
    # get listingID from searchURL
    listingID = re.findall('^.*-([0-9]+)$',searchurl)[0]

    # floor area to sqm
    _floorarea = int(re.findall('[0-9]+',flrareaT.text)[0])
    if _floorarea <= 200:
        floorareaSqm = _floorarea
    else:
        floorareaSqm = round(_floorarea / 10.7639, 2)
    
    # clean up format for price, remove comma
    price = int(priceT.text.replace(",",""))
    
    # calculate remaining lease = 99 - (current year - builtyear)
    byear = int(re.findall('[0-9]+',builtyearT.text)[0])
    remainlease = 99 - (datetime.date.today().year - byear)
    
    # extract Flat Type
    flatType =  re.findall("^[\w]+ ",flatTypeT.text)[0].strip()


    # OUTPUT: newrow contains new listing details. can be used to output to SQL/CSV
    listingDetails = {"listingID": listingID, "imgURL": imgURL, "StreetAdd": staddrT.text, "PostCode": int(postalcodeT.text), "BuiltYear": byear, "RemainingLease": remainlease, "FlatType": flatType, "FloorArea": floorareaSqm, "Price": price}
    
    driver.quit()
    print(f"time {(time.perf_counter() - ticStart)} seconds")


    return listingDetails


def main():
    #scrapeType()
    scrapeSearchListing("https://www.propertyguru.com.sg/listing/hdb-for-sale-812a-choa-chu-kang-avenue-7-23456314")

if __name__ == "__main__":
    main()