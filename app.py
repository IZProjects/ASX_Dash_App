import dash
from dash import dcc, Input, Output, callback, State, page_container, clientside_callback, ClientsideFunction
from dash.exceptions import PreventUpdate
from mysql_connect_funcs import get_df_tblName, get_df_query
from flask import Flask
import dash_mantine_components as dmc
from components.header import header
from components.sidebar import sidebar


df = get_df_tblName("metadataTBL")
df = df.drop_duplicates()
df['label'] = df['symbol'] + ': ' + df['name'] + ' (' + df['exchange'] + ')'
df['value'] = df['symbol'] + '_' + df['country']
label = df['label'].to_list()
value = df['value'].to_list()

options = [{"label": lbl, "value": val} for lbl, val in zip(label, value)]


server = Flask(__name__)
dash._dash_renderer._set_react_version("18.2.0")
app = dash.Dash(__name__, server=server, use_pages=True, external_stylesheets=dmc.styles.ALL)
#app = dash.Dash(__name__, use_pages=True, external_stylesheets=dmc.styles.ALL])


layout = dmc.AppShell(
    [
        dcc.Location(id='url', refresh=True),
        dcc.Store(id="ticker", storage_type='session', data={}),
        dcc.Store(id='single_ticker_metadata', storage_type='session', data={}),
        dmc.AppShellHeader(header, style={'padding-left': '20px', 'padding-right': '20px', 'padding-top': '10px'}),
        dmc.AppShellNavbar(sidebar, style={'padding-left': '10px', 'padding-right': '10px', 'padding-top': '20px'}),
        dcc.Loading([
            dmc.AppShellMain(page_container),
        ], style={"position":"absolute", "top":"20%"})
    ],
    header={"height": 48},
    navbar={"width": 250, "breakpoint": "sm", "collapsed": {"mobile": True}},
    padding="md",
    id="appshell",
)

app.layout = dmc.MantineProvider(id="mantine-provider",children=[layout])


clientside_callback(
    ClientsideFunction(
        namespace='clientside',
        function_name='side_bar_toggle'
    ),
    Output("appshell", "navbar"),
    Input("burger-button", "opened"),
    State("appshell", "navbar"),
)

clientside_callback(
    """
    function(path, opened) {
        if (opened) {
            return !opened;
        }
        return opened;
    }
    """,
    Output("burger-button", "opened"),
    Input("url", "pathname"),
    State("burger-button", "opened"),
    prevent_initial_call=True
)

clientside_callback(
    ClientsideFunction(
        namespace='clientside',
        function_name='theme_switcher_callback'
    ),
    Output("mantine-provider", "theme"),
    Output("mantine-provider", "forceColorScheme"),
    Output("color-scheme-toggle", "rightSection"),
    Output("color-scheme-toggle", "label"),
    Input("color-scheme-toggle", "n_clicks")
)

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
