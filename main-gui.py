import flet
from flet import Container, Page, Row, Text, alignment, colors, Dropdown, dropdown
from flet import Column
import pandas as pd


import matplotlib
from flet.matplotlib_chart import MatplotlibChart

from common.history_utils import *
from common.prices_utils import *
from common.plt_utils import *
from common.get_item_names import *

class MyDataframes:
    def __init__(self):
        self.df = pd.read_json('items\item_categories.json')
        self.df2 = pd.DataFrame()
        self.df_all = pd.DataFrame()
        self.df_all_prices = pd.DataFrame()

class MyLists:
    def __init__(self):
        self.item_list = []
        self.item_names = []

matplotlib.use("svg")

URL_NAME = "https://www.albion-online-data.com/api/v2/stats/"

royal_cities = ['Thetford', 'Lymhurst', 'Bridgewatch', 'Martlock', 'Fort Sterling']

def main(page: Page):
    page.title = "Albion Market Prices"
    page.horizontal_alignment = "center"
    page.vertical_alignment = "center"
    page.window_maximized = True

    mydf = MyDataframes()
    mylist = MyLists()

    fig, _ = plt.subplots()
    charts1 = MatplotlibChart(fig, expand=True, visible=False)
    fig2, _ = plt.subplots()
    charts2 = MatplotlibChart(fig2, expand=True, visible=False)
    
    def get_category(e):
        category = color_dropdown.value
        idx = mydf.df.index[mydf.df['text'] == category].tolist()[0]
        mydf.df2 = pd.DataFrame(mydf.df.iloc[idx]['nodes'])
        color_dropdown2.options = [dropdown.Option(item) for item in mydf.df2['text']]
        print(mydf.df2)
        page.update()

    def get_item(e):
        out_text.value = 'Wait for Processing (takes up to 60 seconds)'
        page.update()
        subcategory = color_dropdown2.value
        idx = mydf.df2.index[mydf.df2['text'] == subcategory].tolist()[0]
        href = mydf.df2.iloc[idx]['href']
        mylist.item_list = get_itemlist(href)
        mylist.item_names = get_item_names(mylist.item_list)
        
        color_dropdown3.options = [dropdown.Option(item) for item in mylist.item_names]
        
        quality_list = [1]
        _, df_all_history = process_history_data(
            mylist.item_list,
            royal_cities,
            quality_list,
            avg_days=14
        )

        mydf.df_all_prices = process_prices_data(
            mylist.item_list,
            royal_cities,
            quality_list
        )

        mydf.df_all = pd.merge(df_all_history, mydf.df_all_prices, how='outer')
        out_text.value = 'You can continue'
        page.update()

    def button_clicked(e):
        item_name = color_dropdown3.value
        idx = mylist.item_names.index(item_name)
        item_name = mylist.item_list[idx]
        print(item_name)
        fig = plot_all_cities(mydf.df_all, item_name, royal_cities, quality=1, no_days=28)
        charts1.figure = fig
        charts1.visible = True
        out_text.value = 'Wait for new Resource type'
        out_text2.value = str(mydf.df_all_prices[mydf.df_all_prices['item_id']==item_name])
        color_dropdown4.options = [dropdown.Option(item) for item in royal_cities]

        page.update()

    def button_clicked2(e):
        plot_city = color_dropdown4.value
        item_name = color_dropdown3.value
        idx = mylist.item_names.index(item_name)
        item_name = mylist.item_list[idx]

        fig2 = plot_one_city(mydf.df_all, item_name, plot_city, quality=1, no_days=14)
        charts2.figure = fig2
        charts2.visible = True
        page.update()

    color_dropdown = Dropdown(
        on_change=get_category,
        width=100,
        options=[dropdown.Option(item) for item in mydf.df['text']],
    )

    color_dropdown2 = Dropdown(
        on_change=get_item,
        width=100,
        options=[],
    )

    color_dropdown3 = Dropdown(
        on_change=button_clicked,
        width=100,
        options=[],
    )

    color_dropdown4 = Dropdown(
        on_change=button_clicked2,
        width=100,
        options=[],
    )
    out_text = Text()
    out_text2 = Text()

    Row1 = Row(
        [
            Container(
                content=color_dropdown,
                margin=10,
                padding=10,
                alignment=alignment.center,
                width=150,
                height=150,
                border_radius=10,
            ),
            Container(
                content=color_dropdown2,
                margin=10,
                padding=10,
                alignment=alignment.center,
                width=150,
                height=150,
                border_radius=10,
            ),
            Container(
                content=color_dropdown3,
                margin=10,
                padding=10,
                alignment=alignment.center,
                width=150,
                height=150,
                border_radius=10,
            ),
            Container(
                content=color_dropdown4,
                margin=10,
                padding=10,
                alignment=alignment.center,
                width=150,
                height=150,
                border_radius=10,
            ),
        ],
        alignment="center",
    )
    Row2= Row(
        [
            Container(
                content=charts1,
                margin=10,
                padding=10,
                alignment=alignment.center,
                bgcolor=colors.BLUE_200,
                width=600,
                height=480,
                border_radius=10,
            ),
            Container(
                content=charts2,
                margin=10,
                padding=10,
                alignment=alignment.center,
                bgcolor=colors.BLUE_200,
                width=600,
                height=480,
                border_radius=10,
            ),
        ],
        alignment="center",
    )

    Row3 = Row(
        [
            Container(
                content=out_text,
                margin=10,
                padding=10,
                alignment=alignment.center,
                width=450,
                height=150,
                border_radius=10,
            ),
            Container(
                content=out_text2,
                margin=10,
                padding=10,
                alignment=alignment.center,
                width=600,
                height=150,
                border_radius=10,
            ),
        ],
        alignment="center"
    )

    page.add(Column([Row1, Row2, Row3]))         

flet.app(target=main)