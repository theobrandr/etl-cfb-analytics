import dash
from dash import html

dash.register_page(__name__, path='/')

layout = html.Div([
    html.H1('Data Analytics for College Football', style={'color': 'white'}),
    #html.Div('Data Analytics for College Football', style={'color': 'white'}),
])