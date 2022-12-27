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

matplotlib.use("svg")

URL_NAME = "https://www.albion-online-data.com/api/v2/stats/"

royal_cities = ['Thetford', 'Lymhurst', 'Bridgewatch', 'Martlock', 'Fort Sterling']
item_name = ["T7_ORE"]

city_and_portals = add_portals(royal_cities)

def main(page: Page):
    page.title = "Containers - clickable and not"
    page.horizontal_alignment = "center"
    page.vertical_alignment = "center"

    mydf = MyDataframes()
    fig, ax = plt.subplots()
    charts1 = MatplotlibChart(fig, expand=True, visible=False)

    color_dropdown = Dropdown(
        width=100,
        options=[dropdown.Option(item) for item in df['text']],
    )

    color_dropdown2 = Dropdown(
        width=100,
        options=[],
    )

    color_dropdown3 = Dropdown(
        width=100,
        options=[],
    )

    out_text = Text()
    out_text2 = Text()

    def get_category(e):
        category = color_dropdown.value
        idx = df.index[df['text'] == category].tolist()[0]
        mydf.df2 = pd.DataFrame(df.iloc[idx]['nodes'])
        color_dropdown2.options = [dropdown.Option(item) for item in mydf.df2['text']]
        print(mydf.df2)
        page.update()

    def get_item(e):
        out_text.value = 'Wait for Processing'
        page.update()
        subcategory = color_dropdown2.value
        idx = mydf.df2.index[mydf.df2['text'] == subcategory].tolist()[0]
        href = mydf.df2.iloc[idx]['href']
        item_list = get_itemlist(href)

        color_dropdown3.options = [dropdown.Option(item) for item in item_list]

        _, df_all_history = process_history_data(
            item_list,
            royal_cities,
            quality_list=[1],
            avg_days=14
        )

        mydf.df_all_prices = get_prices_data(item_list, city_and_portals)
        mydf.df_all = pd.merge(df_all_history, mydf.df_all_prices, how='outer')
        out_text.value = 'You can continue'
        page.update()

    def button_clicked(e):
        item_name = color_dropdown3.value
        print(item_name)
        fig = plot_all_cities(mydf.df_all, item_name, royal_cities, quality=1, no_days=28)
        charts1.figure = fig
        charts1.visible = True
        out_text.value = 'Wait for new Resource type'
        out_text2.value = str(mydf.df_all_prices[mydf.df_all_prices['item_id']==item_name])
        page.update()

    page.add(
        Column(
                [
                Row(
                    [
                        Container(
                            content=color_dropdown,
                            margin=10,
                            padding=10,
                            alignment=alignment.center,
                            bgcolor=colors.AMBER,
                            width=150,
                            height=150,
                            border_radius=10,
                            on_click=get_category,
                        ),
                        Container(
                            content=color_dropdown2,
                            margin=10,
                            padding=10,
                            alignment=alignment.center,
                            bgcolor=colors.GREEN_200,
                            width=150,
                            height=150,
                            border_radius=10,
                            on_click=get_item,
                        ),
                        Container(
                            content=color_dropdown3,
                            margin=10,
                            padding=10,
                            alignment=alignment.center,
                            bgcolor=colors.BLUE_200,
                            width=150,
                            height=150,
                            border_radius=10,
                            on_click=button_clicked,
                        ),
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
                    ],
                    alignment="center",
                ),
                Row(
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
                    alignment="center",
                ),
            ],
            

        )
        
    )

flet.app(target=main)