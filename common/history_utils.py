from typing import Callable
import pandas as pd
import numpy as np
from datetime import datetime as dt, timedelta as td

from common.func_utils import *

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

def merge_data(row: list, timescale: int) -> list:
    """Merges city and portal data in dataframe
    
    Args:
        row: Corresponding history data in a row of dataframe 
        timescale: history data time scale, can be 1, 6 or 24.  
    Returns:
        str: string combination of list elements with comma 
    """
    # removes the duplicates in the list of dictionaries 
    row = [dict(t) for t in {tuple(d.items()) for d in row}]

    # list of dictionary converted to dataframe and time strings to timestamp
    row = pd.DataFrame(row)
    row['timestamp'] = pd.to_datetime(row['timestamp'])

    row = row[row['timestamp'].dt.hour % timescale == 0]
    # sorts the data 
    return row.sort_values(by=['timestamp']).reset_index(drop=True)

def merge_portal_with_city_history(
    df: pd.DataFrame,
    city_list: list,
    timescale: int
) -> pd.DataFrame:
     
    for city in city_list:
        df.loc[df['location'] == city + ' Portal', 'location'] = city

    df = df['data'].groupby([df.location, df.item_id, df.quality]).agg(sum).reset_index()
    df['data'] = df['data'].map(lambda x: merge_data(x, timescale))
    return df

def merge_historic_data(
    df_full: pd.DataFrame,
    df2_row: pd.DataFrame,
    item: str,
    location: str,
    quality: int,
    func: Callable,
    left_iqr: int,
    right_iqr: int,
    data_key: str = 'data'
) -> tuple:
    
    df_row = data_to_df(df_full, item, location, quality, data_key)
    if not df_row.empty:
        df_row = df_row[(df_row['avg_price'] >= int(left_iqr))
            & (df_row['avg_price'] <= int(right_iqr))]
    if not df2_row.empty:
        df2_row['timestamp'] = df2_row['timestamp'].map(func)
        df2_row = df2_row.groupby(['timestamp'], as_index = True).agg(
                {"item_count": np.sum, "avg_price": weight_calc(df2_row)}).reset_index()

    merged_df = pd.merge(df2_row, df_row, how = 'outer')
    merged_df.sort_values(by='timestamp', ignore_index=True, inplace=True)
    df_agg = merged_df.groupby(['timestamp']).item_count.transform(max)
    merged_df =  merged_df.loc[merged_df.item_count == df_agg]
    df_agg = merged_df.groupby(['timestamp']).avg_price.transform(max)
    merged_df =  merged_df.loc[merged_df.avg_price == df_agg]

    df_to_data(df_full, merged_df, item, location, quality, data_key)
    return df_full, merged_df

def validate_history_data(df_raw, item, location_list, quality):
    # TO-DO add quality
    df_empty = pd.DataFrame()
    def concat(bool_list,*args):
        return pd.concat([x['avg_price'] for i,x in enumerate(args) if not bool_list[i]]).reset_index(drop=True)

    for location in location_list:  
        idx = get_data_index(df_raw, item, location, quality)
        if idx is not None:
            daily_data = df_raw.loc[idx,'daily_data']
            weekly_data = df_raw.loc[idx,'weekly_data']
            monthly_data = df_raw.loc[idx,'monthly_data']
            
            bool_list = df_raw.loc[idx,:]['daily_data':'monthly_data'].isnull().to_list()

            df_empty = pd.concat([df_empty,
                concat(bool_list, *[daily_data, weekly_data, monthly_data])]).reset_index(drop=True)

    if len(df_empty) == 0:
        print('no data on item {}'.format(item))
        left_iqr = 0
        right_iqr = 1e12
    else:
        if len(df_empty) >= 100:     
            q1 = df_empty.quantile(0.25)
            q3 = df_empty.quantile(0.75)
            iqr = q3 - q1
            left_iqr = q1 - 1.7*iqr # q1 - 1.5*iqr
            right_iqr = q3 + 1.7*iqr # q3 + 1.5*iqr
        else:
            left_iqr = df_empty.median()/3
            right_iqr = df_empty.median()*3


        d = np.array(df_empty)
        num_of_valids = len(d[(d >= int(left_iqr)) & (d <= int(right_iqr))])
        num_of_eliminated = len(d) - num_of_valids
        percentage_of_eliminated =  100 * num_of_eliminated / len(d) 
        print('for ' + item + ' with quality {} \n'.format(quality))
        print('prices lower than {} and higher than {} are eliminated \n'.\
            format(int(left_iqr), int(right_iqr)))
        print('percentage of eliminated data: %{}\n'.format(percentage_of_eliminated))
        print('max of data: {}\n'.format(np.max(d)))
        print('min of data: {}\n'.format(np.min(d)))
        print('median of data: {}\n'.format(np.median(d)))
        print('-----------------------------------------')
    
    return left_iqr, right_iqr

