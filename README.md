# RealEstatePrice
**https://share.streamlit.io/shimat/realestateprice/main/main.py**

Streamlit study for visualizing real-estate transaction

## Reference Source
https://www.land.mlit.go.jp/webland/servlet/MainServlet

不動産取引価格情報ダウンロードサービス

https://geoshape.ex.nii.ac.jp/ka/ https://www.e-stat.go.jp/terms-of-use

『国勢調査町丁・字等別境界データセット』（CODH作成） 「平成27年国勢調査町丁・字等別境界データ」（NICT加工）

## Installation
### geopandas (Windows)
https://towardsdatascience.com/geopandas-installation-the-easy-way-for-windows-31a666b3610f
```sh
pip install .\GDAL-3.2.3-cp39-cp39-win_amd64.whl
pip install .\pyproj-3.0.1-cp39-cp39-win_amd64.whl
pip install .\Fiona-1.8.19-cp39-cp39-win_amd64.whl
pip install .\Shapely-1.7.1-cp39-cp39-win_amd64.whl
pip install .\geopandas-0.9.0-py3-none-any.whl
```

### geopandas (Streamlit deployment environment)
https://discuss.streamlit.io/t/shared-streamlit-with-geopandas/7277/7

requirements.txt
```
streamlit
fiona
geopandas
```

packages.txt
```
gdal-bin
python-rtree
```

### TopoJSON -> GeoJSON
https://github.com/topojson/topojson-client/blob/master/README.md#topo2geo

```sh
sudo npm install -g topojson-client

topo2geo town < 清田区.topojson
mv town 清田区_geo.json
```
