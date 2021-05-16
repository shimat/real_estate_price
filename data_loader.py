import geopandas as gpd
import numpy as np
import pandas as pd
import streamlit as st
import requests
import io


class DataLoader:
    @staticmethod
    @st.cache
    def load_coordinates_csv(file_name: str):
        csv = pd.read_csv(
            file_name,
            # encoding="SHIFT-JIS",
            header=0,
            usecols=['都道府県名',
                     '市区町村名',
                     '大字町丁目名',
                     '緯度',
                     '経度'])
        return csv

    @staticmethod
    @st.cache
    def load_real_estate_csv(file_name: str):
        csv = pd.read_csv(
            file_name,
            header=0,
            usecols=['No',
                     '種類',
                     '都道府県名',
                     '市区町村名',
                     '地区名',
                     '最寄駅：名称',
                     # '最寄駅：距離（分）',
                     '取引価格（総額）',
                     # '間取り',
                     '面積（㎡）',
                     # '建築年',
                     # '建物の構造',
                     # '用途',
                     # '都市計画',
                     # '建ぺい率（％）',
                     # '容積率（％）',
                     '取引時点',
                     # '改装'
                     ])
        # csv = csv[csv['市区町村名'].str.contains('札幌市')]
        # csv = csv[csv['種類'] == '中古マンション等']
        # csv['最寄駅：距離（分）'] = pd.to_numeric(csv["最寄駅：距離（分）"], errors='coerce')
        csv['面積（㎡）'] = csv['面積（㎡）'].str.replace('㎡以上', '')
        csv['面積（㎡）'] = pd.to_numeric(csv["面積（㎡）"], errors='coerce')
        csv['取引時点'] = csv["取引時点"].str.rstrip("年第１２３４四半期").astype(np.int32)
        #csv = csv.dropna(how='any')
        return csv

    @staticmethod
    @st.cache(allow_output_mutation=True)
    def load_geopandas(file_name: str):
        gdf = gpd.read_file(file_name)
        gdf.drop(columns=['KIGO_I', 'DUMMY1', 'KCODE1'], inplace=True)
        return gdf

    @staticmethod
    @st.cache(allow_output_mutation=True)
    def load_geopandas_from_url(url: str):
        response = requests.get(url).content
        string_io = io.StringIO(response.decode('utf-8'))
        gdf = gpd.read_file(string_io)
        gdf.drop(columns=['KIGO_I', 'DUMMY1', 'KCODE1'], inplace=True)
        return gdf
