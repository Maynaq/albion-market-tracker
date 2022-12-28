from typing import Callable
import pandas as pd
import numpy as np
from datetime import datetime as dt

from common.func_utils import *

def get_prices_data(item_list: list,
    location_list: list,
    quality_list: list
) -> pd.DataFrame:
    
    df = get_data(
        URL_NAME + 'prices' + '/',
        item_list,
        locations = location_list,
        qualities = quality_list
    )

    handle_df(df)

    return merge_portal_with_city_price(df, location_list)

def handle_df(df):
    df.rename(
        columns = {
            'city':'location',
            'sell_price_min_date':'info_date',
            'sell_price_min':'price' 
        }, inplace=True)

    df['info_date'] = pd.to_datetime(df['info_date'], errors='coerce')

    df.drop(
        df.loc[:,'sell_price_max':'buy_price_max_date'].columns,
        axis = 1,
        inplace=True
    )

def merge_portal_with_city_price(
    df: pd.DataFrame,
    royal_cities: list
) -> pd.DataFrame:
    for city in royal_cities:
        df.loc[df['location'] == city + ' Portal', 'location'] = city

    
    df_agg = df.groupby(['item_id','location', 'quality']).info_date.transform(max)
    merged_df = df.loc[df.info_date == df_agg]
    merged_df = merged_df.groupby([
                    'item_id',
                    'location',
                    'quality',
                    'info_date'
                ]).agg(sum).reset_index()

    cur_time = dt.utcnow()
    last_update = cur_time - merged_df['info_date']
    last_update_hours = (last_update.dt.seconds//3600).map(str)
    last_update_mins = ((last_update.dt.seconds//60)%60).map(str)
    merged_df['last_update'] = last_update_hours + 'H' + last_update_mins + 'M'

    return merged_df

def process_prices_data(
        item_list: list,
        location_list: list,
        quality_list: list = [1]
    ) -> tuple:
    
    city_and_portals = add_portals(location_list)

    df = get_prices_data(
        item_list,
        city_and_portals,
        quality_list
    )
    
    return df