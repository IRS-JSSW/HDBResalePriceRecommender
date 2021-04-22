import pandas as pd, numpy as np
from sqlalchemy import create_engine, desc
from sklearn import preprocessing

def recommender_system(df_recommendation):
    #Connect to database
    engine = create_engine("sqlite:///HDBResaleWeb/resaleproject.db")

    #Query database
    query = "SELECT * FROM prop_guru_table"

    #SQL to pandas df
    df = pd.read_sql_query(query, engine)

    print(df_recommendation)

    df_best_match = {'Best Match 1':'Item 1','Best Match 2':'Item 2','Best Match 3':'Item 3'}
    df_cheaper_price = {'Cheaper Price 1':'Item 1','Cheaper Price 2':'Item 2','Cheaper Price 3':'Item 3'}
    df_bigger_house = {'Bigger House 1':'Item 1','Bigger House 2':'Item 2','Bigger House 3':'Item 3'}

    return df_best_match, df_cheaper_price, df_bigger_house