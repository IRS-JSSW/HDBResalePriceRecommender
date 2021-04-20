import requests, json, joblib
import pandas as pd, numpy as np
from datetime import datetime
from HDBResaleWeb.addfeatureslib import geographic_position, get_nearest_railtransit, get_nearest_shoppingmall, get_orchard_distance, get_nearest_hawkercentre, get_nearest_supermarket
from sqlalchemy import create_engine, desc
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error

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
    #Storey 13 and above, return "13 and above"
    if storey_range in ['13 TO 15','16 TO 18','16 TO 20',
                        '19 TO 21','21 TO 25','22 TO 24','25 TO 27','28 TO 30',
                        '26 TO 30','31 TO 33','31 TO 35','34 TO 36','36 TO 40',
                        '37 TO 39','40 TO 42','43 TO 45','46 TO 48','49 TO 51']:
        return '13 and above'
    else: 
        return storey_range

def map_flat_type(flat_type, flat_model):
    if (flat_model == 'Adjoined flat'):
        return "Jumbo"
    if (flat_model == 'Terrace'):
        return "Terrace"
    else:
        return flat_type

def cpi_index():
    url_cpi = 'https://data.gov.sg/api/action/datastore_search?resource_id=52e93430-01b7-4de0-80df-bc83d0afed40&limit=50000'
    data = json.loads(requests.get(url_cpi).content)

    df = pd.DataFrame(data['result']['records'])

    df_cpi = pd.DataFrame(columns=['cpi_quarter','cpi_index'])

    for i in range(0,len(df)):
        if (df.iloc[i]['quarter'][:4] >= '2000'):
            insert_row = {
                "cpi_quarter": df.iloc[i]['quarter'],
                "cpi_index": df.iloc[i]['index']
            }
            df_cpi = df_cpi.append(insert_row, ignore_index=True)

    # #If current quarter not in list, get average CPI of previous 3 months
    # datagov_latest_quarter = str(datagov_latest_month.year) + "-Q" + str(datagov_latest_month.quarter)
    # latest_hdb_cpi_quarter = str(df_cpi['cpi_quarter'][-1:])
    # if (datagov_latest_quarter != latest_hdb_cpi_quarter):
    #     # average_cpi_3months = round(sum(list(map(float, df_cpi['cpi_index'][-3:]))) / 3, 2)
    #     cpi_index = df_cpi.iloc[-1]['cpi_index']
    #     df_cpi = df_cpi.append({"cpi_quarter":datagov_latest_quarter, "cpi_index":cpi_index}, ignore_index=True)

    return df_cpi

######################################################################################################
#Retrieve rail transit data from database
def railtransit():
    #Connect to database
    engine = create_engine("sqlite:///HDBResaleWeb/resaleproject.db")

    #Query database
    query = "SELECT * FROM rail_transit_table"

    #SQL to pandas df
    df = pd.read_sql_query(query, engine)
    
    df_railtransit = df[['station_name','latitude','longitude']]
    df_railtransit.insert(len(df_railtransit.columns), 'coordinates', list(zip(df['latitude'],df['longitude'])))
    df_railtransit = df_railtransit[['station_name','coordinates']]

    # print(df_railtransit.head(10))
    return df_railtransit

#Retrieve shopping malls data from database
def shoppingmalls():
    #Connect to database
    engine = create_engine("sqlite:///HDBResaleWeb/resaleproject.db")

    #Query database
    query = "SELECT * FROM shopping_malls_table"

    #SQL to pandas df
    df = pd.read_sql_query(query, engine)
    
    df_shoppingmalls = df[['Shopping_Malls','latitude','longitude']]
    df_shoppingmalls.insert(len(df_shoppingmalls.columns), 'coordinates', list(zip(df['latitude'],df['longitude'])))
    df_shoppingmalls = df_shoppingmalls[['Shopping_Malls','coordinates']]

    return df_shoppingmalls

#Retrieve hawker centre data from database
def hawkercentre():
    #Connect to database
    engine = create_engine("sqlite:///HDBResaleWeb/resaleproject.db")

    #Query database
    query = "SELECT * FROM hawker_centre_table"

    #SQL to pandas df
    df = pd.read_sql_query(query, engine)
    
    df_hawkercentre = df[['name_of_centre','latitude','longitude']]
    df_hawkercentre.insert(len(df_hawkercentre.columns), 'coordinates', list(zip(df['latitude'],df['longitude'])))
    df_hawkercentre = df_hawkercentre[['name_of_centre','coordinates']]

    return df_hawkercentre

