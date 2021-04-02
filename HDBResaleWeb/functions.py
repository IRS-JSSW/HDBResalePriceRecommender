import requests, json
import pandas as pd
from HDBResaleWeb import db
from HDBResaleWeb.models import resaleDataGov

def UpdateResaleData():
    url = 'https://data.gov.sg/api/action/datastore_search?resource_id=42ff9cfe-abe5-4b54-beda-c88f9bb438ee&limit=1000'
    results = requests.get(url)
    data = json.loads(results.content)

    df = pd.DataFrame(data['result']['records'])
    # total = data['result']['total']

    for i in range(0, len(df)):
        # print(df.iloc[i])
        update = resaleDataGov(
            town = df.iloc[i]['town'],
            flat_type = df.iloc[i]['flat_type'],
            flat_model = df.iloc[i]['flat_model'],
            floor_area_sqm = df.iloc[i]['floor_area_sqm'],
            street_name = df.iloc[i]['street_name'],
            resale_price = df.iloc[i]['resale_price'],
            month = df.iloc[i]['month'],
            lease_commence_date = df.iloc[i]['lease_commence_date'],
            storey_range = df.iloc[i]['storey_range'],
            block = df.iloc[i]['block']
        )
        db.session.add(update)
        db.session.commit()