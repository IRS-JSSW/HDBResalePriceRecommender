import pandas as pd, numpy as np
from sqlalchemy import create_engine, desc
from sklearn import preprocessing

def get_score(df):
    #Coefficient based on user survey
    Coeff = {'Ease of Access to LRT/MRT Station': 0.2891891892, 
            'Distance to Mall': 0.1657657658, 
            'Distance to Hawker Centre': 0.1846846847, 
            'Distance to City Centre (Orchard)': 0.1261261261, 
            'Age of Flat': 0.2342342342
            }

def recommender_system(df_recommendation):
    #Connect to database
    engine = create_engine("sqlite:///HDBResaleWeb/resaleproject.db")

    #Query database
    query = "SELECT * FROM prop_guru_table"

    #SQL to pandas df
    df = pd.read_sql_query(query, engine)

    #Best match - Most similar to user search (Similar / Better scoring than user search)
    ###Outside the zone - surprise factor ###
    #Filter based on user Input (hard filter)
    filter_flat_type = (df["flat_type"] == df_recommendation['flat_type'])
    filter_floor_area_sqm = ((df["floor_area_sqm"] <= df_recommendation['floor_area_sqm'] + 10) & (df["floor_area_sqm"] >= df_recommendation['floor_area_sqm'] - 10))

    df_best_match = df[filter_flat_type & filter_floor_area_sqm]
    

    print(df_best_match.head(3))

    df_best_match = {'Best Match 1':'Item 1','Best Match 2':'Item 2','Best Match 3':'Item 3'}
    df_cheaper_price = {'Cheaper Price 1':'Item 1','Cheaper Price 2':'Item 2','Cheaper Price 3':'Item 3'}
    df_bigger_house = {'Bigger House 1':'Item 1','Bigger House 2':'Item 2','Bigger House 3':'Item 3'}

    return df_best_match, df_cheaper_price, df_bigger_house