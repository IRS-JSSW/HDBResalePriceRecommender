import requests, json
import pandas as pd
from HDBResaleWeb import db
from HDBResaleWeb.models import DataGovTable, PropGuruTable, RailTransitTable, ShoppingMallsTable, HawkerCentreTable, SuperMarketTable
from HDBResaleWeb.addfeatureslib import geographic_position, get_nearest_railtransit, get_nearest_shoppingmall, get_orchard_distance, get_nearest_hawkercentre, get_nearest_supermarket
from sqlalchemy import desc

#Mapping postal sector to postal district
def map_postal_district(postal_sector):
    if postal_sector in ['01', '02', '03', '04', '05', '06']:
        return '01'
    if postal_sector in ['07', '08']:
        return '02'
    if postal_sector in ['14', '15', '16']:
        return '03'
    if postal_sector in ['09', '10']:
        return '04'
    if postal_sector in ['11', '12', '13']:
        return '05'
    if postal_sector in ['17']:
        return '06'
    if postal_sector in ['18', '19']:
        return '07'
    if postal_sector in ['20', '21']:
        return '08'
    if postal_sector in ['22', '23']:
        return '09'
    if postal_sector in ['24', '25', '26', '27']:
        return '10'
    if postal_sector in ['28', '29', '30']:
        return '11'
    if postal_sector in ['31', '32', '33']:
        return '12'
    if postal_sector in ['34', '35', '36', '37']:
        return '13'
    if postal_sector in ['38', '39', '40', '41']:
        return '14'
    if postal_sector in ['42', '43', '44', '45']:
        return '15'
    if postal_sector in ['46', '47', '48']:
        return '16'
    if postal_sector in ['49', '50', '81']:
        return '17'
    if postal_sector in ['51', '52']:
        return '18'
    if postal_sector in ['53', '54', '55', '82']:
        return '19'
    if postal_sector in ['56', '57']:
        return '20'
    if postal_sector in ['58', '59']:
        return '21'
    if postal_sector in ['60', '61', '62', '63', '64']:
        return '22'
    if postal_sector in ['65', '66', '67', '68']:
        return '23'
    if postal_sector in ['69', '70', '71']:
        return '24'
    if postal_sector in ['72', '73']:
        return '25'
    if postal_sector in ['77', '78']:
        return '26'
    if postal_sector in ['75', '76']:
        return '27'
    if postal_sector in ['79', '80']:
        return '28'

#Map storey range to Low/Middle/High
def map_storey_range(storey_range):
    #Storey 6 and below will be low floor
    if storey_range in ['01 TO 03','01 TO 05','04 TO 06']:
        return 'Low'
    #Storey 7 to 10 will be middle floor
    if storey_range in ['07 TO 09','06 TO 10']:
        return 'Middle'
    #Storey 10 and above will be high floor
    if storey_range in ['10 TO 12','11 TO 15','13 TO 15','16 TO 18','16 TO 20',
                        '19 TO 21','21 TO 25','22 TO 24','25 TO 27','28 TO 30',
                        '26 TO 30','31 TO 33','31 TO 35','34 TO 36','36 TO 40',
                        '37 TO 39','40 TO 42','43 TO 45','46 TO 48','49 TO 51']:
        return 'High'

def map_flat_type(flat_type, flat_model):
    if (flat_model == 'Adjoined flat'):
        return "Jumbo"
    if (flat_model == 'Terrace'):
        return "Terrace"
    else:
        return flat_type

def cpi_index():
    filepath = 'HDBResaleWeb/dataset/housing-and-development-board-resale-price-index-1q2009-100-quarterly.csv'
    df = pd.read_csv(filepath)
    df_cpi = pd.DataFrame(columns=['cpi_quarter','cpi_index'])

    for i in range(0,len(df)):
        if (df.iloc[i]['quarter'][:4] >= '2000'):
            insert_row = {
                "cpi_quarter": df.iloc[i]['quarter'],
                "cpi_index": df.iloc[i]['index']
            }
            df_cpi = df_cpi.append(insert_row, ignore_index=True)

    return df_cpi

