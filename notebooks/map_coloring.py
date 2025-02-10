import json
from collections import defaultdict
from random import Random
from IPython.display import display_png, Image

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# Suppress warnings from Plotly.
import warnings
warnings.filterwarnings('ignore')

# Load and filter GeoJSON file.
with open('../data/geojson-counties-fips.json') as f:
    geo = json.load(f)

STATE_UTAH = 49
geo['features'] = [feature for feature in geo['features'] if feature['properties']['STATE'] == str(STATE_UTAH)]
counties = [feature['id'] for feature in geo['features']]
county_names = {feature['id']: feature['properties']['NAME'] for feature in geo['features']}

# Load adjacency data.
nbrs = defaultdict(list)

for index, row in pd.read_csv('../data/county_adjacency2024.txt', delimiter='|').iterrows():
    u = row['County GEOID']
    v = row['Neighbor GEOID']

    if u // 1000 == STATE_UTAH and v // 1000 == STATE_UTAH and u != v:
        nbrs[str(u)] += [str(v)]

# Initialize pseudorandom number generator.
rand = Random(12345)


def show_map(colors, show_png=False):
    color_map = {str(i + 1): px.colors.qualitative.Plotly[i] for i in range(10)}
    color_map['-'] = 'rgba(0,0,0,0)'
    df = pd.DataFrame(colors.items(), columns=['fips', 'color'], dtype=str)  # load as discrete values
    df = df[df['color'] != '0'].sort_values(by=['color'])

    fig = px.choropleth_mapbox(
        df,
        geojson=geo,
        locations='fips',
        color='color',
        color_discrete_map=color_map,
        mapbox_style='carto-positron',
        zoom=5.5,
        center={"lat": 39.5, "lon": -111.55},
        width=500,
        height=500,
        opacity=0.8
    )
    fig.update_layout(
        margin=dict(r=0, t=0, l=0, b=0),
        showlegend=True
    )

    if show_png:
        display_png(Image(fig.to_image('png')))
    else:
        fig.show()
