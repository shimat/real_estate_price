import numpy as np
import pandas as pd
import pydeck
import streamlit as st
from converter import Converter
from load_data import load_coordinates_csv, load_real_estate_csv


REAL_ESTATE_CSV_FILE_NAME = "data/マンション情報_札幌.csv"
COORDINATES_CSV_FILE_NAME = "data/位置情報_札幌.csv"

df_pos = load_coordinates_csv(COORDINATES_CSV_FILE_NAME)
st.write('位置', df_pos)

df_rs = load_real_estate_csv(REAL_ESTATE_CSV_FILE_NAME)
st.write('マンション情報', df_rs)

df_rs2020 = df_rs[(df_rs['取引時点'] >= 2010)].copy()
df_rs2020['_70平米換算取引価格'] = (df_rs2020['取引価格（総額）'] * (70 / df_rs2020['面積（㎡）'])).astype(np.int64)

df_area_groups = df_rs2020[['地区名', '_70平米換算取引価格']].groupby('地区名')
st.write('Groups')
df_result = df_area_groups.mean().astype(np.int64)


for index, row in df_result.iterrows():
    #st.write(index, Converter.replace_area_number_to_kansuji(index))
    df_pos_area = df_pos[
        df_pos["大字町丁目名"].str.contains(Converter.replace_area_number_to_kansuji(index))]
    #st.write(df_pos_area)
    #st.write(index, Converter.to_hankaku(index), Converter.replace_area_number_to_kansuji(index), df_pos_area)
    #st.write(df_pos_area[["緯度", "経度"]].mean())
    lat, lon = df_pos_area[["緯度", "経度"]].mean()
    df_result.at[index, '緯度'] = lat
    df_result.at[index, '経度'] = lon
    #st.write(lat, lon)


st.pydeck_chart(pydeck.Deck(
    map_style='mapbox://styles/mapbox/streets-v11',
    width=1200,
    height=800,
    initial_view_state=pydeck.ViewState(
        latitude=43.05,
        longitude=141.35,
        zoom=10.5,
        pitch=50,
    ),
    layers=[
        pydeck.Layer(
            'HeatmapLayer',
            data=df_result,
            get_position='[経度, 緯度]',
            get_weight='_70平米換算取引価格',
            opacity=0.8,
            radius_pixels=70,
            elevation_scale=50,
            elevation_range=[0, 1000],
            threshold=0.03
        )
    ],
))

st.pydeck_chart(pydeck.Deck(
    map_style='mapbox://styles/mapbox/streets-v11',
    initial_view_state=pydeck.ViewState(
        latitude=43.05,
        longitude=141.35,
        zoom=10.5,
        pitch=50,
    ),
    layers=[
        pydeck.Layer(
            'GridLayer',
            data=df_result,
            get_position='[経度, 緯度]',
            get_elevation_weight='_70平米換算取引価格',
            get_fill_color=[255, 0, 0, 255],
            cell_size=500,
            elevation_scale=20,
            elevation_range=[0, 100],
            #pickable=True,
            extruded=True,
        ),
    ],
))