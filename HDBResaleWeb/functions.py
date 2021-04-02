import requests, json
import pandas as pd
from HDBResaleWeb import db
from HDBResaleWeb.models import resaleDataGov
from sqlalchemy import desc

def updateresaledata():
    url = 'https://data.gov.sg/api/action/datastore_search?resource_id=42ff9cfe-abe5-4b54-beda-c88f9bb438ee&limit=100'
    results = requests.get(url)
    data = json.loads(results.content)

    df = pd.DataFrame(data['result']['records'])
    total = data['result']['total']

    last_record = resaleDataGov.query.order_by(resaleDataGov.id.desc()).first()
    print(last_record)
    # latest_month = pd.to_datetime(last_record.month)
    update_month = pd.to_datetime("2017-12")

    for i in range(0, len(df)):
        if pd.to_datetime(df.iloc[i]['month']) <= update_month:
            update = resaleDataGov(
            #Raw features from datagov
                month = pd.to_datetime(df.iloc[i]['month']),
                town = df.iloc[i]['town'],
                flat_type = df.iloc[i]['flat_type'],
                # block = df.iloc[i]['block'],
                street_name = df.iloc[i]['street_name'],
                storey_range = df.iloc[i]['storey_range'],
                floor_area_sqm = df.iloc[i]['floor_area_sqm'],
                flat_model = df.iloc[i]['flat_model'],
                lease_commence_date = df.iloc[i]['lease_commence_date'],
                remaining_lease = df.iloc[i]['remaining_lease'][:2],
                resale_price = df.iloc[i]['resale_price'],
            #Additional features added
                latitude = "1234",
                longitude = "4321",
                mrt_distance = "0.001",
                mall_nearest = "Clementi Mall",
                mall_distance = "0.000015",
                cbd_distance = "2.33"
            )
            db.session.add(update)
            db.session.commit()