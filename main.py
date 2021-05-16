import geopandas as gpd
import numpy as np
import pandas as pd
import pydeck
import streamlit as st
from converter import Converter
from data_loader import DataLoader


REAL_ESTATE_CSV_FILE_NAME = "data/不動産情報_北海道.csv"
COORDINATES_CSV_FILE_NAME = "data/位置情報.csv"


st.set_page_config(layout="wide")

area = st.sidebar.selectbox('地域',
                            ('札幌市中央区', '札幌市東区', '札幌市西区', '札幌市南区', '札幌市北区',
                             '札幌市豊平区', '札幌市清田区', '札幌市白石区', '札幌市厚別区', '札幌市手稲区',
                             '函館市', '小樽市', '旭川市', '室蘭市', '釧路市', '帯広市', '北見市',
                             '夕張市', '岩見沢市', '網走市', '留萌市', '苫小牧市', '稚内市', '美唄市',
                             '芦別市', '江別市', '赤平市', '紋別市', '士別市', '名寄市', '三笠市', '根室市',
                             '千歳市', '滝川市', '砂川市', '歌志内市', '深川市', '富良野市', '登別市',
                             '恵庭市', '伊達市', '北広島市', '石狩市', '北斗市', ))
kind = st.sidebar.selectbox('種類', ('中古マンション等', '宅地(土地)', '宅地(土地と建物)', '農地', '林地'))
aggregation_period = st.sidebar.radio("集計期間", ('全期間(2005-2020)', '2005-2009', '2010-2014', '2015-2020'))
aggregation_mode = st.sidebar.radio('集計方法', ('mean', 'median', 'max', 'min'))
st.title(f'北海道不動産取引価格集計 ({area})')
st.markdown("マンションは70m&#178;、土地は1坪(約3.3m&#178;)単位で換算した価格で集計しています")
if kind == '中古マンション等':
    unit_str = "70m&#178;"
    unit_value = 70
else:
    unit_str = '坪'
    unit_value = 400 / 121

# 座標
df_pos = DataLoader.load_coordinates_csv(COORDINATES_CSV_FILE_NAME)
pos = df_pos[df_pos['市区町村名'].str.startswith(area)].iloc[0]
# st.write(pos)

# 物件の絞り込み
df_rs = DataLoader.load_real_estate_csv(REAL_ESTATE_CSV_FILE_NAME).copy()
df_rs = df_rs[df_rs['市区町村名'].str.startswith(area)]
#st.write(df_rs)
df_rs = df_rs[df_rs['種類'].str.startswith(kind)]
# st.write(df_rs)


df_rs['単位換算取引価格'] = (df_rs['取引価格（総額）'] * (unit_value / df_rs['面積（㎡）'])).astype(np.int64)
# st.write(df_rs.head())
price_max = df_rs[['地区名', '単位換算取引価格']].groupby('地区名').agg('mean')['単位換算取引価格'].max()
if np.isnan(price_max):
    price_max = 1

if aggregation_period == '全期間(2005-2020)':
    df_rs_target = df_rs
elif aggregation_period == '2005-2009':
    df_rs_target = df_rs[(2005 <= df_rs['取引時点']) & (df_rs['取引時点'] < 2010)]
elif aggregation_period == '2010-2014':
    df_rs_target = df_rs[(2010 <= df_rs['取引時点']) & (df_rs['取引時点'] < 2014)]
else:
    df_rs_target = df_rs[(df_rs['取引時点'] >= 2015)]
# st.write(df_rs_target)

df_area_groups = df_rs_target[['地区名', '単位換算取引価格']].groupby('地区名')
df_price_by_area = df_area_groups.agg(aggregation_mode).astype(np.int64)
df_count_by_area = df_area_groups.count().rename(columns={'単位換算取引価格': 'count'})
# st.write(df_count_by_area)


gdf = DataLoader.load_geopandas_from_url(f"https://raw.githubusercontent.com/shimat/geodata/main/geojson/{area}_geo.json").copy()
# st.write(gdf.head())
# gdf = gdf.assign(bg_color=[[0, 0, 0, 0] for _ in range(len(gdf))])

gdf['price'] = 0
gdf['count'] = 0

for index, row in df_price_by_area.iterrows():
    if area == '名寄市':
        area_to_match = index  # TODO: 住所が変更された模様, マッチしない
    else:
        area_to_match = Converter.replace_area_number_to_kansuji(index)
    # st.write(index, area_to_match)
    price = row["単位換算取引価格"]
    count = df_count_by_area["count"].get(index, 0)
    gdf.loc[gdf['S_NAME'].str.startswith(area_to_match), 'price'] = price
    gdf.loc[gdf['S_NAME'].str.startswith(area_to_match), 'count'] = count

gdf['norm_price'] = (gdf['price']) / price_max
gdf['elevation'] = gdf['norm_price'] * 3000
gdf['bg_color'] = gdf['norm_price'].apply(lambda x: [255, 256 * (1 - x), 0 * (1 - x)])
gdf['format_price'] = gdf['price'].apply(lambda x: '{0:,}'.format(int(x)))
# st.write(gdf.head())

st.header("取引価格マップ")
geojson_layer = pydeck.Layer(
    'GeoJsonLayer',
    gdf,
    opacity=0.5,
    stroked=True,
    filled=True,
    extruded=True,
    wireframe=True,
    get_fill_color='bg_color',
    get_position="geometry",
    get_elevation='elevation',
    # get_line_color=[0, 0, 0, 192],
    get_line_width=1,
    pickable=True,
    get_color=[0, 255, 0],
    get_text='S_NAME',
)
st.pydeck_chart(pydeck.Deck(
    map_style='mapbox://styles/mapbox/streets-v11',
    initial_view_state=pydeck.ViewState(
        latitude=pos['緯度'],
        longitude=pos['経度'],
        zoom=10.5,
        pitch=50,
    ),
    layers=[
        geojson_layer
    ],
    tooltip={"html": f"""
<b>{{S_NAME}}</b>
<ul style="display:inline;list-style:none;">
<li>価格({aggregation_mode}): ￥{{format_price}}/{unit_str}</li>
<li>取引数: {{count}} </li>
</ul>"""},
))

st.header("対象データ 統計")
st.write(df_rs_target.drop(columns=["No"]).describe())

st.markdown("""
<style>
div.xx-small-font dt,dd,a {
    font-size:xx-small !important;
}
</style>
""", unsafe_allow_html=True)
st.sidebar.markdown("""
-----
<p>GitHub</p>
<p><a href="https://github.com/shimat/RealEstatePrice">https://github.com/shimat/RealEstatePrice</a></p>
<p>出典</p>
<div class="xx-small-font">
<dl>
<dt>不動産取引価格データ</dt>
<dd>不動産取引価格情報ダウンロードサービス
(<a href="https://www.land.mlit.go.jp/webland/servlet/MainServlet">https://www.land.mlit.go.jp/webland/servlet/MainServlet</a>)</dd>
<dt>地区境界データ</dt>
<dd>『国勢調査町丁・字等別境界データセット』（CODH作成） 「平成27年国勢調査町丁・字等別境界データ」（NICT加工）
(<a href="https://geoshape.ex.nii.ac.jp/ka/">https://geoshape.ex.nii.ac.jp/ka/</a>)</dd>
</dl>
</div>
""", unsafe_allow_html=True)

# st.write('マンション情報', df_rs)
# st.write(df_rs.dtypes)
# st.write('地区ごとの平均価格', df_result)
# st.write(gdf.head())
