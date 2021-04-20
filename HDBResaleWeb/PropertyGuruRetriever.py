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


from HDBResaleWeb.functions import map_postal_district, railtransit, shoppingmalls, hawkercentre, supermarket
from HDBResaleWeb.models import DataGovTable, PropGuruTable, RailTransitTable, ShoppingMallsTable, HawkerCentreTable, SuperMarketTable
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

def getListingName(listingURL):
    """This function infers the listing name from the listing URL
    Scenario to clean property name that:
    - Does not start with digit (block number)

    Args:
        listingURL ([string]): listingURL

    Returns:
        [string]: Listing Name
    """
    temp = re.search(r"hdb-for-sale\D*-(\S+)-\d+", listingURL).group(1)
    return temp.replace("-", " ")

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

def addfeaturesPG(pgDF):
    """Add Columns to PG Data
    all rows listing names must not be empty

    Args:
        

    Returns:
        

    """
    #pgDF = pd.read_csv(r".\HDBResaleWeb\dataset\propguru.csv")

    df_insert = pd.DataFrame(columns=["id","flat_type","listing_url", "img_url", "listing_name","floor_area_sqm","lease_commence_date","remaining_lease","resale_price",
                "latitude","longitude","postal_district","mrt_nearest","mrt_distance",
                "mall_nearest","mall_distance","orchard_distance","hawker_distance","market_distance"])

    #Retrieve amenities data and CPI index
    df_railtransit = railtransit()
    df_shoppingmalls = shoppingmalls()
    df_hawkercentre = hawkercentre()
    df_supermarket = supermarket()

    print(pgDF.info())
    #Loop through the records to update
    for i in range(0, len(pgDF)):
        #Get the full address of the record to retrieve the latitude, longitude and postal sector from Onemap or Google
        full_address = pgDF.iloc[i]['ListingName']
        #print("{0}: {1}".format(pgDF.iloc[i]['listingID'],pgDF.iloc[i]['ListingName']))
        try:
            onemap_postal_sector, onemap_latitude, onemap_longitude = geographic_position(full_address)
            print("{0}: {1}".format(onemap_postal_sector,pgDF.iloc[i]['ListingName']))
            #If postal sector is not found, it could be listing name is wrong. try to infer from listingURL
            if (onemap_postal_sector == ""):
                full_address = getListingName(pgDF.loc[i,'listingURL'])
                onemap_postal_sector, onemap_latitude, onemap_longitude = geographic_position(full_address)
                if(onemap_postal_sector != ""):
                    pgDF.loc[i, 'ListingName'] = full_address
                else:
                    continue
            #print(onemap_postal_sector, onemap_latitude, onemap_longitude)
        except Exception as e:
            print(str(e))
            print("ERROR: {0}".format(pgDF.iloc[i]['listingID']))
            continue
        #If latitude and longitude is found
        if (onemap_latitude != 0):
            mrt_nearest, mrt_distance = get_nearest_railtransit(onemap_latitude, onemap_longitude, df_railtransit)
            mall_nearest, mall_distance = get_nearest_shoppingmall(onemap_latitude, onemap_longitude, df_shoppingmalls)
            orchard_distance = get_orchard_distance(onemap_latitude, onemap_longitude)
            hawker_distance = get_nearest_hawkercentre(onemap_latitude, onemap_longitude, df_hawkercentre)
            market_distance = get_nearest_supermarket(onemap_latitude, onemap_longitude, df_supermarket)
            postal_district = int(map_postal_district(onemap_postal_sector))
    
        #If latitude is not found, fill with null values
        if (onemap_latitude == 0):
            print("UNABLE TO GET ONEMAP")
            print(pgDF.iloc[i]['listingID'])
            mrt_nearest = "null"
            mrt_distance = 0
            mall_nearest = "null"
            mall_distance = 0
            orchard_distance = 0
            hawker_distance = 0
            market_distance = 0
            postal_district = 0


        #pending: need check onemap_postal_sector not null
        df_insert = df_insert.append({
            "id": pgDF.iloc[i]['listingID'],
            "flat_type": pgDF.iloc[i]['FlatType'],
            "listing_url": pgDF.iloc[i]['listingURL'],
            "img_url": pgDF.iloc[i]['imgURL'],
            "listing_name": pgDF.iloc[i]['ListingName'],
            "floor_area_sqm": float(pgDF.iloc[i]['FloorArea']),
            "lease_commence_date": int(pgDF.iloc[i]['BuiltYear']),
            "remaining_lease": int(pgDF.iloc[i]['RemainingLease']),
            "resale_price": int(pgDF.iloc[i]['Price']),
            "latitude": float(onemap_latitude),
            "longitude": float(onemap_longitude),
            "postal_district": postal_district,
            "mrt_nearest": mrt_nearest,
            "mrt_distance": mrt_distance,
            "mall_nearest": mall_nearest,
            "mall_distance": mall_distance,
            "orchard_distance": orchard_distance,
            "hawker_distance": hawker_distance,
            "market_distance": market_distance
        }, ignore_index=True)
    
    # set listingID as index
    df_insert.set_index('id')
    df_insert.to_csv('.\HDBResaleWeb\dataset\propguru_complete.csv')
    
    # Connect to database
    engine = create_engine("sqlite:///HDBResaleWeb/resaleproject.db")
    
    # Remove existing data, then insert dataframe into sqlite database (without removing PK constraint)
    with engine.connect() as con:
        rs = con.execute('DELETE FROM prop_guru_table')
    
    df_insert.to_sql('prop_guru_table', con=engine, if_exists='append', index=False)

