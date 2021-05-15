import geopandas as gpd
import numpy as np
import pandas as pd
import pydeck
import streamlit as st
from converter import Converter
from load_data import load_real_estate_csv, load_geopandas

REAL_ESTATE_CSV_FILE_NAME = "data/マンション情報_札幌.csv"

st.set_page_config(layout="wide")

ward = st.sidebar.selectbox('行政区', ('中央区', '東区', '西区', '南区', '北区', '豊平区', '清田区', '白石区', '厚別区', '手稲区'))
aggregation_period = st.sidebar.radio("集計期間", ('全期間(2005-2020)', '2005-2009', '2010-2014', '2015-2020'))
aggregation_mode = st.sidebar.radio('集計方法', ('mean', 'median', 'max', 'min'))
st.title(f'札幌市中古マンション取引価格集計 ({ward})')
st.markdown("一律70m&#178;で換算した価格で集計しています")

df_rs = load_real_estate_csv(REAL_ESTATE_CSV_FILE_NAME).copy()
df_rs = df_rs[df_rs['市区町村名'].str.contains(ward)]
df_rs['70平米換算取引価格'] = (df_rs['取引価格（総額）'] * (70 / df_rs['面積（㎡）'])).astype(np.int64)
#st.write(df_rs.head())
price_max = df_rs[['地区名', '70平米換算取引価格']].groupby('地区名').agg('mean')['70平米換算取引価格'].max()

if aggregation_period == '全期間(2005-2020)':
    df_rs_target = df_rs
elif aggregation_period == '2005-2009':
    df_rs_target = df_rs[(2005 <= df_rs['取引時点']) & (df_rs['取引時点'] < 2010)]
elif aggregation_period == '2010-2014':
    df_rs_target = df_rs[(2010 <= df_rs['取引時点']) & (df_rs['取引時点'] < 2014)]
else:
    df_rs_target = df_rs[(df_rs['取引時点'] >= 2015)]

df_area_groups = df_rs_target[['地区名', '70平米換算取引価格']].groupby('地区名')
df_price_by_area = df_area_groups.agg(aggregation_mode).astype(np.int64)
df_count_by_area = df_area_groups.count().rename(columns={'70平米換算取引価格': 'count'})
#st.write(df_count_by_area)


gdf = load_geopandas(f"data/札幌市{ward}_geo.json").copy()
# gdf = gdf.assign(bg_color=[[0, 0, 0, 0] for _ in range(len(gdf))])

gdf['price'] = 0
gdf['count'] = 0

for index, row in df_price_by_area.iterrows():
    area_name_kansuji = Converter.replace_area_number_to_kansuji(index)
    price = row["70平米換算取引価格"]
    count = df_count_by_area["count"].get(index, 0)
    gdf.loc[gdf['S_NAME'].str.contains(area_name_kansuji), 'price'] = price
    gdf.loc[gdf['S_NAME'].str.contains(area_name_kansuji), 'count'] = count

gdf['norm_price'] = (gdf['price']) / price_max
gdf['elevation'] = gdf['norm_price'] * 3000
gdf['bg_color'] = gdf['norm_price'].apply(lambda x: [255, 256 * (1 - x), 0 * (1 - x)])
gdf['format_price'] = gdf['price'].apply(lambda x: '{0:,}'.format(int(x)))
#st.write(gdf.head())

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
        latitude=43.05,
        longitude=141.35,
        zoom=10.5,
        pitch=50,
    ),
    layers=[
        geojson_layer
    ],
    tooltip={"html": f"""
<b>{{S_NAME}}</b>
<ul style="display:inline;list-style:none;">
<li>価格({aggregation_mode}): ￥{{format_price}} </li>
<li>取引数: {{count}} </li>
</ul>"""},
))

st.header("対象データ 統計")
st.write(df_rs_target.drop(columns=["No"]).describe())

st.markdown("""
<style>
div.small-font dt,dd {
    font-size:xx-small !important;
}
</style>
""", unsafe_allow_html=True)
st.sidebar.markdown("""
-----
<div class="small-font">
<p>出典</p>
<dl>
<dt>マンション取引価格データ</dt>
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
