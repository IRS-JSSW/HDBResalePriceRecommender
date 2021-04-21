from sklearn import preprocessing
import numpy as np
import pandas as pd

#Read data for flat data
df = pd.read_csv('./HDBResaleWeb/dataset/propguru_complete.csv')
df.rename(columns={'Unnamed: 0':'S/N'}, inplace=True)

#Read Google Survey data
df_surv = pd.read_csv('./HDBResaleWeb/dataset/Importance when purchasing resale flat.csv', names = ['TimeStamp', 'First', 'Second', 'Third', 'Forth', 'Fifth'])
df_surv.drop(['TimeStamp'], axis=1, inplace=True)
df_surv.drop([0], inplace=True)
df_surv.reset_index(inplace=True, drop=True)


### Setting up Hard_filter ###

# User Input
u_postal_district = 4
u_flat_type = "1 ROOM"
u_mrt_nearest ="Tiong Bahru"
u_floor_area_sqm = 31.0296453887532



### function list ###

# Data normalization
def data_normalization(df,col_name):
    df[col_name+'_normalized'] = preprocessing.normalize((np.asarray(df[col_name])).reshape(1,len(df[col_name])))[0].tolist()
    return df

def loop_norm(df):
    # List data that needs to be normalized
    col_names = ['mrt_distance','mall_distance', 'market_distance', 'hawker_distance', 'orchard_distance', 'remaining_lease']

    for col_name in col_names:
        data_normalization(df, col_name)

# appending dictionary
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


# Function to get scoring for the property
def get_score(df):
    score = []
    X_Val = ['mrt_distance_normalized', 'mall_distance_normalized', 'hawker_distance_normalized', 'orchard_distance_normalized', 'remaining_lease_normalized']

    for i in range(0, len(df)):
        score_n = 0
        for j in range(0,5):
            score_n = score_n + ((df[X_Val[j]][i] * Coeff[j]))
        score.append(score_n)
    return score
        
# Function that sorts the filtered listing data    
def sort_result(df):
    df.sort_values(['score','resale_price'], ascending=[False, True],inplace=True)

### End of function list ###




### Coefficient generation based on user survey ###
sv_index = ['Ease of Access to LRT/MRT Station', 'Distance to Mall', 'Distance to Hawker Centre', 'Distance to City Centre (Orchard)', 'Age of Flat']
sv_col = list(df_surv)


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




### Most similar to user search (Similar / Better scoring than user search) ###
### Outside the zone - surprise factor ###


# filter based on user Input (hard filter)

# filter_postal_district = df.postal_district == u_postal_district
filter_flat_type = df.flat_type == u_flat_type
# filter_mrt = df.mrt_nearest == u_mrt_nearest
filter_floor_area_sqm = ((df.floor_area_sqm <= u_floor_area_sqm + 10) & (df.floor_area_sqm >= u_floor_area_sqm - 10))


# Combine all the Hard filters
all_filter = filter_flat_type & filter_floor_area_sqm


# Filter data based on the combined filter
df_filt_1 = df[all_filter]
df_filt_1.reset_index(inplace=True, drop=True)


# Append user input to df_filt


# Data normalization
loop_norm(df_filt_1)

# Get Scoring
df_filt_1['score'] = get_score(df_filt_1)

# Get scoring for user and filter the df_filt (property score >= user score)


# Sort top 3
sort_result(df_filt_1)
print(df_filt_1.head(3))




### Better Price same size (Similar) ###
#### size +- 10sqm ###
### Within the same zone ###

# filter based on user Input (hard filter)

filter_postal_district = df.postal_district == u_postal_district
filter_flat_type = df.flat_type == u_flat_type
# filter_mrt = df.mrt_nearest == u_mrt_nearest
filter_floor_area_sqm = ((df.floor_area_sqm <= u_floor_area_sqm + 10) & (df.floor_area_sqm >= u_floor_area_sqm - 10))


# Combine all the Hard filters
all_filter = filter_postal_district & filter_flat_type & filter_floor_area_sqm


# Filter data based on the combined filter
df_filt_2 = df[all_filter]
df_filt_2.reset_index(inplace=True, drop=True)


# Append user input to df_filt


# Data normalization
loop_norm(df_filt_2)

# Get Scoring
df_filt_2['score'] = get_score(df_filt_2)

# Get scoring for user and filter the df_filt (property score >= user score)


# Sort top 3
sort_result(df_filt_2)
print(df_filt_2.head(3))



### Same Price bigger house (Scoring has to be similar to user input) ###
### anything that has lower price ###
### within the same zone ###
### sq_m >= user input ###


# filter based on user Input (hard filter)

filter_postal_district = df.postal_district == u_postal_district
filter_flat_type = df.flat_type == u_flat_type
# filter_mrt = df.mrt_nearest == u_mrt_nearest
filter_floor_area_sqm = ((df.floor_area_sqm > u_floor_area_sqm))


# Combine all the Hard filters
all_filter = filter_postal_district & filter_flat_type & filter_floor_area_sqm


# Filter data based on the combined filter
df_filt_3 = df[all_filter]
df_filt_3.reset_index(inplace=True, drop=True)


# Append user input to df_filt


# Data normalization
loop_norm(df_filt_3)

# Get Scoring
df_filt_3['score'] = get_score(df_filt_3)

# Get scoring for user and filter the df_filt (property score ~~ user score)


# filter for resale price <= user

# Sort top 3
sort_result(df_filt_3)
print(df_filt_3.head(3))

