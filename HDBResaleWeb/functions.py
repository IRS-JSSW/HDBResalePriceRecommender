import requests, json
import pandas as pd
from HDBResaleWeb import db
from HDBResaleWeb.models import DataGovTable, PropGuruTable, RailTransitTable, ShoppingMallsTable, HawkerCentreTable
from HDBResaleWeb.addfeatureslib import geographic_position, get_nearest_railtransit
from sqlalchemy import desc

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

    query_railtransit = RailTransitTable.query.all()
    df_railtransit = pd.DataFrame(columns=['station_name','coordinates'])
    for query_result in query_railtransit:
        insert_row = {
            "station_name": query_result.station_name,
            "coordinates": (query_result.latitude, query_result.longitude)
        }
        df_railtransit = df_railtransit.append(insert_row, ignore_index=True)

    # print(df_railtransit.iloc[0])

    for i in range(0, len(df)):
        if pd.to_datetime(df.iloc[i]['month']) <= update_month:
            full_address = df.iloc[i]['block'] + ' ' + df.iloc[i]['street_name']
            onemap_postal_sector, onemap_latitude, onemap_longitude = geographic_position(full_address)
            #Combine latitude and longitude into one variable
            datagov_coordinates = (float(onemap_latitude), float(onemap_longitude))
            mrt_nearest, mrt_distance = get_nearest_railtransit(datagov_coordinates, df_railtransit)
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
                postal_district = onemap_postal_sector,
                mrt_nearest = mrt_nearest,
                mrt_distance = mrt_distance,
                mall_nearest = "Dummy Mall",
                mall_distance = "0.000015",
                cbd_distance = "2.33",
                hawker_distance = '0.0012'
                # market_distance = '0.001'
            )
            db.session.add(update)
            db.session.commit()

def update_propguru_table():
    # url = 'https://www.propertyguru.com.sg/property-for-sale?property_type=H&order=desc'
    # results = requests.get(url)
    print("Building this function...")

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

def insert_hawkercentre_data():
    filepath = 'HDBResaleWeb/dataset/hawkers.csv'
    df = pd.read_csv(filepath)
    for i in range(0, len(df)):
        update = HawkerCentreTable(
            name_of_centre = df.iloc[i]['name_of_centre'],
            type_of_centre = df.iloc[i]['type_of_centre'],
            owner = df.iloc[i]['owner'],
            no_of_stalls = df.iloc[i]['no_of_stalls'],
            no_of_cooked_food_stalls = df.iloc[i]['no_of_cooked_food_stalls'],
            no_of_mkt_produce_stalls = df.iloc[i]['no_of_mkt_produce_stalls'],
            postal_code = df.iloc[i]['postal_code'],
            latitude = df.iloc[i]['latitude'],
            longitude = df.iloc[i]['longitude'],
            full_address = df.iloc[i]['full_address']
        )
        db.session.add(update)
        db.session.commit()

# def insert_supermarket_data():
#     filepath = 'HDBResaleWeb/dataset/markets.csv'
#     df = pd.read_csv(filepath)
#     for i in range(0, len(df)):
#         update = SuperMarketTable(
#             licensee_name = df.iloc[i]['licensee_name'],
#             postal_code = df.iloc[i]['postal_code'],
#             latitude = df.iloc[i]['latitude'],
#             longitude = df.iloc[i]['longitude'],
#             full_address = df.iloc[i]['full_address']
#         )
#         db.session.add(update)
#         db.session.commit()