def get_history_data(
    item_list: list,
    location_list: list,
    quality_list: list,
    timescale: int
) -> pd.DataFrame:

    df = get_data(
        URL_NAME + 'history' + '/',
        item_list,
        locations = location_list,
        qualities = quality_list,
        timescale = timescale
    )

    return merge_portal_with_city_history(df, location_list, timescale)

def process_history_data(
        item_list: list,
        location_list: list,
        quality_list: list = [1],
        avg_days: int = 14
    ) -> tuple:
    
    city_and_portals = add_portals(location_list)

    daily_df_raw = get_history_data(
        item_list,
        city_and_portals,
        quality_list,
        timescale = 1
    )
    
    weekly_df_raw = get_history_data(
        item_list,
        city_and_portals,
        quality_list,
        timescale = 6
    )
    
    monthly_df_raw = get_history_data(
        item_list,
        city_and_portals,
        quality_list,
        timescale = 24
    )
    
    df_raw = pd.merge(pd.merge(daily_df_raw.rename(columns={'data': 'daily_data'}),
                    weekly_df_raw.rename(columns={'data': 'weekly_data'}), how = 'outer'),
                    monthly_df_raw.rename(columns={'data': 'monthly_data'}), how = 'outer')

    df_raw.sort_values(by = ['location','item_id'], ignore_index=True, inplace=True)
    df_all = df_raw.copy()

    for item in item_list:
        for quality in quality_list:
            if not quality in df_all['quality'].unique():
                continue
            left_iqr, right_iqr = validate_history_data(df_raw,
            item, location_list, quality)

            for location in location_list:
                idx = get_data_index(df_all, item, location, quality)
                if idx is not None:
            # read daily, weekly, monthly data
                    daily_df = data_to_df(df_all,
                        item,
                        location,
                        quality,
                        data_key='daily_data'
                    )

                    daily_df = daily_df[(daily_df['avg_price'] >= int(left_iqr))
                    & (daily_df['avg_price'] <= int(right_iqr))]
                    
                    df_to_data(
                        df_all,
                        daily_df,
                        item,
                        location,
                        quality,
                        data_key='daily_data'
                    )

                    week_func = lambda x: x.replace(hour = 6 * (x.hour // 6))
                    df_all, weekly_result_df = merge_historic_data(
                        df_all,
                        daily_df,
                        item,
                        location,
                        quality,
                        week_func,
                        left_iqr,
                        right_iqr,
                        data_key='weekly_data'
                    )

                    month_func = lambda x: (x - np.timedelta64(6,'h')).replace(hour = 0)
                    df_all, monthly_result_df = merge_historic_data(
                        df_all,
                        weekly_result_df,
                        item,
                        location,
                        quality,
                        month_func,
                        left_iqr,
                        right_iqr,
                        data_key='monthly_data'
                    )   
                    data_key = 'left_iqr'
                    data = int(left_iqr)
                    df_all.at[idx, data_key] = data
                    
                    data_key = 'right_iqr'
                    data = int(right_iqr)
                    df_all.at[idx, data_key] = data

                    cur_time = dt.utcnow()
                    temp_df = monthly_result_df.copy()
                    if temp_df.empty:
                        df_all.drop([idx],inplace=True)
                        df_all.reset_index(drop=True,inplace=True)
                        continue
                    temp_df = temp_df.loc[temp_df.timestamp + td(days=avg_days+1) > cur_time,:]
                
                    if not temp_df.empty:
                        data_key = 'avg_item_count'.format(avg_days)
                        data = np.round(temp_df.item_count.mean())
                        df_all.at[idx, data_key] = data

                        data_key = 'avg_price'.format(avg_days)
                        data = np.sum(temp_df.item_count*temp_df.avg_price)\
                            /(np.sum(temp_df.item_count))
                        df_all.at[idx, data_key] = int(data)
                    else:
                        print('no new data for {} on {}'.format(item,location))
                

    
    # df_all = pd.merge(pd.merge(daily_df_raw.rename(columns={'data': 'daily_data'}),
    #     weekly_df_raw.rename(columns={'data': 'weekly_data'}), how = 'outer'),
    #     monthly_df_raw.rename(columns={'data': 'monthly_data'}), how = 'outer')

    return df_raw, df_all

