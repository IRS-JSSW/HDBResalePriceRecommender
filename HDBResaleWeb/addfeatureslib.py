import requests, json
import pandas as pd
# from onemapsg import OneMapClient
from haversine import haversine, Unit

apikey = 'AIzaSyCgkqiLJGlOIEp198VLr-X2anzIEpM5lFI'

def geographic_position(full_address):
    #Use OneMap Geocoding API to get lat, long and postal code
    full_address = full_address + ' Singapore'
    search = 'https://developers.onemap.sg/commonapi/search?searchVal='+full_address+'&returnGeom=Y&getAddrDetails=Y'

    result = requests.get(search)
    data = pd.DataFrame(json.loads(result.content)['results'])
    num_results = int(json.loads(result.content)['found'])

    #If location not found in OneMap, use Google Geocoding API
    if (num_results < 1):
        search = 'https://maps.googleapis.com/maps/api/geocode/json?&address='+full_address+'&key='+apikey
        
        result = requests.get(search)
        data = pd.json_normalize(json.loads(result.content)['results'])
        
        if (not data.empty):
            postal_code = str(data['formatted_address'][0])
            postal_sector_start = postal_code.find('Singapore') + 10
            postal_sector_end = postal_code.find('Singapore') + 12
            postal_sector = postal_code[postal_sector_start:postal_sector_end]
            latitude = float(data['geometry.location.lat'][0])
            longitude = float(data['geometry.location.lng'][0])
        if (data.empty):
            postal_sector = 0
            latitude = 0
            longitude = 0

    #If location found in OneMap, get values from json output
    if (num_results >= 1):
        postal_sector = data.iloc[0]['POSTAL'][:2]
        latitude = data.iloc[0]['LATITUDE']
        longitude = data.iloc[0]['LONGITUDE']

    #If postal code not found in OneMap, use Google Geocoding API
    if (postal_sector != 0) and (postal_sector.lower() == 'ni'):
        search = 'https://maps.googleapis.com/maps/api/geocode/json?&address='+full_address+'&key='+apikey

        result = requests.get(search)
        data = pd.json_normalize(json.loads(result.content)['results'])
        postal_code = str(data['formatted_address'][0])
        postal_sector_start = postal_code.find('Singapore') + 10
        postal_sector_end = postal_code.find('Singapore') + 12
        postal_sector = postal_code[postal_sector_start:postal_sector_end]
        
    return postal_sector, latitude, longitude
    
######################################################################################################
#Function to get nearest transit rail
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

#Function to get nearest shopping mall
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

#Function to calculate distance to orchard
def get_orchard_distance(onemap_latitude,onemap_longitude):
    # Orchard MRT coordinates
    orchard_coordinates = (1.30489770246908, 103.832525108319)
    #Combine latitude and longitude into one variable
    onemap_coordinates = (float(onemap_latitude), float(onemap_longitude))
    return haversine(onemap_coordinates, orchard_coordinates)

#Function to get nearest hawker centre
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

#Function to get nearest supermarket
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