#Retrieve supermarket data from database
def supermarket():
    #Connect to database
    engine = create_engine("sqlite:///HDBResaleWeb/resaleproject.db")

    #Query database
    query = "SELECT * FROM super_market_table"

    #SQL to pandas df
    df = pd.read_sql_query(query, engine)
    
    df_supermarket = df[['licensee_name','latitude','longitude']]
    df_supermarket.insert(len(df_supermarket.columns), 'coordinates', list(zip(df['latitude'],df['longitude'])))
    df_supermarket = df_supermarket[['licensee_name','coordinates']]

    return df_supermarket

######################################################################################################
#Copy transit rails data from csv to database
def insert_railtransit_data():
    filepath = 'HDBResaleWeb/dataset/mrtlrt_coord.csv'
    df = pd.read_csv(filepath)
    #Rename column "type" to "rail_type"
    df = df.rename(columns={"type": "rail_type"})

    #Connect to database
    engine = create_engine("sqlite:///HDBResaleWeb/resaleproject.db")

    #Insert dataframe into sqlite database
    df.to_sql('rail_transit_table', con=engine, if_exists='append', index=False)

#Copy shopping malls data from csv to database
def insert_shoppingmalls_data():
    filepath = 'HDBResaleWeb/dataset/malls_final.csv'
    df = pd.read_csv(filepath)

    #Connect to database
    engine = create_engine("sqlite:///HDBResaleWeb/resaleproject.db")

    #Insert dataframe into sqlite database
    df.to_sql('shopping_malls_table', con=engine, if_exists='append', index=False)

#Copy hawker centre data from csv to database
def insert_hawkercentre_data():
    filepath = 'HDBResaleWeb/dataset/hawkers.csv'
    df = pd.read_csv(filepath)

    #Connect to database
    engine = create_engine("sqlite:///HDBResaleWeb/resaleproject.db")

    #Insert dataframe into sqlite database
    df.to_sql('hawker_centre_table', con=engine, if_exists='append', index=False)

#Copy supermarket data from csv to database
def insert_supermarket_data():
    filepath = 'HDBResaleWeb/dataset/markets.csv'
    df = pd.read_csv(filepath)

    #Connect to database
    engine = create_engine("sqlite:///HDBResaleWeb/resaleproject.db")

    #Insert dataframe into sqlite database
    df.to_sql('super_market_table', con=engine, if_exists='append', index=False)


