import requests, json, joblib
import pandas as pd, numpy as np
from datetime import datetime
from HDBResaleWeb.addfeatureslib import geographic_position, get_nearest_railtransit, get_nearest_shoppingmall, get_orchard_distance, get_nearest_hawkercentre, get_nearest_supermarket
from sqlalchemy import create_engine, desc
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import KFold,GridSearchCV,train_test_split
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

    #Drop irrelevant features
    X = df_datagov2.drop(columns=['index','cpi_adjusted_resale_price','flat_type'], axis=1)
    #Normalise the values of floor area
    X["floor_area_sqm"] = np.log(X["floor_area_sqm"])
    #Normalise the values of target
    y = np.log(df_datagov2['cpi_adjusted_resale_price'])

    ####2. Onehot Encoding####
    #Encode month e.g month 1 is 2015-01-01, month 71 is 2020-12-01
    X['month'] = pd.Categorical(X['month']).codes
    #Encode storey range
    X['storey_range'] = pd.Categorical(X['storey_range']).codes


    #Custom encode postal district 1 to 28 and drop the column
    categorical_features = ['postal_district']
    postal_districts = pd.DataFrame(0, index=np.arange(len(X)), columns=['postal_district_1','postal_district_2','postal_district_3','postal_district_4','postal_district_5',
                        'postal_district_6','postal_district_7','postal_district_8','postal_district_9','postal_district_10',
                        'postal_district_11','postal_district_12','postal_district_13','postal_district_14','postal_district_15',
                        'postal_district_16','postal_district_17','postal_district_18','postal_district_19','postal_district_20',
                        'postal_district_21','postal_district_22','postal_district_23','postal_district_24','postal_district_25',
                        'postal_district_26','postal_district_27','postal_district_28'])
    X = pd.concat([X, postal_districts], axis=1)

    for i in range(1,29):
        column_index = i + 11
        X.iloc[(X['postal_district'] == i), [column_index]] = 1

    X = X.drop(columns=categorical_features, axis=1)

    ###Build Regression Model###

    #3. Split the dataset into training and test set
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    #4. Select Gradient Boosting Regression model, parameter n_estimators of 400
    scaler = StandardScaler().fit(X_train)
    rescaled_X_train = scaler.transform(X_train)
    model = GradientBoostingRegressor(random_state=21, n_estimators=400)
    model.fit(rescaled_X_train, y_train)

    #Transform the validation dataset
    rescaled_X_test = scaler.transform(X_test)
    predictions = model.predict(rescaled_X_test)

    #Get top 10 features sorted in descending order
    for importance, name in sorted(zip(model.feature_importances_, X_train.columns),reverse=True)[:10]:
        print(name, importance)

    #Get RMSE score for predicting test set
    actual_y_test = np.exp(y_test)
    actual_predicted = np.exp(predictions)
    diff = abs(actual_y_test - actual_predicted)

    compare_actual = pd.DataFrame({'Test Data': actual_y_test, 'Predicted Price' : actual_predicted, 'Difference' : diff})
    compare_actual = compare_actual.astype(int)
    print(compare_actual.head(5))
    rmse = round(mean_squared_error(actual_y_test, actual_predicted, squared=False), 4)

    print("RMSE: {0}".format(rmse))

    # #5. Save Regression Tree model and scaler
    model_filename = 'hdb_resale_model.joblib'
    joblib.dump(model, model_filename)
    scaler_filename = 'hdb_resale_scaler.joblib'
    joblib.dump(scaler, scaler_filename)

    #Optimise parameters using grid search for GradientBoostingRegressor
    # scaler = StandardScaler().fit(X_train)
    # rescaledX = scaler.transform(X_train)
    # param_grid = dict(n_estimators=np.array([50,100,200,300,400]))
    # model = GradientBoostingRegressor(random_state=21)
    # kfold = KFold(n_splits=10, random_state=21, shuffle=True)
    # grid = GridSearchCV(estimator=model, param_grid=param_grid, scoring='neg_mean_squared_error', cv=kfold)
    # grid_result = grid.fit(rescaledX, y_train)

    # means = grid_result.cv_results_['mean_test_score']
    # stds = grid_result.cv_results_['std_test_score']
    # params = grid_result.cv_results_['params']
    # for mean, stdev, param in zip(means, stds, params):
    #     print("%f (%f) with: %r" % (mean, stdev, param))

    # print("Best: %f using %s" % (grid_result.best_score_, grid_result.best_params_))

