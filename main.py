from common.history_utils import *
from common.prices_utils import *

from common.plt_utils import * 
import sys
import os
# TO-DO LIST 
# 0. Flipping
    # Get the average market price for 1 week, calculate the daily item_count
    # Target is %10 of the daily market.
    # Calculate buy order and sell order prices.
# 1. Merge city and portal data
# 2. Merge history and price data 
# 3. Check refining profit with and without focus
# 4. Merge time-scale=1,6,24 data to a one data (for a week lets say)
# 5. Create a (online?) database and get user input
# 6. Compare the database and the api and get the newest data
# 7. Configure item names and database names
# 8. Save data to local and Get data from local, write time data
# 9. Update data from api
# 10. 

URL_NAME = "https://www.albion-online-data.com/api/v2/stats/"

#item_name = ["T7_ORE", "T7_METALBAR"]
royal_cities = ['Thetford', 'Lymhurst', 'Bridgewatch', 'Martlock', 'Fort Sterling']
#qualities = [1,2,3,4,5]
os.startfile("items\\items.txt")
item_name = [input('Enter the item:')]
#qualities = input('Enter the qualities:')
df_raw_history, df_all_history = process_history_data(
    item_name,
    royal_cities,
    quality_list=[1],
    avg_days=14
)

df_all_prices = get_prices_data(item_name, royal_cities, quality_list=[1])

df_all = merger_hist_price(df_all_history, df_all_prices)
plot_all_cities(df_all, item_name[0], royal_cities, quality=1, no_days=28, show=True)

while 1:
    plot_city = int(input('Enter the id (1: Thetford, 2: Lymhurst, 3: Bridgewatch, 4: Martlock, 5: Fort Sterling, 0: Exit): '))

    if plot_city == 0:
        sys.exit()
    elif (plot_city > 0 and plot_city < 6): 
        plot_city = plot_city - 1
    else:
        print('Try again')
        continue
    plot_one_city(df_all, item_name[0], royal_cities[plot_city], quality=1, no_days=14, show=True)

breakpointt = 1