######################################################################################################
#Function to update HDB resale data from data gov
def update_datagov_table():
    url_2017 = 'https://data.gov.sg/api/action/datastore_search?resource_id=42ff9cfe-abe5-4b54-beda-c88f9bb438ee&limit=500000'
    # url_2015 = 'https://data.gov.sg/api/action/datastore_search?resource_id=1b702208-44bf-4829-b620-4615ee19b57c&limit=500000'
    data = json.loads(requests.get(url_2017).content)

    df = pd.DataFrame(data['result']['records'])
    #Get the list of unique year and month of datagov records
    df_month = list(set(df['month']))
    df_month = sorted(pd.to_datetime(df_month))
    df['yearmonth'] = pd.to_datetime(df['month'])
    # print(df['yearmonths'])

    #Retrieve amenities data and CPI index
    df_railtransit = railtransit()
    df_shoppingmalls = shoppingmalls()
    df_hawkercentre = hawkercentre()
    df_supermarket = supermarket()
    df_cpi_index = cpi_index()
    
    #Check the last HDB resale CPI quarter e.g 2020-Q4
    # latest_cpi_quarter = str(df_cpi_index.iloc[-1]['cpi_quarter'])
    latest_cpi_quarter = "2020-Q4"
    #Replace quarter as the last month in the quarter e.g Q1 to 03, Q2 to 06, Q3 to 09, Q4 to 12
    latest_cpi_quarter = latest_cpi_quarter.replace('Q1','03').replace('Q2','06').replace('Q3','09').replace('Q4','12')
    latest_cpi_quarter = pd.to_datetime(latest_cpi_quarter)
    # print(latest_cpi_quarter)

    #Connect to database
    engine = create_engine("sqlite:///HDBResaleWeb/resaleproject.db")

    #Get the year and month of the last record in data gov table from database
    query_lastrecord = "SELECT * FROM data_gov_table ORDER BY id DESC LIMIT 1"
    df_datagov_query = pd.read_sql_query(query_lastrecord, engine)
    query_lastrecord_month = pd.to_datetime(df_datagov_query['month'])[0] if len(df_datagov_query) != 0 else pd.to_datetime("2014-12")
    # print(query_lastrecord_month)

    #Get the list of year and month that is not updated in the database
    update_month = []
    for month in df_month:
        if (month > query_lastrecord_month) and (month <= latest_cpi_quarter):
            update_month.append(month)
    print(update_month)

    df2 = df[(df['yearmonth'].isin(update_month))]
    df2 = df2.reset_index()
    # print(len(df2))

    df_insert = pd.DataFrame(columns=["month","flat_type","storey_range","floor_area_sqm","remaining_lease","resale_price",
                "cpi_adjusted_resale_price","latitude","longitude","postal_district","mrt_nearest","mrt_distance",
                "mall_nearest","mall_distance","orchard_distance","hawker_distance","market_distance"])

    #If records to update more than 0
    if(len(df2) > 0):
        #Loop through the records to update
        for i in range(0, len(df2)):
            #Map the flat type
            flat_type = map_flat_type(df2.iloc[i]['flat_type'], df2.iloc[i]['flat_model'])
            #Map the storey range
            storey_range = map_storey_range(df2.iloc[i]['storey_range'])
            #Calculate remaining lease
            remaining_lease = 99 - int(df2.iloc[i]['month'][:4]) + int(df2.iloc[i]['lease_commence_date'])
            #Calculate resale_price adjusted for HDB resale CPI
            resale_price = df2.iloc[i]['resale_price']
            record_date = df2.iloc[i]['month']
            record_month = pd.to_datetime(record_date)
            record_quarter = record_date[:4] + "-Q" + str(record_month.quarter)
            cpi_adjusted_resale_price = float(resale_price) / float(df_cpi_index[df_cpi_index['cpi_quarter']==record_quarter]['cpi_index']) * 100
            #Get the full address of the record to retrieve the latitude, longitude and postal sector from Onemap or Google
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
            df_insert = df_insert.append({
                "month": record_month.date(),
                "flat_type": flat_type,
                "storey_range": storey_range,
                "floor_area_sqm": float(df2.iloc[i]['floor_area_sqm']),
                "remaining_lease": int(remaining_lease),
                "resale_price": float(resale_price),
                "cpi_adjusted_resale_price": cpi_adjusted_resale_price,
                "latitude": float(onemap_latitude),
                "longitude": float(onemap_longitude),
                "postal_district": int(map_postal_district(onemap_postal_sector)),
                "mrt_nearest": mrt_nearest,
                "mrt_distance": mrt_distance,
                "mall_nearest": mall_nearest,
                "mall_distance": mall_distance,
                "orchard_distance": orchard_distance,
                "hawker_distance": hawker_distance,
                "market_distance": market_distance
            }, ignore_index=True)

    # print(df_insert.dtypes)
    #Insert dataframe into sqlite database
    df_insert.to_sql('data_gov_table', con=engine, if_exists='append', index=False)


