import requests, json
import pandas as pd
# from onemapsg import OneMapClient
from haversine import haversine, Unit

# Client = OneMapClient(email='jovintoh88sp@gmail.com', password='MtechISS2021')

def geographic_position(full_address):
    full_address = full_address
    search = 'https://developers.onemap.sg/commonapi/search?searchVal='+full_address+'&returnGeom=Y&getAddrDetails=Y'

    result = requests.get(search)
    data = pd.DataFrame(json.loads(result.content)['results'])
    postal_sector = data.iloc[0]['POSTAL'][:2]
    latitude = data.iloc[0]['LATITUDE']
    longitude = data.iloc[0]['LONGITUDE']

    return postal_sector, latitude, longitude

def get_nearest_railtransit(datagov_coordinates, railtransit_data):
    nearest_distance = 1000
    nearest_rail = 0
    distances = []
    for record in range(len(railtransit_data)):
        distance = haversine(datagov_coordinates, railtransit_data.iloc[record]['coordinates'])
        distances.append(distance)
        if distance < nearest_distance:
            nearest_distance = distance
            nearest_rail = railtransit_data.iloc[record]['station_name']

    return str(nearest_rail), float(nearest_distance)