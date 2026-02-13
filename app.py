import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output, State
import plotly.express as px
import pandas as pd
import json
import requests

# Load GeoJSON from URL
geojson_url = "https://raw.githubusercontent.com/EugeneBorshch/ukraine_geojson/master/UA_FULL_Ukraine.geojson"
response = requests.get(geojson_url)
geojson = json.loads(response.text)

# Sample static data (adjust names to match GeoJSON properties['name'])
data = {
    'Oblast': [
        'Kyiv', 'Poltava Oblast', 'Dnipropetrovsk Oblast', 'Zaporizhzhia Oblast',
        'Lviv Oblast', 'Kharkiv Oblast', 'Odessa Oblast', 'Vinnytsia Oblast',
        'Donetsk Oblast', 'Cherkasy Oblast', 'Chernihiv Oblast', 'Chernivtsi Oblast',
        'Ivano-Frankivsk Oblast', 'Kherson Oblast', 'Khmelnytskyi Oblast',
        'Kirovohrad Oblast', 'Luhansk Oblast', 'Mykolaiv Oblast', 'Rivne Oblast',
        'Sumy Oblast', 'Ternopil Oblast', 'Volyn Oblast', 'Zakarpattia Oblast',
        'Zhytomyr Oblast', 'Autonomous Republic of Crimea'
    ],
    'GDP_per_capita_USD': [
        15904, 5100, 4800, 3728, 3518, 3259, 3225, 2900,
        1870, 2500, 2200, 2400, 2800, 2000, 2600, 2300, 1800, 2700, 2100, 2500, 2400, 2300, 2800, 2600, 1500
    ],  # Approximate values for completeness
    'Population': [
        2950000, 1370000, 3100000, 1650000, 2480000, 2600000, 2350000, 1520000,
        4100000, 1200000, 950000, 850000, 1350000, 1000000, 1230000, 900000, 2100000, 1100000, 1140000, 1030000, 1030000, 1030000, 1240000, 1240000, 900000
    ]  # Approximate values
}
df = pd.DataFrame(data)

# Initialize the Dash app with Bootstrap for better styling
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Layout
app.layout = dbc.Container([
    dcc.Tabs([
        dcc.Tab(label='Interactive Dashboard', children=[
            html.H1("Interactive Ukraine Dashboard"),
            
            # Text information
            html.P("This dashboard displays an interactive map of Ukraine's oblasts. Select an indicator to color the map. Click on an oblast to view details in the side panel."),
            
            # Filter: Dropdown for indicator
            dbc.Row([
                dbc.Col([
                    html.Label("Select Indicator:"),
                    dcc.Dropdown(
                        id='indicator-dropdown',
                        options=[
                            {'label': 'GDP per Capita (USD)', 'value': 'GDP_per_capita_USD'},
                            {'label': 'Population', 'value': 'Population'}
                        ],
                        value='GDP_per_capita_USD'
                    )
                ], width=4)
            ]),
            
            # Interactive Map
            dcc.Graph(id='ukraine-map', style={'height': '600px'}),
            
            # Side panel (Offcanvas) for details
            dbc.Offcanvas(
                id="oblast-details",
                title="Oblast Details",
                is_open=False,
                placement="end",  # Side panel on the right
                style={"width": "25%"}  # 1/4 of the screen
            ),
            
            # Image Carousel (Slider with images)
            html.H3("Image Gallery"),
            dbc.Carousel(
                items=[
                    {"key": "1", "src": "https://example.com/image1.jpg", "caption": "Image 1"},
                    {"key": "2", "src": "https://example.com/image2.jpg", "caption": "Image 2"},
                    {"key": "3", "src": "https://example.com/image3.jpg", "caption": "Image 3"}
                ],
                controls=True,
                indicators=True,
                interval=2000,
                ride="carousel"
            ),
            
            # Static images
            html.H3("Static Images"),
            html.Img(src="https://example.com/static-image.jpg", style={'width': '50%'})
        ]),
        
        dcc.Tab(label='Static Page 1', children=[
            html.H1("Static Information Page"),
            html.P("This is a static page with textual information."),
            html.P("You can add more content here, such as reports or descriptions."),
            html.Img(src="https://example.com/another-image.jpg", style={'width': '100%'})
        ]),
        
        dcc.Tab(label='Static Page 2', children=[
            html.H1("Another Static Page"),
            html.P("Additional static content goes here.")
        ])
    ])
], fluid=True)

# Callback to update the map based on selected indicator
@app.callback(
    Output('ukraine-map', 'figure'),
    Input('indicator-dropdown', 'value')
)
def update_map(indicator):
    fig = px.choropleth_mapbox(
        df,
        geojson=geojson,
        locations='Oblast',  # Match with properties['name'] in GeoJSON
        featureidkey='properties.name',  # Assuming the key in GeoJSON is 'name'
        color=indicator,
        mapbox_style="carto-positron",
        zoom=4,
        center={"lat": 48.3794, "lon": 31.1656},
        color_continuous_scale="YlGnBu",
        labels={indicator: indicator}
    )
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    return fig

# Callback to handle click on map and show details in offcanvas
@app.callback(
    [Output('oblast-details', 'is_open'),
     Output('oblast-details', 'children')],
    [Input('ukraine-map', 'clickData')],
    [State('oblast-details', 'is_open')]
)
def toggle_offcanvas(clickData, is_open):
    if clickData:
        oblast = clickData['points'][0]['location']
        details = df[df['Oblast'] == oblast].iloc[0]
        content = [
            html.P(f"Oblast: {oblast}"),
            html.P(f"GDP per Capita (USD): {details['GDP_per_capita_USD']}"),
            html.P(f"Population: {details['Population']}")
            # Add more details or charts here
        ]
        return True, content
    return is_open, []

if __name__ == '__main__':
    app.run_server(debug=True)
