import requests

import re
import json
from bs4 import BeautifulSoup
import pandas as pd

albion_url = 'https://www.albiononline2d.com'
common_tags = ['Uncommon', 'Rare', 'Exceptional', 'Pristine']
common_tags2 = ['Adept\'s', 'Expert\'s', 'Master\'s', 'Grandmaster\'s', 'Elder\'s']

def get_itemlist(href: str) -> list:
    """Extract a list of items from a webpage specified by the `href` parameter.

    Args:
        href: The relative URL of the webpage to scrape.

    Returns:
        item_list: A list of items extracted from the webpage.
    """

    url = albion_url + href + '?tier=4'
    soup = BeautifulSoup(requests.get(url).content, 'html.parser')

    # select <script> tag of interest
    s = soup.find(lambda t: t.name == 'script' and 'var config' in t.text) 
    t = re.search(r'var config = (\{.*\});', s.text)[1]
    items = json.loads(t)['itemsForMarketData']
    item_list = items.split(',')
    #  
    item_list = [s.replace('@0', '') for s in item_list]
    new_item_list = []
    for count in range(len(item_list)):
        if count%5==0:
            cur_list = item_list[count:count+5] 
            for i in range(4,9):
                temp_list = [s.replace('T4', 'T' + str(i)) for s in cur_list]
                for temp_item in temp_list:
                    new_item_list.append(temp_item)

    return new_item_list    

def get_item_names(item_list: list) -> list:

    item_names_list = []
    all_items = pd.read_json('items\items.json')
    for item in item_list:
        df = all_items[all_items['UniqueName']==item]
        item_name = df['LocalizedNames'].item()['EN-US']
        for tags in (common_tags + common_tags2):
            item_name = item_name.replace(tags, '')
        if item[-2] != '@':
            item_name = item[:2] + '.0' + item_name
        else:
            item_name = item[:2] + '.' + item[-1] + '' + item_name 

        item_names_list.append(item_name)
    return item_names_list

def update_categories(): 
    urls = albion_url + '/en/item/'
    soup = BeautifulSoup(requests.get(urls).content, 'html.parser')

    # select <script> tag of interest
    s = soup.find(lambda t: t.name == 'script' and 'var config' in t.text) 
    t = re.search(r'var config = (\{.*\});', s.text)[1]
    a = json.loads(t)['categoriesTree']
    df = pd.DataFrame(a)
    df.to_json('items\item_categories.json', orient='records')
    return df

def update_item_list():
    url = "https://raw.githubusercontent.com/broderickhyman/ao-bin-dumps/master/formatted/items.txt"
    res = requests.get(url)
    file = open('items\items.txt', 'w', encoding="utf-8")
    file.write(res.text)
    file.close()

    url = "https://raw.githubusercontent.com/broderickhyman/ao-bin-dumps/master/formatted/items.json"
    df = pd.read_json(url)
    df.to_json('items\items.json', orient='records')
    return df


update_categories()
update_item_list()
# saves file

# df2 = pd.read_json('items\item_categories.json')