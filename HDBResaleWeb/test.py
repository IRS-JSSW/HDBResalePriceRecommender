import pandas as pd
import requests, json

apikey = 'AIzaSyCgkqiLJGlOIEp198VLr-X2anzIEpM5lFI'

# full_address = "27A C'WEALTH AVE" + " Singapore"
full_address = '46 JLN BT HO SWEE'
search = 'https://maps.googleapis.com/maps/api/geocode/json?&address='+full_address+'&key='+apikey

result = requests.get(search)
# data = pd.DataFrame(json.loads(result.content)['results'])
data = pd.json_normalize(json.loads(result.content)['results'])

if (not data.empty):
    print('DF is not empty')

# postal_code = str(data['formatted_address'][0])
# postal_code_start = postal_code.find('Singapore') + 10
# postal_code_end = postal_code.find('Singapore') + 12
# latitude = float(data['geometry.location.lat'][0])
# longitude = float(data['geometry.location.lng'][0])

# print(postal_code[postal_code_start:postal_code_end])
# print(latitude, longitude)