def summarizeFlatType(flattypePG):
    """This function converts flat type in PG to flat type in DataGov. Include what is shown on search filter and individual listing

    Args:
        flattypePG (string): flat type used in PG
    
    Returns:
        key (string): flat type used in DG

    """    
    dictFlatTypes = {"1 ROOM":["1R", "1-Room / Studio"], \
                    "2 ROOM":["2A", "2I", "2S"], \
                    "3 ROOM":["3A", "3NG", "3Am", "3NGm", "3I", "3Im", "3S", "3STD", "3NG (New Generation)", "3A (Modified)", "3NG (Modified)", "3I (Improved)", "3I (Modified)", "3S (Simplified)", "3STD (Standard)"], \
                    "4 ROOM":["4A", "4NG", "4S", "4I", "4STD", "4NG (New Generation)", "4S (Simplified)", "4I (Improved)", "4STD (Standard)"], \
                    "5 ROOM":["5A", "5I", "5S"], \
                    "JUMBO":["6J", "Jumbo"], \
                    "EXECUTIVE":["EA", "EM", "EA (Exec Apartment)", "EM (Exec Maisonette)"], \
                    "MULTI-GENERATION":["MG", "MG (Multi-Generation)"], \
                    "TERRACE":["TE", "Terrace"]}

    for key, value in dictFlatTypes.items():
         if flattypePG in value:
             return key
    
    # Key does not exist
    return ""

def scrapeType():
    column_names = ["listingID", "listingURL", "imgURL", "ListingName", "BuiltYear", "RemainingLease", "FlatType", "FloorArea", "Price"]
    results = pd.DataFrame(columns = column_names)

    residx = 0

    #listFlattype= ["1R", "2A", "2I", "2S", "3A", "3NG", "3Am", "3NGm", "3I", "3Im", "3S", "3STD"]
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
                        newrow = {"listingID": listingID, "listingURL": listingURL, "imgURL": imgURL, "ListingName": l.text, "BuiltYear": byear, "RemainingLease": remainlease, "FlatType": summarizeFlatType(listFlattype[listIdx]), "FloorArea": floorareaSqm, "Price": price}
                        results = results.append(newrow, ignore_index = True)

                    driver.quit()
                    print(f"time {(time.perf_counter() - tic)} seconds")
                print("***************************************")
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
                newrow = {"listingID": listingID, "listingURL": listingURL, "imgURL": imgURL, "ListingName": l.text, "BuiltYear": byear, "RemainingLease": remainlease, "FlatType": summarizeFlatType(listFlattype[listIdx]), "FloorArea": floorareaSqm, "Price": price}
                results = results.append(newrow, ignore_index = True)
                
            driver.quit()
            print(f"time {(time.perf_counter() - tic)} seconds")
        print("***************************************")
        
        # Clean up the dataset
        # remove duplicate listing
        results.drop_duplicates(subset=['listingID'], inplace=True, keep='last')
        
        # infer missing listing Name
        results.loc[results['ListingName'].isnull(),'ListingName'] = results.loc[results['ListingName'].isnull(),'listingURL'].apply(lambda x: getListingName(str(x)))
        # if Listing Name is pure digit, it is invalid, hence set it to Null
        results.loc[results['ListingName'].str.isdecimal(), "ListingName"] = None
        # infer missing listing Name
        results.loc[results['ListingName'].isnull(),'ListingName'] = results.loc[results['ListingName'].isnull(),'listingURL'].apply(lambda x: getListingName(str(x)))

        results.to_csv(r".\HDBResaleWeb\dataset\propguru.csv", index=False, columns=column_names)

    # add additional features to data and commit to SQL
    addfeaturesPG(results)
    
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
    
    # extract Flat Type according to DG type
    # e.g. "3NG (Modified) HDB For Sale" => 3
    flatType = summarizeFlatType(flatTypeT.text.split(" HDB")[0].strip())
    #flatType =  re.findall("^[\w]+ ",flatTypeT.text)[0].strip()

    # OUTPUT: newrow contains new listing details. can be used to output to SQL/CSV
    listingDetails = {"listingID": listingID, "imgURL": imgURL, "StreetAdd": staddrT.text, "PostCode": int(postalcodeT.text), "BuiltYear": byear, "RemainingLease": remainlease, "FlatType": flatType, "FloorArea": floorareaSqm, "Price": price}
    
    driver.quit()
    print(f"time {(time.perf_counter() - ticStart)} seconds")


    return listingDetails

# To be copied to functions.py
def update_propguru_table():
    print("update_propguru_table: Building this function...")
    print(os.getcwd())
    pgDF = pd.read_csv(r".\HDBResaleWeb\dataset\propguru.csv")
    print(pgDF.head())

    
    onemap_postal_sector, onemap_latitude, onemap_longitude = geographic_position(full_address)

def main():
    #addfeaturesPG()
    #update_propguru_table()
    scrapeType()
    #summarizeFlatType("2A")
    #scrapeSearchListing("https://www.propertyguru.com.sg/listing/hdb-for-sale-812a-choa-chu-kang-avenue-7-23456314")

if __name__ == "__main__":
    main()