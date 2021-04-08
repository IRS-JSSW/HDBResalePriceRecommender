import requests, json
import pandas as pd
from HDBResaleWeb import db
from HDBResaleWeb.models import DataGovTable, PropGuruTable, RailTransitTable, ShoppingMallsTable, HawkerCentreTable, SuperMarketTable
from HDBResaleWeb.addfeatureslib import geographic_position, get_nearest_railtransit, get_nearest_shoppingmall, get_cbd_distance, get_nearest_hawkercentre, get_nearest_supermarket
from sqlalchemy import desc

#Mapping postal sector to postal district
def postal_district(postal_sector):
    if postal_sector in ['01', '02', '03', '04', '05', '06']:
        return '01'
    elif postal_sector in ['07', '08']:
        return '02'
    elif postal_sector in ['14', '15', '16']:
        return '03'
    elif postal_sector in ['09', '10']:
        return '04'
    elif postal_sector in ['11', '12', '13']:
        return '05'
    elif postal_sector in ['17']:
        return '06'
    elif postal_sector in ['18', '19']:
        return '07'
    elif postal_sector in ['20', '21']:
        return '08'
    elif postal_sector in ['22', '23']:
        return '09'
    elif postal_sector in ['24', '25', '26', '27']:
        return '10'
    elif postal_sector in ['28', '29', '30']:
        return '11'
    elif postal_sector in ['31', '32', '33']:
        return '12'
    elif postal_sector in ['34', '35', '36', '37']:
        return '13'
    elif postal_sector in ['38', '39', '40', '41']:
        return '14'
    elif postal_sector in ['42', '43', '44', '45']:
        return '15'
    elif postal_sector in ['46', '47', '48']:
        return '16'
    elif postal_sector in ['49', '50', '81']:
        return '17'
    elif postal_sector in ['51', '52']:
        return '18'
    elif postal_sector in ['53', '54', '55', '82']:
        return '19'
    elif postal_sector in ['56', '57']:
        return '20'
    elif postal_sector in ['58', '59']:
        return '21'
    elif postal_sector in ['60', '61', '62', '63', '64']:
        return '22'
    elif postal_sector in ['65', '66', '67', '68']:
        return '23'
    elif postal_sector in ['69', '70', '71']:
        return '24'
    elif postal_sector in ['72', '73']:
        return '25'
    elif postal_sector in ['77', '78']:
        return '26'
    elif postal_sector in ['75', '76']:
        return '27'
    elif postal_sector in ['79', '79']:
        return '28'

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
            "Shopping_Malls": query_result.name_of_centre,
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
            "Shopping_Malls": query_result.licensee_name,
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

######################################################################################################
#Function to update HDB resale data from data gov
def update_datagov_table():
    url_2017 = 'https://data.gov.sg/api/action/datastore_search?resource_id=42ff9cfe-abe5-4b54-beda-c88f9bb438ee&limit=100'
    url_2015 = 'https://data.gov.sg/api/action/datastore_search?resource_id=1b702208-44bf-4829-b620-4615ee19b57c&limit=10'
    #Data before 2015 does not have the 'remaining_lease' column and data
    # url_2012 = 'https://data.gov.sg/api/action/datastore_search?resource_id=83b2fc37-ce8c-4df4-968b-370fd818138b&limit=5'
    # url_2000 = 'https://data.gov.sg/api/action/datastore_search?resource_id=8c00bf08-9124-479e-aeca-7cc411d884c4&limit=5'
    data = json.loads(requests.get(url_2015).content)

    df = pd.DataFrame(data['result']['records'])
    # total = data['result']['total']
    
    # query_datagov = DataGovTable.query.order_by(DataGovTable.id.desc()).all()
    # df_datagov = pd.DataFrame(columns=['month','result','block','street_name'])
    # for query_result in query_datagov:
    #     df_datagov = df_datagov.append([query_result.month, query_result.town, query_result.block, query_result.street_name])
    # latest_month = pd.to_datetime(last_record.month)
    update_month = pd.to_datetime("2017-12")

    df_railtransit = railtransit()
    df_shoppingmalls = shoppingmalls()
    df_hawkercentre = hawkercentre()
    df_supermarket = supermarket()

    for i in range(0, len(df)):
        if pd.to_datetime(df.iloc[i]['month']) <= update_month:
            full_address = df.iloc[i]['block'] + ' ' + df.iloc[i]['street_name']
            onemap_postal_sector, onemap_latitude, onemap_longitude = geographic_position(full_address)
            mrt_nearest, mrt_distance = get_nearest_railtransit(onemap_latitude, onemap_longitude, df_railtransit)
            mall_nearest, mall_distance = get_nearest_shoppingmall(onemap_latitude, onemap_longitude, df_shoppingmalls)
            cbd_distance = get_cbd_distance(onemap_latitude, onemap_longitude)
            hawker_distance = get_nearest_hawkercentre(onemap_latitude, onemap_longitude, df_hawkercentre)
            market_distance = get_nearest_supermarket(onemap_latitude, onemap_longitude, df_supermarket)
            update = DataGovTable(
            #Raw features from datagov
                month = pd.to_datetime(df.iloc[i]['month']),
                town = df.iloc[i]['town'],
                flat_type = df.iloc[i]['flat_type'],
                block = df.iloc[i]['block'],
                street_name = df.iloc[i]['street_name'],
                storey_range = df.iloc[i]['storey_range'],
                floor_area_sqm = df.iloc[i]['floor_area_sqm'],
                flat_model = df.iloc[i]['flat_model'],
                lease_commence_date = df.iloc[i]['lease_commence_date'],
                remaining_lease = df.iloc[i]['remaining_lease'][:2],
                resale_price = df.iloc[i]['resale_price'],
            #Additional features added          
                latitude = onemap_latitude,
                longitude = onemap_longitude,
                postal_district = postal_district(onemap_postal_sector),
                mrt_nearest = mrt_nearest,
                mrt_distance = mrt_distance,
                mall_nearest = mall_nearest,
                mall_distance = mall_distance,
                cbd_distance = cbd_distance,
                hawker_distance = hawker_distance,
                market_distance = market_distance
            )
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

#Import data from database

#Choose appropriate features

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