######################################################################################################
def train_regression_model():
    #Connect to database
    engine = create_engine("sqlite:///HDBResaleWeb/resaleproject.db")

    #Query database and import relevant features into dataframe
    query = "SELECT * FROM data_gov_table"

    #SQL to pandas df
    df = pd.read_sql_query(query, engine)
    
    df_datagov = df[["month","flat_type","storey_range","floor_area_sqm","remaining_lease",
                    "cpi_adjusted_resale_price","latitude","longitude","postal_district","mrt_distance",
                    "mall_distance","orchard_distance","hawker_distance","market_distance"]]

    ###1. Remove outliers from dataset###
    df_datagov2 = df_datagov[(df_datagov['floor_area_sqm'] <= 215) & (df_datagov['mrt_distance'] <= 2.5)]
    df_datagov2 = df_datagov2.reset_index()

    #Choose target
    X = df_datagov2.drop(columns=['index','cpi_adjusted_resale_price','flat_type'], axis=1)
    y = np.log1p(df_datagov2['cpi_adjusted_resale_price'])

    ####2. Onehot Encoding####
    #Encode month e.g month 1 is 2015-01-01, month 71 is 2020-12-01
    X['month'] = pd.Categorical(X['month']).codes
    #Encode storey range
    X['storey_range'] = pd.Categorical(X['storey_range']).codes

    #Encode flat type and postal district
    categorical_features = ['postal_district']
    for feature in categorical_features:
        X = pd.concat([X, pd.get_dummies(X[feature], prefix=feature)], axis=1)
    X = X.drop(columns=categorical_features, axis=1)


    ###Build Regression Model###

    #3. Split the dataset into training and test set
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=1 / 5, random_state=42)

    #4. Select Regression Tree model, Best regression tree with parameter max_depth of 18 and min_samples_split of 24
    model = DecisionTreeRegressor(criterion='mse', max_depth=18, min_samples_split = 24, random_state=0)
    # model = GradientBoostingRegressor(criterion='mse', max_depth=8, min_samples_split = 24, learning_rate=0.01, random_state=0)
    model.fit(X_train, y_train)

    #Get top 10 features sorted in descending order
    for importance, name in sorted(zip(model.feature_importances_, X_train.columns),reverse=True)[:10]:
        print (name, importance)

    X_test.to_csv("test_data.csv", index = False)

    #Get RMSE score for predicting test set
    y_pred = np.log1p(model.predict(X_test))
    rmse = np.exp(mean_squared_error(y_test, y_pred, squared=False)).round(4)

    print("RMSE: {0}".format(rmse))

    #5. Save Regression Tree model
    filename = 'hdb_resale_model.joblib'
    joblib.dump(model, filename)

    #Optimise parameters using grid search
    # best_para = {'max_depth':0, 'min_samples':0}
    # best_test_acc = 0
    # # grid search
    # for max_depth in range(1, 20):
    #     for min_samples in range(2,30):
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
def load_regression_model(search_df):
    filename = "hdb_resale_model.joblib"
    loaded_model = joblib.load(filename)

    #Count number of months since 2015-01-01
    start = pd.to_datetime('2015-01-01')
    current = pd.to_datetime('today')
    months = (current.year - start.year) * 12 + (current.month - start.month)
    print(months)

    #Predict price for low, middle and high floors
    df_predict_low = [[75,0,67.0,59,1.31207968902337,103.760802118745,0.5955574900450702,0.4623104220664519,8.013058559461447,0.11629349454113441,0.18709338677006054,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]]
    df_predict_middle = [[75,1,67.0,59,1.31207968902337,103.760802118745,0.5955574900450702,0.4623104220664519,8.013058559461447,0.11629349454113441,0.18709338677006054,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]]
    df_predict_high = [[75,2,67.0,59,1.31207968902337,103.760802118745,0.5955574900450702,0.4623104220664519,8.013058559461447,0.11629349454113441,0.18709338677006054,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]]


    #Return predicted price for low, middle and high floors
    predict_low = np.exp(loaded_model.predict(df_predict_low))[0]
    predict_middle = np.exp(loaded_model.predict(df_predict_middle))[0].round()
    predict_high = np.exp(loaded_model.predict(df_predict_high))[0].round()

    #Adjust predicted price for HDB CPI index based on weighted average of past 3 quarters CPI
    df_cpi_index = cpi_index()
    # average_cpi_3months = round(sum(list(map(float, df_cpi_index['cpi_index'][-3:]))) / 3, 2)
    latest_cpi_3months = (float(df_cpi_index.iloc[-1]['cpi_index'])*0.7) + (float(df_cpi_index.iloc[-2]['cpi_index'])*0.2) + (float(df_cpi_index.iloc[-3]['cpi_index'])*0.1)
    print(latest_cpi_3months)

    predict_low_cpi = (predict_low * latest_cpi_3months / 100).round(0)
    predict_middle_cpi = (predict_middle * latest_cpi_3months / 100).round(0)
    predict_high_cpi = (predict_high * latest_cpi_3months / 100).round(0)

    return predict_low_cpi, predict_middle_cpi, predict_high_cpi
