import requests, json
import pandas as pd
from HDBResaleWeb import db
from HDBResaleWeb.models import DataGovTable, PropGuruTable
from HDBResaleWeb.addfeatureslib import geographic_position
from sqlalchemy import desc

def update_datagov_table():
    url_2017 = 'https://data.gov.sg/api/action/datastore_search?resource_id=42ff9cfe-abe5-4b54-beda-c88f9bb438ee&limit=100'
    url_2015 = 'https://data.gov.sg/api/action/datastore_search?resource_id=1b702208-44bf-4829-b620-4615ee19b57c&limit=10'
    #Data before 2015 does not contain remaining_lease column
    # url_2012 = 'https://data.gov.sg/api/action/datastore_search?resource_id=83b2fc37-ce8c-4df4-968b-370fd818138b&limit=5'
    # url_2000 = 'https://data.gov.sg/api/action/datastore_search?resource_id=8c00bf08-9124-479e-aeca-7cc411d884c4&limit=5'
    results = requests.get(url_2015)
    data = json.loads(results.content)

    df = pd.DataFrame(data['result']['records'])
    # total = data['result']['total']

    last_record = DataGovTable.query.order_by(DataGovTable.id.desc()).all()
    for result in last_record:
        print(result.month, result.town, result.block, result.street_name)
    # latest_month = pd.to_datetime(last_record.month)
    update_month = pd.to_datetime("2017-12")

    for i in range(0, len(df)):
        if pd.to_datetime(df.iloc[i]['month']) <= update_month:
            full_address = df.iloc[i]['block'] + ' ' + df.iloc[i]['street_name']
            get_latitude, get_longitude = geographic_position(full_address)
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
                latitude = get_latitude,
                longitude = get_longitude,
                district = 'Dummy district',
                mrt_nearest = 'Dummy mrt station',
                mrt_distance = "0.001",
                mall_nearest = "Dummy Mall",
                mall_distance = "0.000015",
                cbd_distance = "2.33",
                market_distance = '0.001',
                hawker_distance = '0.0012'
            )
            db.session.add(update)
            db.session.commit()

def update_propguru_table():
    # url = 'https://www.propertyguru.com.sg/property-for-sale?property_type=H&order=desc'
    # results = requests.get(url)
    print("Building this function...")