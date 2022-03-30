import sys
import os

import streamlit as st
import requests
import pandas as pd

API_SERVER = os.getenv("API_SERVER", default="flask-api")
API_SERVER_PORT = int(os.getenv("API_SERVER_PORT", default=5000))

def get_all_data(provider):
    try:
        r = requests.get(f"http://{API_SERVER}:{API_SERVER_PORT}/api/offers/{provider}")
    except Exception as exc:
        print(f"{exc.__class__.__name__}: {exc}")
        print("Quitting")
        sys.exit(1)

    if r.status_code != 200:
        print(f"Status code {r.status_code}")
        sys.exit(2)

    try:
        data = r.json()
    except Exception as exc:
        print(exc)
        sys.exit(3)
    
    return data


data_nfj = get_all_data("nfj")
data_bdg = get_all_data("bdg")


if not all([data_nfj, data_bdg]):
    print("Problems with API. Quitting...")
    sys.exit(3)

for offer in data_bdg:
    offer['location'] = offer['location'][0]

df_data_nfj = pd.DataFrame(data_nfj)
df_data_bdg = pd.DataFrame(data_bdg)

df_data_nfj.set_index('offer_id', inplace=True)
df_data_bdg.set_index('offer_id', inplace=True)

data_nfj_bar_plot_locations = df_data_nfj['location'].value_counts(dropna=True).drop(['Zdalna', '$+'])
data_bdg_bar_plot_locations = df_data_bdg['location'].value_counts(dropna=True).drop('Remote')


def render_table_chart():
    table, chart = st.columns(2)
    selected = table.selectbox("Source", ("Bulldogjobs", "Nofluffjobs"), help="Select source you want data from")

    def render_helper(df_data, df_data_bar_locations):
        table.dataframe(df_data, height=700, width=1600)
        chart.header("Job offers according to city")
        chart.bar_chart(df_data_bar_locations)

    if selected == 'Bulldogjobs':
        render_helper(df_data_bdg, data_bdg_bar_plot_locations)
    elif selected == 'Nofluffjobs':
        render_helper(df_data_nfj, data_nfj_bar_plot_locations)


st.set_page_config(layout="wide")
st.header("IT Job offers in Poland (as of 22.01.2022)")
render_table_chart()


# ###
# import matplotlib.pyplot as plt

# def wrap_axes(ax, fig):

#     """Put axes (object created by pandas plotting API) inside matplotlib figure."""

#     ax.figure = fig
#     fig.axes.append(ax)
#     fig.add_axes(ax)

#     temp_ax = fig.add_subplot(111)
#     ax.set_position(temp_ax.get_position())
#     temp_ax.remove


# ax = df_bar_plot_locations.plot.barh("Locations", "Offers")
# fig = plt.figure()
# wrap_axes(ax, fig)


# st.header("Job offers according to city (pandas chart)")
# st.pyplot(fig)