######################################################################################################
#Retrieve rail transit data from database
def railtransit():
    query_railtransit = RailTransitTable.query.all()
    df_railtransit = pd.DataFrame(columns=['station_name','coordinates'])
    for query_result in query_railtransit:
        insert_row = {
            "station_name": query_result.station_name,
            "coordinates": (query_result.latitude, query_result.longitude)
        }
        df_railtransit = df_railtransit.append(insert_row, ignore_index=True)
    
    return df_railtransit
    # print(df_railtransit.iloc[0])

#Retrieve shopping malls data from database
def shoppingmalls():
    query_shoppingmalls = ShoppingMallsTable.query.all()
    df_shoppingmalls = pd.DataFrame(columns=['Shopping_Malls','coordinates'])
    for query_result in query_shoppingmalls:
        insert_row = {
            "Shopping_Malls": query_result.Shopping_Malls,
            "coordinates": (query_result.latitude, query_result.longitude)
        }
        df_shoppingmalls = df_shoppingmalls.append(insert_row, ignore_index=True)

    return df_shoppingmalls

#Retrieve hawker centre data from database
def hawkercentre():
    query_hawkercentre = HawkerCentreTable.query.all()
    df_hawkercentre = pd.DataFrame(columns=['name_of_centre','coordinates'])
    for query_result in query_hawkercentre:
        insert_row = {
            "name_of_centre": query_result.name_of_centre,
            "coordinates": (query_result.latitude, query_result.longitude)
        }
        df_hawkercentre = df_hawkercentre.append(insert_row, ignore_index=True)

    return df_hawkercentre

#Retrieve supermarket data from database
def supermarket():
    query_supermarket = SuperMarketTable.query.all()
    df_supermarket = pd.DataFrame(columns=['licensee_name','coordinates'])
    for query_result in query_supermarket:
        insert_row = {
            "licensee_name": query_result.licensee_name,
            "coordinates": (query_result.latitude, query_result.longitude)
        }
        df_supermarket = df_supermarket.append(insert_row, ignore_index=True)

    return df_supermarket

######################################################################################################
#Copy transit rails data from csv to database
def insert_railtransit_data():
    filepath = 'HDBResaleWeb/dataset/mrtlrt_coord.csv'
    df = pd.read_csv(filepath)
    for i in range(0, len(df)):
        update = RailTransitTable(
            station_name = df.iloc[i]['station_name'],
            rail_type = df.iloc[i]['type'],
            latitude = df.iloc[i]['latitude'],
            longitude = df.iloc[i]['longitude']
        )
        db.session.add(update)
        db.session.commit()

#Copy shopping malls data from csv to database
def insert_shoppingmalls_data():
    filepath = 'HDBResaleWeb/dataset/malls_final.csv'
    df = pd.read_csv(filepath)
    for i in range(0, len(df)):
        update = ShoppingMallsTable(
            Shopping_Malls = df.iloc[i]['Shopping_Malls'],
            latitude = df.iloc[i]['latitude'],
            longitude = df.iloc[i]['longitude'],
            full_address = df.iloc[i]['full_address']
        )
        db.session.add(update)
        db.session.commit()

#Copy hawker centre data from csv to database
def insert_hawkercentre_data():
    filepath = 'HDBResaleWeb/dataset/hawkers.csv'
    df = pd.read_csv(filepath)
    for i in range(0, len(df)):
        update = HawkerCentreTable(
            name_of_centre = df.iloc[i]['name_of_centre'],
            type_of_centre = df.iloc[i]['type_of_centre'],
            owner = df.iloc[i]['owner'],
            no_of_stalls = int(df.iloc[i]['no_of_stalls']),
            no_of_cooked_food_stalls = int(df.iloc[i]['no_of_cooked_food_stalls']),
            no_of_mkt_produce_stalls = int(df.iloc[i]['no_of_mkt_produce_stalls']),
            postal_code = int(df.iloc[i]['postal_code']),
            latitude = df.iloc[i]['latitude'],
            longitude = df.iloc[i]['longitude'],
            full_address = df.iloc[i]['full_address']
        )
        db.session.add(update)
        db.session.commit()

