import dash
from dash import html, dcc, Input, Output, callback, State
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
#from dash_bootstrap_templates import ThemeSwitchAIO
from mysql_connect_funcs import get_df_tblName, get_df_query
from flask import Flask

df = get_df_tblName("metadataTBL")
df = df.drop_duplicates()
df['label'] = df['symbol'] + ': ' + df['name'] + ' (' + df['exchange'] + ')'
df['value'] = df['symbol'] + '_' + df['country']
label = df['label'].to_list()
value = df['value'].to_list()

options = [{"label": lbl, "value": val} for lbl, val in zip(label, value)]

server = Flask(__name__)

app = dash.Dash(__name__, server=server, use_pages=True, external_stylesheets=[dbc.themes.SPACELAB])
#app = dash.Dash(__name__, use_pages=True, external_stylesheets=[dbc.themes.SPACELAB])


sidebar = html.Div(
    [
        html.H4("SiteName", className="display-4"),
        html.Hr(),
        html.P(
            "A simple sidebar layout with navigation links", className="lead"
        ),
        dbc.Nav(
            [
                dbc.NavLink(
                    [
                        html.Div(page["name"], className="ms-2"),
                    ],
                    href=page["path"],
                    active="exact",
                )
                for page in dash.page_registry.values()
            ],
            vertical=True,
            pills=True,
        ),
    ],
    style={'position':'sticky', 'top':'0', 'height':'100vh'},
)

app.layout = dbc.Container([
    dcc.Location(id='url', refresh=True),
    dcc.Store(id="ticker", storage_type='session',data={}),
    dcc.Store(id='single_ticker_metadata', storage_type='session', data={}),
    dbc.Row(
        [
            dbc.Col([sidebar], width=2, className='column_left', style={'background-color': '#f8f9fa'}),

            dbc.Col([dbc.Row([dbc.Row(dcc.Dropdown(id="my-dynamic-dropdown", placeholder="Search..."))],style={'background-color': 'black', 'position': 'sticky', 'top':'0', 'z-index':'100', 'padding-top': '20px', 'padding-bottom': '27px'}),
                     dbc.Row([dash.page_container],style={'padding-top': '20px'})], width=10)
        ]
    )
], fluid=True)

@callback(
    Output("my-dynamic-dropdown", "options"),
    Input("my-dynamic-dropdown", "search_value")
)
def update_options(search_value):
    if not search_value:
        raise PreventUpdate
    return [o for o in options if search_value.lower() in o["label"].lower()]

@callback(
    Output("ticker", "data"),
    [Input("my-dynamic-dropdown", "value"),
     Input('url', 'search')],
    State("ticker", "data")
)
def get_stockID(dropdown, url, store_state):
    if dropdown:
        return dropdown
    elif url:
        return url[6:]
    else:
        if store_state:
            return store_state
        else:
            return 'TPG_AU'

@callback(
    Output("single_ticker_metadata", "data"),
    Input("ticker", "data"),
)
def meta_data_store(ticker):
    if ticker is None:
        ticker = "TPG_AU"
    symbol = ticker[0:-3]
    query = "SELECT * FROM metadataTBL WHERE symbol = " + "'" + symbol + "'"
    df = get_df_query(query)
    dict = df.to_dict()
    return dict


@callback(
    Output('url', 'href'),
    Input("my-dynamic-dropdown", "value")
)
def update_url(value):
    if value:
        return f'/02-companyoverview?data={value}'



if __name__ == "__main__":
    app.run(debug=False)
