from typing import Callable
import requests
import pandas as pd
import numpy as np

URL_NAME = "https://www.albion-online-data.com/api/v2/stats/"
ROYAL_CITIES = ['Martlock', 'Thetford', 'Fort Sterling', 'Lymhurst', 'Bridgewatch']
DEBUG = True
# TO-DO 
# gather data from time-scale = 1, then time-scale = 6, DONE 
# then time-scale = 24 and gather all, DONE
# add quality to code
# inplace for dataframes, DONE
# check validity of the data you get (important)
    # check for all data to compare, DONE
    # make the invalid data nan 
    # make a function to see if data is valid
# add taxes for selling and buying
# add average prices and item counts
# add cur prices and cur time
# inner functions used in pandas
# check time-data compability DONE
# dataframe functions
# IMPORTANT, MERGE FUNCTION IS NOT WORKING PROPERLY

def get_data(url_name: str, items: list, **kwargs) -> pd.DataFrame:
    """Gets the multiple item data using api 
    
    Args:
        url_name: it is the api url name. There are two types of data:\
        history and prices data. History data shows the daily, weekly and
        monthly data; prices data gets the current data.
        items: list of items, needs to be a list even if there is
        only one item

    Keyword Args:
        **timescale (int): it is used with history data, if not used api
        automatically returns weekly data. 
        **locations (list): list of locations (str), needs to be a list even
        if there is only one location. If not used api automatically returns 
        the data from all the possible cities.
        **qualities (Union[int, list]): list of qualities (int). If not used api 
        automatically returns the data from all possible qualities.  

    Returns:
        pd.DataFrame: returns the obtained dataframe from the api  
    """
    # A nice solution for lists 
    url_name = url_name + list_to_string(items)

    # You can't put time-scale as key into input, hack for it
    if 'timescale' in kwargs:
        kwargs['time-scale'] = kwargs.pop('timescale')

    if kwargs:
        kwargs_iter = iter(kwargs.items())
        first_key, first_value =  next(kwargs_iter)
        url_name = url_name + '?' + first_key + '=' + list_to_string(first_value)
        
        for kwarg in kwargs_iter:
            key, value = kwarg
            # Additional arguments starts with & in api
            url_name = url_name + '&' + key + '=' + list_to_string(value) 

    if DEBUG:
        print('requesting response from {}'.format(url_name))

    response = requests.get(url_name)

    return pd.DataFrame(response.json())

def list_to_string(str_list: list) -> str:
    """This function combines the list of strings with a comma.
    
    Args:
        str_list: The input list, can be str or int

    Returns:
        str: string combination of list elements with comma 
    """

    if isinstance(str_list, list):
        return ','.join(list(map(str,str_list)))
    else:
        return str(str_list)

def weight_calc(df: pd.DataFrame) -> Callable:
    """Lambda function to calculate prices with item count
    
    Args:
        df: The input dataframe

    Returns:
        str: string combination of list elements with comma 
    """
    return lambda x: int(np.round(np.average(x, weights=df.loc[x.index, "item_count"])))

def add_portals(city_list: list) -> list:
    """Adds portal names of the cities to the list of cities
    
    Args:
        city_list: The input list of strings, should be royal cities

    Returns:
        str: string combination of list elements with comma 
    """
    city_list_modified = city_list.copy()
    for city in city_list:
        assert city in ROYAL_CITIES, 'city is not a royal city'
        city_list_modified.append(city + ' Portal')
    return city_list_modified

def get_data_index(
    df: list,
    item: str,
    location: str,
    quality: int = 1
) -> int:

    idx = df.index[(df['location'] == location)
    & (df['item_id'] == item)
    & (df['quality'] == quality)]
    
    if len(idx):
        return idx[0]
    else:
        return None

    

def data_to_df(
    df: pd.DataFrame,
    item: str,
    location: str, 
    quality: int = 1,
    data_key: str = 'data'
) -> pd.DataFrame:

    idx = get_data_index(df, item, location, quality)

    if df.loc[idx,:][data_key:data_key].isnull().all():
        # typing is problematic
        return  pd.DataFrame({'item_count': pd.Series(dtype='int64'),
                   'avg_price': pd.Series(dtype='int64'),
                   'timestamp': pd.Series(dtype='datetime64[ns]')})
    else:
        return df.loc[idx, data_key].copy()

def df_to_data(
    df: pd.DataFrame,
    data: pd.DataFrame,
    item: str,
    location: str,
    quality: int = 1,
    data_key: str = 'data'
) -> None:

    idx = get_data_index(df, item, location, quality)
    if idx is not None:
        df.at[idx, data_key] = data.copy()

