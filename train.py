from sklearn.linear_model import LinearRegression

"""
X = df[['最寄駅：距離（分）']]
y = df[['取引価格（総額）']]

st.write(X)
st.write(y)
st.write(str(type(X)))
st.write(str(type(y)))

model = LinearRegression()
model.fit(X, y)
y_pred = model.predict([[1],[2],[3],[4],[5],[7],[10],[15],[20]])
st.write(y_pred)
"""

"""
st.vega_lite_chart(df, {
    'width': 600,
    'height': 600,
    'mark': {'type': 'circle', 'tooltip': True},
    'encoding': {
        'x': {'field': '最寄駅：距離（分）', 'type': 'quantitative'},
        'y': {'field': '取引価格（総額）', 'type': 'quantitative'},
     },
})

st.vega_lite_chart(df, {
    'width': 600,
    'height': 600,
    'mark': {'type': 'circle', 'tooltip': True},
    'encoding': {
        'x': {'field': '面積（㎡）', 'type': 'quantitative'},
        'y': {'field': '取引価格（総額）', 'type': 'quantitative'},
     },
})
"""