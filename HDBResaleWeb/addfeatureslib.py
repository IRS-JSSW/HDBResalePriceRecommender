import requests, json
import pandas as pd
# from onemapsg import OneMapClient
from haversine import haversine, Unit

# Client = OneMapClient(email='jovintoh88sp@gmail.com', password='MtechISS2021')

def geographic_position(full_address):
    full_address = full_address
    search = 'https://developers.onemap.sg/commonapi/search?searchVal='+full_address+'&returnGeom=Y&getAddrDetails=N'

    result = requests.get(search)
    data = pd.DataFrame(json.loads(result.content)['results'])
    latitude = data.iloc[0]['LATITUDE']
    longitude = data.iloc[0]['LONGITUDE']

    return latitude, longitude