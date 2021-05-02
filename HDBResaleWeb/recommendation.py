import joblib
import pandas as pd, numpy as np
from sqlalchemy import create_engine, desc
from sklearn import preprocessing
from sklearn.preprocessing import MinMaxScaler

# def get_score(user_input):
#     #Coefficient based on user survey
#     #[Age of flat: 0.351351351, orchard_distance: 0.027027027, hawker_distance: 0.054054054, mall_distance: 0, mrt_distance: 0.567567568]
#     recommend_score = 0.351351351*(99 - pgDF.iloc[i]['RemainingLease']) +  1/(0.027027027*orchard_distance) +  1/(0.054054054*hawker_distance)+ 1/(0.567567568*mrt_distance)

def recommender_system(df_user_input):
    #Connect to database
    engine = create_engine("sqlite:///HDBResaleWeb/resaleproject.db")

    #Query database
    query = "SELECT * FROM prop_guru_table"

    #SQL to pandas df
    df = pd.read_sql_query(query, engine)

    #Load MinMaxScaler used during scoring of all propguru listings
    scaler_filename = 'HDBResaleWeb/hdb_recommender_scaler.joblib'
    scaler = joblib.load(scaler_filename)

    df_user_input[['scaled_rem_lease', 'scaled_orchard_distance', 'scaled_hawker_distance', 'scaled_mall_distance', 'scaled_mrt_distance']] = scaler.transform(df_user_input[['remaining_lease', 'orchard_distance', 'hawker_distance', 'mall_distance', 'mrt_distance']])
    df_user_input[['scaled_orchard_distance', 'scaled_hawker_distance', 'scaled_mall_distance', 'scaled_mrt_distance']] = 1.0 - df_user_input[['scaled_orchard_distance', 'scaled_hawker_distance', 'scaled_mall_distance', 'scaled_mrt_distance']]

    df_user_input = df_user_input.assign(recommend_score = 0.2342342342*df_user_input.scaled_rem_lease + 0.1261261261*df_user_input.scaled_orchard_distance + 0.1846846847*df_user_input.scaled_hawker_distance + 0.1657657658*df_user_input.scaled_mall_distance + 0.2891891892*df_user_input.scaled_mrt_distance)


    #Best match - Most similar to user search (Similar / Better scoring than user search)
    ###Outside the zone - surprise factor ###
    #Filter based on user Input (hard filter)
    filter_postal_district = (df["postal_district"] != df_user_input['postal_district'][0])
    filter_flat_type = (df["flat_type"] == df_user_input['flat_type'][0])
    filter_score = (df["recommend_score"] > df_user_input['recommend_score'][0])
    filter_maxprice = (df["resale_price"] < df_user_input['listing_price'][0] + 26000)
    filter_remaininglease = (df["remaining_lease"] > df_user_input['remaining_lease'][0] - 5)

    df_best_match_1 = df[filter_postal_district & filter_flat_type & filter_score & filter_maxprice & filter_remaininglease].copy()

    #Drop listing with same listing name and resale price
    df_best_match_1.drop_duplicates(subset=['listing_name','resale_price'], inplace=True, keep='last')
    df_best_match_1 = df_best_match_1.sort_values('recommend_score', ascending=False).head(3)
    #If listing than than 3
    if len(df_best_match_1) < 3:  
        df_best_match_2 = df[filter_flat_type & filter_score & filter_maxprice & filter_remaininglease].copy()
        #Drop listing with same listing name and resale price
        df_best_match_2.drop_duplicates(subset=['listing_name','resale_price'], inplace=True, keep='last')
        df_best_match_2 = df_best_match_2.sort_values('recommend_score', ascending=False).head(3 - len(df_best_match_1))
        df_best_match = pd.concat([df_best_match_1, df_best_match_2])
    else:
        df_best_match = df_best_match_1
    

    #Similar Size, Better Price (Similar)
    ###Within the same zone - Size +10, Price < user input###
    #Filter based on user Input (hard filter)
    filter_postal_district = (df["postal_district"] == df_user_input['postal_district'][0])
    filter_floor_area_sqm = (df["floor_area_sqm"].between(df_user_input['floor_area_sqm'][0] * 0.9, df_user_input['floor_area_sqm'][0] * 1.1))
    filter_maxprice = (df["resale_price"] < df_user_input['listing_price'][0])
    
    df_cheaper_price_1 = df[filter_postal_district & filter_floor_area_sqm & filter_score & filter_maxprice].copy()
    #Drop listing with same listing name and resale price
    df_cheaper_price_1.drop_duplicates(subset=['listing_name','resale_price'], inplace=True, keep='last')
    df_cheaper_price_1 = df_cheaper_price_1.sort_values('resale_price', ascending=False).head(3)
    #If listing than than 3
    if len(df_cheaper_price_1) < 3:  
        df_cheaper_price_2 = df[filter_floor_area_sqm & filter_score & filter_maxprice].copy()
        #Drop listing with same listing name and resale price
        df_cheaper_price_2.drop_duplicates(subset=['listing_name','resale_price'], inplace=True, keep='last')
        df_cheaper_price_2 = df_cheaper_price_2.sort_values('resale_price', ascending=False).head(3 - len(df_cheaper_price_1))
        df_cheaper_price = pd.concat([df_cheaper_price_1, df_cheaper_price_2])
    else:
        df_cheaper_price = df_cheaper_price_1


    #Similar Price, Bigger House (Similar)
    ###Within the same zone - Size > user input, Price +- 26000###
    #Filter based on user Input (hard filter)
    filter_postal_district = (df["postal_district"] == df_user_input['postal_district'][0])
    filter_floor_area_sqm = (df["floor_area_sqm"] >= df_user_input['floor_area_sqm'][0])
    filter_maxprice = (df["resale_price"].between(df_user_input['listing_price'][0] - 26000, df_user_input['listing_price'][0] + 26000))
    
    df_bigger_house_1 = df[filter_postal_district & filter_score & filter_floor_area_sqm & filter_maxprice].copy()
    #Drop listing with same listing name and resale price
    df_bigger_house_1.drop_duplicates(subset=['listing_name','resale_price'], inplace=True, keep='last')
    df_bigger_house_1 = df_bigger_house_1.sort_values('floor_area_sqm', ascending=False).head(3)
    #If listing than than 3
    if len(df_bigger_house_1) < 3:  
        df_bigger_house_2 = df[filter_floor_area_sqm & filter_score & filter_maxprice].copy()
        df_bigger_house_2 = df_bigger_house_2.sort_values('floor_area_sqm', ascending=False).head(3 - len(df_bigger_house_1))
        df_bigger_house = pd.concat([df_bigger_house_1, df_bigger_house_2])
    else:
        df_bigger_house = df_bigger_house_1

    return df_best_match, df_cheaper_price, df_bigger_house