#Copy supermarket data from csv to database
def insert_supermarket_data():
    filepath = 'HDBResaleWeb/dataset/markets.csv'
    df = pd.read_csv(filepath)
    for i in range(0, len(df)):
        update = SuperMarketTable(
            licensee_name = df.iloc[i]['licensee_name'],
            postal_code = int(df.iloc[i]['postal_code']),
            latitude = df.iloc[i]['latitude'],
            longitude = df.iloc[i]['longitude'],
            full_address = df.iloc[i]['full_address']
        )
        db.session.add(update)
        db.session.commit()

#Copy propguru data from csv to database
def insert_propguru_data():
    filepath = 'HDBResaleWeb/dataset/propguru.csv'
    df = pd.read_csv(filepath)
    for i in range(0, len(df)):
        update = PropGuruTable(
            licensee_name = df.iloc[i]['licensee_name'],
            postal_code = int(df.iloc[i]['postal_code']),
            latitude = df.iloc[i]['latitude'],
            longitude = df.iloc[i]['longitude'],
            full_address = df.iloc[i]['full_address']
        )
        db.session.add(update)
        db.session.commit()

######################################################################################################
#Function to update HDB resale data from data gov
def update_datagov_table():
    url_2017 = 'https://data.gov.sg/api/action/datastore_search?resource_id=42ff9cfe-abe5-4b54-beda-c88f9bb438ee&limit=500000'
    # url_2015 = 'https://data.gov.sg/api/action/datastore_search?resource_id=1b702208-44bf-4829-b620-4615ee19b57c&limit=500000'
    #Data before 2015 does not have the 'remaining_lease' column and data
    # url_2012 = 'https://data.gov.sg/api/action/datastore_search?resource_id=83b2fc37-ce8c-4df4-968b-370fd818138b&limit=500000'
    # url_2000 = 'https://data.gov.sg/api/action/datastore_search?resource_id=8c00bf08-9124-479e-aeca-7cc411d884c4&limit=400000'
    data = json.loads(requests.get(url_2017).content)

    df = pd.DataFrame(data['result']['records'])
    
    update_month = pd.to_datetime("2021-04")

    df2 = df[df['month'] == "2017-01"]
    df2 = df2.reset_index()

    df_railtransit = railtransit()
    df_shoppingmalls = shoppingmalls()
    df_hawkercentre = hawkercentre()
    df_supermarket = supermarket()
    df_cpi_index = cpi_index()

    for i in range(0, len(df2)):
        if pd.to_datetime(df2.iloc[i]['month']) <= update_month:
            record_date = df2.iloc[i]['month']
            record_month = pd.to_datetime(record_date)
            record_quarter = record_date[:4] + "-Q" + str(record_month.quarter)
            resale_price = df2.iloc[i]['resale_price']
            flat_type = map_flat_type(df2.iloc[i]['flat_type'], df2.iloc[i]['flat_model'])
            storey_range = map_storey_range(df2.iloc[i]['storey_range'])
            remaining_lease = 99 - int(df2.iloc[i]['month'][:4]) + int(df2.iloc[i]['lease_commence_date'])
            cpi_adjusted_resale_price = float(resale_price) / float(df_cpi_index[df_cpi_index['cpi_quarter']==record_quarter]['cpi_index']) * 100
            full_address = df2.iloc[i]['block'] + ' ' + df2.iloc[i]['street_name']
            onemap_postal_sector, onemap_latitude, onemap_longitude = geographic_position(full_address)
            #If latitude and longitude is found
            if (onemap_latitude != 0):
                mrt_nearest, mrt_distance = get_nearest_railtransit(onemap_latitude, onemap_longitude, df_railtransit)
                mall_nearest, mall_distance = get_nearest_shoppingmall(onemap_latitude, onemap_longitude, df_shoppingmalls)
                orchard_distance = get_orchard_distance(onemap_latitude, onemap_longitude)
                hawker_distance = get_nearest_hawkercentre(onemap_latitude, onemap_longitude, df_hawkercentre)
                market_distance = get_nearest_supermarket(onemap_latitude, onemap_longitude, df_supermarket)
            #If latitude and longitude is not found, fill with null values
            if (onemap_latitude == 0):
                mrt_nearest = "null"
                mrt_distance = 0
                mall_nearest = "null"
                mall_distance = 0
                orchard_distance = 0
                hawker_distance = 0
                market_distance = 0
            #Create array to add new record from datagov into database
            update = DataGovTable(
            #Raw features from datagov
                month = record_month,
                # town = df2.iloc[i]['town'],
                flat_type = flat_type,
                # block = df2.iloc[i]['block'],
                # street_name = df2.iloc[i]['street_name'],
                storey_range = storey_range,
                floor_area_sqm = df2.iloc[i]['floor_area_sqm'],
                # lease_commence_date = df2.iloc[i]['lease_commence_date'],
                remaining_lease = remaining_lease,
                resale_price = resale_price,
            #Additional features added          
                cpi_adjusted_resale_price = cpi_adjusted_resale_price,
                latitude = onemap_latitude,
                longitude = onemap_longitude,
                postal_district = map_postal_district(onemap_postal_sector),
                mrt_nearest = mrt_nearest,
                mrt_distance = mrt_distance,
                mall_nearest = mall_nearest,
                mall_distance = mall_distance,
                orchard_distance = orchard_distance,
                hawker_distance = hawker_distance,
                market_distance = market_distance
            )

            #Add and commit the record to database
            db.session.add(update)
            db.session.commit()

