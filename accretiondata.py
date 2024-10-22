import dash
from dash import Dash, html, dcc

app = Dash(__name__, use_pages=True, suppress_callback_exceptions=True,
           )

app.layout = html.Div([
    html.H1('Accretion Data', style={'color': 'white'}),
    html.Div([
        html.Div(
            dcc.Link(f"{page['title']}", href=page["relative_path"], className='nav-link-style')
        ) for page in dash.page_registry.values()
    ]),
    dash.page_container
])

if __name__ == '__main__':
    # These are the default dash host and ports
    host = '127.0.0.1'
    port = 8050
    # Start the Dash server
    print(f"Dash app is running on http://{host}:{port}/")
    app.run(host=host, port=port, debug=True)
    #app.run(debug=True)
