from common.history_utils import *
from common.prices_utils import *

from common.plt_utils import * 

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

item_name = ["T4_ORE", "T4_ORE_LEVEL1@1", "T4_ORE_LEVEL2@2", "T4_ORE_LEVEL3@3"]
royal_cities = ['Thetford', 'Lymhurst', 'Bridgewatch', 'Martlock', 'Fort Sterling']
qualities = [1,2,3,4,5]
df_raw_history, df_all_history = process_history_data(
    item_name,
    royal_cities,
    qualities,
    avg_days=14
)

city_and_portals = add_portals(royal_cities)
df_all_prices = get_prices_data(item_name, city_and_portals)

df_all = pd.merge(df_all_history, df_all_prices, how='outer')
plot_one_city(df_all, item_name[1], royal_cities[0], quality=1, no_days=14)
plot_all_cities(df_all, item_name[1], royal_cities, quality=1, no_days=28)
breakpointt = 1