######################################################################################################
#Function to update propguru data
def update_propguru_table():
    # url = 'https://www.propertyguru.com.sg/property-for-sale?property_type=H&order=desc'
    # results = requests.get(url)
    print("Building this function...")

######################################################################################################
###1. Preprocess datagov dataset for building price prediction model###
def train_regression_model():
#Query database and import relevant features into dataframe
    query_datagov = DataGovTable.query.all()
    df_datagov = pd.DataFrame(columns=["month","flat_type","storey_range","floor_area_sqm","remaining_lease",
                                        "resale_price","latitude","longitude","postal_district","mrt_distance",
                                        "mall_distance","orchard_distance","hawker_distance","market_distance"])
    for query_result in query_datagov:
        get_result = {
            "month": query_result.month,
            "flat_type": query_result.flat_type,
            "storey_range": query_result.storey_range,
            "floor_area_sqm": query_result.floor_area_sqm,
            "remaining_lease": query_result.remaining_lease,
            "resale_price": query_result.resale_price,
            "latitude": query_result.latitude,
            "longitude": query_result.longitude,
            "postal_district": query_result.postal_district,
            "mrt_distance": query_result.mrt_distance,
            "mall_distance": query_result.mall_distance,
            "orchard_distance": query_result.orchard_distance,
            "hawker_distance": query_result.hawker_distance,
            "market_distance": query_result.market_distance
        }
        df_datagov = df_datagov.append(get_result, ignore_index=True)

#Choose target


#Onehot Encoding


###2. Build Regression Model###

#Split the dataset into training and test set
# X_train, X_test, y_train, y_test = train_test_split(X, Y_regression, test_size=1 / 3, random_state=42)

#Build Regression Tree
# dt = DecisionTreeRegressor(criterion='mse',random_state=0)
# dt.fit(X_train, y_train)

#Optimise parameters using grid search
# best_para = {'max_depth':0, 'min_samples':0}
# best_test_acc = 0
# # grid search
# for max_depth in range(1, 20):
#     for min_samples in range(2,50):
#         dt = DecisionTreeRegressor(criterion='mse',max_depth=max_depth, min_samples_split = min_samples, random_state=0)
#         dt.fit(X_train, y_train)
#         if dt.score(X_test, y_test) > best_test_acc:
#             best_test_acc = dt.score(X_test, y_test)
#             best_para['max_depth'] = max_depth
#             best_para['min_samples'] = min_samples

# dt = DecisionTreeRegressor(criterion='mse',max_depth=best_para['max_depth'], min_samples_split = best_para['min_samples'], random_state=0)
# dt.fit(X_train, y_train)
# print("Best score on training set: {:.3f}".format(dt.score(X_train, y_train)))
# print("Best score on test set: {:.3f}".format(dt.score(X_test, y_test)))
# print("Best regression tree with parameter max_depth of {0} and min_samples_split of {1}".format(best_para['max_depth'], best_para['min_samples']))

######################################################################################################
###Loading Regression Model###
# def load_regression_model():
# abc