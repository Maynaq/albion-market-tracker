import requests

import re
import json
from bs4 import BeautifulSoup
import pandas as pd

def update_categories(): 
    urls = 'https://www.albiononline2d.com/en/item/'
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