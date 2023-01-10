import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime as dt, timedelta as td
from common.func_utils import *

# TO-DO prices data messes up the graph
# Do something for no data
def plot_one_city(
    df_all: pd.DataFrame,
    item: str,
    city: str,
    quality: int = 1,
    no_days: int = 7,
    show: bool = False
) -> None:

    fig,ax = plt.subplots()

    # set x-axis label
    ax.set_xlabel("timestamps", fontsize=14)
    # set y-axis label
    ax.set_ylabel("avg_price",color="red",fontsize=14)
    # twin object for two different y-axis on the sample plot
    ax2 = ax.twinx()

    if quality == 1:
        quality_name = 'Normal'
    elif quality == 2:
        quality_name = 'Good'
    elif quality == 3:
        quality_name = 'Outstanding'
    elif quality == 4:
        quality_name = 'Excellent'
    elif quality == 5:
        quality_name = 'Masterpiece'
        
    ax2.set_ylabel("item count", color="blue", fontsize=14)

    plt.title(item + ' ' + quality_name + ' quality at ' + city)

    cur_time = dt.utcnow()
    compare_time = cur_time-td(days=no_days)-td(hours=(cur_time-td(days=no_days)).hour+1)

    idx = get_data_index(df_all, item, city, quality)
    if idx is not None:
        daily_df = df_all.loc[idx,:]['daily_data']
        daily_df = daily_df.loc[daily_df.timestamp > compare_time,:]

        weekly_df = df_all.loc[idx,:]['weekly_data']
        weekly_df = weekly_df.loc[weekly_df.timestamp > compare_time,:]

        monthly_df = df_all.loc[idx,:]['monthly_data']
        monthly_df = monthly_df.loc[monthly_df.timestamp > compare_time,:]

        monthly_df['timestamp'] = monthly_df['timestamp']

        # make a plot
        ax.plot(
            daily_df.timestamp,
            daily_df.avg_price,
            color="blue", 
            marker=".",
            linewidth=1,
            alpha=0.25,
            label='daily'
        )

        ax.plot(
            weekly_df.timestamp,
            weekly_df.avg_price,
            color="red", 
            marker="x",
            linewidth=2,
            alpha=0.5, 
            label='weekly'
        )

        ax.plot(
            monthly_df.timestamp,
            monthly_df.avg_price,
            color="green", 
            marker="o",
            linewidth=4,
            label='monthly'
        )

        # make a plot with different y-axis using second axis object
        ax2.bar(
            monthly_df.timestamp,
            monthly_df.item_count,
            color="green",
            alpha=0.2
        )
        ax.legend()

    if show:
        plt.show(block=False)

    return fig

def plot_all_cities(
    df_all: pd.DataFrame,
    item: str,
    royal_cities: list,
    quality: int = 1,
    no_days: int = 7,
    show=False
) -> None:

    fig,ax = plt.subplots()

    plt.grid('on')
    # set x-axis label
    ax.set_xlabel("timestamps", fontsize=14)
    # set y-axis label
    ax.set_ylabel("avg_price", color="red", fontsize=14)
   
    # twin object for two different y-axis on the sample plot
    ax2 = ax.twinx()
    ax2.set_ylabel("item count", color="blue", fontsize=14)

    cur_time = dt.utcnow()
    compare_time = cur_time-td(days=no_days)-td(hours=(cur_time-td(days=no_days)).hour+1)
    for i, city in enumerate(royal_cities):
        idx = get_data_index(df_all, item, city, quality)
        if idx is None:
            continue
        df = df_all.loc[idx]

        weekly_df = df['weekly_data']
        weekly_df = weekly_df.loc[weekly_df.timestamp > compare_time,:]
        
        monthly_df = df['monthly_data']
        monthly_df = monthly_df.loc[monthly_df.timestamp > compare_time,:]
        monthly_df['timestamp'] = monthly_df['timestamp']

        try:
            # make a plot
            color = next(ax._get_lines.prop_cycler)['color']

            p1, = ax.plot(
                weekly_df.timestamp,
                weekly_df.avg_price,
                marker=".",
                linewidth=1,
                color=color,
                label=city
            )
            # make a plot with different y-axis using second axis object
            p2 = ax2.bar(
                monthly_df.timestamp + i*td(hours=3),
                monthly_df.item_count,
                width=td(hours=2),
                alpha=0.25,
                color=color,
                label=city
            )
                
            p3 = ax.hlines(
                xmin=cur_time-td(days=no_days),
                xmax=cur_time,
                y=df.avg_price,
                linewidth=2,
                alpha=0.5,
                colors=color,
                linestyles='--',
                label=city
            )

            p4 = ax.scatter(
                x = df.info_date,
                y = df.price,
                color=color,
                marker='*',
                s=250,
                label=city
            )

        except Exception as e:
            print(e)

    ax2.legend(loc='upper left')
    # l1 = ax.legend(handles = tuple_list,
    #     labels=royal_cities,
    #     loc='upper left',
    #     title='avg prices and item counts', 
    #     handler_map={tuple: HandlerTuple(None)}
    # )
    
    # ax.add_artist(l1)

    # ax.legend(handles = tuple_list2,
    #     labels=royal_cities,
    #     loc='upper right',
    #     title='current prices',
    #     shadow=True,
    #     bbox_to_anchor=(0.2, 1),
    #     handler_map={tuple: HandlerTuple(None)}
    # )

    if quality == 1:
        quality_name = 'Normal'
    elif quality == 2:
        quality_name = 'Good'
    elif quality == 3:
        quality_name = 'Outstanding'
    elif quality == 4:
        quality_name = 'Excellent'
    elif quality == 5:
        quality_name = 'Masterpiece'
    
    plt.title('{} days of '.format(no_days) + item + ' ' + quality_name + ' quality')
    
    if show:
        plt.show(block=False)

    return fig

