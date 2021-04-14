import pandas as pd
import requests, json
from datetime import datetime

# apikey = 'AIzaSyCgkqiLJGlOIEp198VLr-X2anzIEpM5lFI'

# # full_address = "27A C'WEALTH AVE" + " Singapore"
# full_address = '46 JLN BT HO SWEE'
# search = 'https://maps.googleapis.com/maps/api/geocode/json?&address='+full_address+'&key='+apikey

# result = requests.get(search)
# # data = pd.DataFrame(json.loads(result.content)['results'])
# data = pd.json_normalize(json.loads(result.content)['results'])

# if (not data.empty):
#     print('DF is not empty')

# postal_code = str(data['formatted_address'][0])
# postal_code_start = postal_code.find('Singapore') + 10
# postal_code_end = postal_code.find('Singapore') + 12
# latitude = float(data['geometry.location.lat'][0])
# longitude = float(data['geometry.location.lng'][0])

# print(postal_code[postal_code_start:postal_code_end])
# print(latitude, longitude)

datagov_latest_month = pd.to_datetime("2021-01-01")

url_cpi = 'https://data.gov.sg/api/action/datastore_search?resource_id=52e93430-01b7-4de0-80df-bc83d0afed40&limit=50000'
data = json.loads(requests.get(url_cpi).content)

df = pd.DataFrame(data['result']['records'])

df_cpi = pd.DataFrame(columns=['cpi_quarter','cpi_index'])

for i in range(0,len(df)):
    if (df.iloc[i]['quarter'][:4] >= '2000'):
        insert_row = {
                "cpi_quarter": df.iloc[i]['quarter'],
                "cpi_index": df.iloc[i]['index']
            }
        df_cpi = df_cpi.append(insert_row, ignore_index=True)

#If current quarter not in list, get average CPI of previous 3 months
datagov_latest_quarter = str(datagov_latest_month.year) + "-Q" + str(datagov_latest_month.quarter)
latest_hdb_cpi_quarter = str(df_cpi['cpi_quarter'][-1:])
if (datagov_latest_quarter != latest_hdb_cpi_quarter):
    
    # average_cpi_3months = round(sum(list(map(float, df_cpi['cpi_index'][-3:]))) / 3, 2)
    cpi_index = df_cpi.iloc[-1]['cpi_index']
    df_cpi = df_cpi.append({"cpi_quarter":datagov_latest_quarter, "cpi_index":cpi_index}, ignore_index=True)


print(df_cpi[-5:])