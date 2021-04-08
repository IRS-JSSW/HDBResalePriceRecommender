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
    #If first entry doesn't have valid postal code, use postal code from second entry
    postal_sector = data.iloc[0]['POSTAL'][:2] if (data.iloc[0]['POSTAL'][:2]) != "Ni" else data.iloc[1]['POSTAL'][:2]
    latitude = data.iloc[0]['LATITUDE']
    longitude = data.iloc[0]['LONGITUDE']

    return postal_sector, latitude, longitude

def get_nearest_railtransit(onemap_latitude,onemap_longitude,railtransit_data):
    nearest_distance = 1000
    nearest_rail = 0
    distances = []
    #Combine latitude and longitude into one variable
    onemap_coordinates = (float(onemap_latitude), float(onemap_longitude))
    for record in range(len(railtransit_data)):
        distance = haversine(onemap_coordinates, railtransit_data.iloc[record]['coordinates'])
        distances.append(distance)
        if distance < nearest_distance:
            nearest_distance = distance
            nearest_rail = railtransit_data.iloc[record]['station_name']

    return str(nearest_rail), float(nearest_distance)

def get_nearest_shoppingmall(onemap_latitude,onemap_longitude,shoppingmall_data):
    nearest_distance = 1000
    nearest_mall = 0
    distances = []
    #Combine latitude and longitude into one variable
    onemap_coordinates = (float(onemap_latitude), float(onemap_longitude))
    for record in range(len(shoppingmall_data)):
        distance = haversine(onemap_coordinates, shoppingmall_data.iloc[record]['coordinates'])
        distances.append(distance)
        if distance < nearest_distance:
            nearest_distance = distance
            nearest_mall = shoppingmall_data.iloc[record]['Shopping_Malls']

    return str(nearest_mall), float(nearest_distance)

def get_cbd_distance(onemap_latitude,onemap_longitude):
    # Raffles Place MRT coordinates
    cbd_coordinates = (1.2840188940605939, 103.85160965868303)
    #Combine latitude and longitude into one variable
    onemap_coordinates = (float(onemap_latitude), float(onemap_longitude))
    return haversine(onemap_coordinates, cbd_coordinates)

def get_nearest_hawkercentre(onemap_latitude,onemap_longitude,hawkercentre_data):
    nearest_distance = 1000
    distances = []
    #Combine latitude and longitude into one variable
    onemap_coordinates = (float(onemap_latitude), float(onemap_longitude))
    for record in range(len(hawkercentre_data)):
        distance = haversine(onemap_coordinates, hawkercentre_data.iloc[record]['coordinates'])
        distances.append(distance)
        if distance < nearest_distance:
            nearest_distance = distance

    return float(nearest_distance)

def get_nearest_supermarket(onemap_latitude,onemap_longitude,supermarket_data):
    nearest_distance = 1000
    distances = []
    #Combine latitude and longitude into one variable
    onemap_coordinates = (float(onemap_latitude), float(onemap_longitude))
    for record in range(len(supermarket_data)):
        distance = haversine(onemap_coordinates, supermarket_data.iloc[record]['coordinates'])
        distances.append(distance)
        if distance < nearest_distance:
            nearest_distance = distance

    return float(nearest_distance)