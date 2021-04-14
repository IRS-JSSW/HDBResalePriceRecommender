from sklearn import preprocessing
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

#Read data for flat data
df = pd.read_csv('./_flats.csv')
df.rename(columns={'Unnamed: 0':'S/N'}, inplace=True)

#Read Google Survey data
df_surv = pd.read_csv('./Surv_Result.csv', names = ['TimeStamp', 'First', 'Second', 'Third', 'Forth', 'Fifth'])
df_surv.drop(['TimeStamp'], axis=1, inplace=True)
df_surv.drop([0], inplace=True)
df_surv.reset_index(inplace=True, drop=True)



### Setting up Hard_filter ###

# User Input
u_town = "ANG MO KIO"
u_flat_type = "2 ROOM"
u_mrt_nearest ="Ang Mo Kio"
# u_floor_area_sqm = ""



# filter based on user Input
filter_mrt = df.nearest_MRT == u_mrt_nearest
# filter_town = df.town == u_town
# filter_flat_type = df.flat_type == u_flat_type


# Combine all the Hard filters
all_filter = filter_mrt
# all_filter = filter_flat_type & filter_town


# Filter data based on the combined filter
df_filt = df[all_filter]
df_filt.reset_index(inplace=True, drop=True)

# Data normalization
def data_normalization(df,col_name):
    df[col_name+'_normalized'] = preprocessing.normalize((np.asarray(df[col_name])).reshape(1,len(df[col_name])))[0].tolist()
    return df

# List data that needs to be normalized
col_names = ['MRT_distance','Mall_distance', 'Market_distance', 'Hawker_distance', 'CBD_distance']

for col_name in col_names:
    data_normalization(df_filt, col_name)


### Coefficient generation based on user survey ###
sv_index = ['Ease of Access to LRT/MRT Station', 'Distance to Mall', 'Distance to Hawker Centre', 'Distance to City Centre (Orchard)', 'Age of Flat']
sv_col = list(df_surv)

def append_value(dict_obj, key, value):
    # Check if key exist in dict or not
    if key in dict_obj:
        # Key exist in dict.
        # Check if type of value of key is list or not
        if not isinstance(dict_obj[key], list):
            # If type is not list then make it list
            dict_obj[key] = [dict_obj[key]]
        # Append the value in list
        dict_obj[key].append(value)
    else:
        # As key is not in dict,
        # so, add key-value pair
        dict_obj[key] = value


def loop_dict(diction):
    for i in sv_index:
        append_value(dict_matrix, i, diction.get(i))


dict_matrix = {}
for i in sv_col:
    if i == 'First':
        loop_dict(df_surv.groupby(i).count()['Second'].to_dict())
        
    else:
        loop_dict(df_surv.groupby(i).count()['First'].to_dict())   


df_matrix = pd.DataFrame(dict_matrix, index=sv_col)
df_matrix = df_matrix.fillna(0)
df_score = pd.DataFrame({'First': 5, 'Second': 4, 'Third':3, 'Forth':2, 'Fifth':1},index=sv_index).T


# m_MRT = ((df_matrix* df_score))['Ease of Access to LRT/MRT Station'].sum()
Coeff = []
for i in sv_index:
    Coeff.append(((df_matrix* df_score))[i].sum())

print(Coeff) #['Ease of Access to LRT/MRT Station', 'Distance to Mall', 'Distance to Hawker Centre', 'Distance to City Centre (Orchard)', 'Age of Flat']

# Scoring
score = []
X_Val = ['MRT_distance_normalized', 'Mall_distance_normalized', 'Hawker_distance_normalized', 'Orchard_distance_normalized', 'Age_of_flat_normalized']

for i in range(0, len(df_filt)):
    for j in range(0,5):
        score.append((df_filt[X_Val[j]][i] * Coeff[j]))
    

df_filt['score'] = score
print(df_filt)

# User Input Scoring

# Most similar to user search (Similar / Better scoring than user search)
# Outside the zone - surprise factor

# Better Price same size (Similar)
# size +- 10sqm
# Within the same zone

# Same Price bigger house (Scoring has to be similar to user input)
# anything that has lower price
# within the same zone
# sq_m >= user input