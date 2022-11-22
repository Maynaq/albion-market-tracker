import requests

import re
import json
from bs4 import BeautifulSoup
import pandas as pd

albion_url = 'https://www.albiononline2d.com'

def get_itemlist(href):
    url = albion_url + href
    soup = BeautifulSoup(requests.get(url).content, 'html.parser')

    # select <script> tag of interest
    s = soup.find(lambda t: t.name == 'script' and 'var config' in t.text) 
    t = re.search(r'var config = (\{.*\});', s.text)[1]
    items = json.loads(t)['itemsForMarketData']
    items_list = items.split(',')
    return items_list    

def update_categories(): 
    urls = albion_url + '/en/item/'
    soup = BeautifulSoup(requests.get(urls).content, 'html.parser')

    # select <script> tag of interest
    s = soup.find(lambda t: t.name == 'script' and 'var config' in t.text) 
    t = re.search(r'var config = (\{.*\});', s.text)[1]
    a = json.loads(t)['categoriesTree']
    return pd.DataFrame(a)
    
df = update_categories()

# saves file
df.to_json('items\item_categories.json', orient='records')

# df2 = pd.read_json('items\item_categories.json')