######################################################################################################
###Loading Regression Model###
def load_regression_model(search_df):
    model_filename = "hdb_resale_model.joblib"
    loaded_model = joblib.load(model_filename)
    scaler_filename = "hdb_resale_scaler.joblib"
    loaded_scaler = joblib.load(scaler_filename)

    #Count number of months since 2015-01-01
    start = pd.to_datetime('2015-01-01')
    current = pd.to_datetime('today')
    months = (current.year - start.year) * 12 + (current.month - start.month)
    # print(months)

    #Retrieve amenities data and CPI index
    df_railtransit = railtransit()
    df_shoppingmalls = shoppingmalls()
    df_hawkercentre = hawkercentre()
    df_supermarket = supermarket()
    df_cpi_index = cpi_index()

    #Get coordinates and postal sector using address
    full_address = search_df.get('StreetAdd') + " Singapore"
    onemap_postal_sector, onemap_latitude, onemap_longitude = geographic_position(full_address)
    postal_district = int(map_postal_district(onemap_postal_sector))
    floor_area_sqm = np.log(float(search_df.get('FloorArea')))
    remaining_lease = int(search_df.get('RemainingLease'))
    latitude = float(onemap_latitude)
    longitude = float(onemap_longitude)
    mrt_nearest, mrt_distance = get_nearest_railtransit(onemap_latitude, onemap_longitude, df_railtransit)
    mall_nearest, mall_distance = get_nearest_shoppingmall(onemap_latitude, onemap_longitude, df_shoppingmalls)
    orchard_distance = get_orchard_distance(onemap_latitude, onemap_longitude)
    hawker_distance = get_nearest_hawkercentre(onemap_latitude, onemap_longitude, df_hawkercentre)
    market_distance = get_nearest_supermarket(onemap_latitude, onemap_longitude, df_supermarket)

    df_postal_district = [0] * 28
    df_postal_district[postal_district - 1] = 1

    #Predict price for the 5 storey range
    df_predict_L1 = [[months,0,floor_area_sqm,remaining_lease,latitude,longitude,mrt_distance,mall_distance,orchard_distance,hawker_distance,market_distance]+ df_postal_district]
    df_predict_L4 = [[months,1,floor_area_sqm,remaining_lease,latitude,longitude,mrt_distance,mall_distance,orchard_distance,hawker_distance,market_distance]+ df_postal_district]
    df_predict_L7 = [[months,2,floor_area_sqm,remaining_lease,latitude,longitude,mrt_distance,mall_distance,orchard_distance,hawker_distance,market_distance]+ df_postal_district]
    df_predict_L10 = [[months,3,floor_area_sqm,remaining_lease,latitude,longitude,mrt_distance,mall_distance,orchard_distance,hawker_distance,market_distance]+ df_postal_district]
    df_predict_L13 = [[months,4,floor_area_sqm,remaining_lease,latitude,longitude,mrt_distance,mall_distance,orchard_distance,hawker_distance,market_distance]+ df_postal_district]

    #Use saved scaler to rescale data
    rescaled_df_L1 = loaded_scaler.transform(df_predict_L1)
    rescaled_df_L4 = loaded_scaler.transform(df_predict_L4)
    rescaled_df_L7 = loaded_scaler.transform(df_predict_L7)
    rescaled_df_L10 = loaded_scaler.transform(df_predict_L10)
    rescaled_df_L13 = loaded_scaler.transform(df_predict_L13)

    #Use saved model to do prediction
    predicted_L1 = np.exp(loaded_model.predict(rescaled_df_L1))[0]
    predicted_L4 = np.exp(loaded_model.predict(rescaled_df_L4))[0]
    predicted_L7 = np.exp(loaded_model.predict(rescaled_df_L7))[0]
    predicted_L10 = np.exp(loaded_model.predict(rescaled_df_L10))[0]
    predicted_L13 = np.exp(loaded_model.predict(rescaled_df_L13))[0]
 
    # #Adjust predicted price for HDB CPI index based on weighted average of past 3 quarters CPI
    df_cpi_index = cpi_index()
    weighted_cpi_3quarters = (float(df_cpi_index.iloc[-1]['cpi_index'])*0.4583) + (float(df_cpi_index.iloc[-2]['cpi_index'])*0.3333) + (float(df_cpi_index.iloc[-3]['cpi_index'])*0.2083)

    predicted_L1_cpi = round((predicted_L1 * weighted_cpi_3quarters / 100))
    predicted_L4_cpi = round((predicted_L4 * weighted_cpi_3quarters / 100))
    predicted_L7_cpi = round((predicted_L7 * weighted_cpi_3quarters / 100))
    predicted_L10_cpi = round((predicted_L10 * weighted_cpi_3quarters / 100))
    predicted_L13_cpi = round((predicted_L13 * weighted_cpi_3quarters / 100))

    return predicted_L1_cpi, predicted_L4_cpi, predicted_L7_cpi, predicted_L10_cpi, predicted_L13_cpi
