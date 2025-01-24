import dash
from dash import dcc, html, callback, Output, Input, dash_table
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import dash_mantine_components as dmc
from src.mysql_connect_funcs import get_df_tblName, get_df_query, get_cursor

dash.register_page(__name__, name='Peer Comparison') # '/' is home page

valuation_items = ['Price to Earnings', 'Price to Book Value', 'Price to Tangible Book Value', 'Price to Sales','Price to Free Cash Flow', 'Price to Pretax Income',
                   'Enterprise Value to Earnings', 'Enterprise Value to Book Value','Enterprise Value to Tangible Book Value','Enterprise Value to Sales',
                   'Enterprise Value to Free Cash Flow', 'Enterprise Value to Pretax Income']

efficiency_items = ['Return on Assets', 'Return on Equity', 'Return on Invested Capital','Return on Capital Employed','Gross Margin', 'EBITDA Margin',
                    'Operating Margin', 'Pretax Margin', 'Net Income Margin','Free Cash Flow Margin']

growth_items = ['Revenue Growth', 'Gross Profit Growth', 'EBITDA Growth', 'Operating Income Growth', 'Pre-Tax Income Growth', 'Net Income Growth',
                'Diluted EPS Growth', 'Number of Diluted Shares Growth', 'Free Cash Flow Growth', 'Operating Cash Flow Growth', 'Capital Expenditure Growth',
                'Cash & Cash Equivilants Growth', 'Plant, Property and Equipment Growth', 'Total Asset Growth', 'Total Equity Growth', 'Capital Expenditure Growth']

other_items = ['Book Value', 'Tangible Book Value','Asset to Equity','Equity to Assets', 'Debt to Equity', 'Debt to Assets', 'Current Ratio', 'Net Debt',
                 'Payout Ratio', 'Revenue', 'Cost of Goods Sold', 'Gross Profit', 'Selling, General and Admin Expenses', 'Research & Development',
                 'Total Operating Expenses', 'EBITDA''Operating Income', 'Pre-tax Income', 'Net Income from Continuing Operations', 'Net Income', 'EPS - Basic',
                 'EPS - Diluted', 'Number of Basic Shares', 'Number of Shares Diluted','Capital Expenditure', 'Share Count', 'Market Cap','Enterprise Value']

def strip_keys(d):
    return {k.strip(): v for k, v in d.items()}

def convert_to_float(value):
    if isinstance(value, str) and '%' in value:
        # Remove '%' and convert to decimal
        return float(value.replace('%', '')) / 100
    else:
        return float(value)

def convert_to_percentage(decimal_str):
    num = float(decimal_str)
    percentage = f"{num * 100:.2f}%"
    return percentage

def round_to_two_decimal_places(num_str):
    num = float(num_str)
    rounded_str = f"{num:.2f}"
    return rounded_str


def format_number(num_str):
    num = float(num_str)
    abs_num = abs(num)  # Use absolute value for comparison

    if abs_num >= 1_000_000_000:
        formatted_number = f"{num / 1_000_000_000:.1f} B"
    elif abs_num >= 1_000_000:
        formatted_number = f"{num / 1_000_000:.1f} M"
    elif abs_num >= 1_000:
        formatted_number = f"{num / 1_000:.1f} K"
    else:
        formatted_number = num_str  # Keep as-is for smaller numbers

    return formatted_number


layout = dbc.Spinner(dbc.Container(
    [
        dcc.Store(id="target_dict", storage_type='session', data={}),
        dcc.Store(id="peer1_dict", storage_type='session', data={}),
        dcc.Store(id="peer2_dict", storage_type='session', data={}),
        dcc.Store(id="peer3_dict", storage_type='session', data={}),
        dcc.Store(id="peer4_dict", storage_type='session', data={}),
        dcc.Store(id="peer5_dict", storage_type='session', data={}),
        dcc.Store(id="peers", storage_type='session', data=[]),
        dcc.Store(id="peers_shown", storage_type='session', data=[]),
        dbc.Row([
            dbc.Col([dbc.Row(html.H2(id='stock_name')),
                     dbc.Row(html.Span([
                         dbc.Badge(id='currency_badge', color="primary", className="me-1"),
                         dbc.Badge(id='sector_badge', color="warning", className="me-1"),
                         dbc.Badge(id='industry_badge', color="danger", className="me-1"),
                         dbc.Badge(id='category_badge', color="dark", className="me-1")]))
                     ], width=10),
            dbc.Col([dbc.Row(html.H2(id='stock_price')),
                     dbc.Row(html.P(id="price_change"), id='price_change_row')],
                    width=2, style={'text-align': 'right'}),
        ], style={'margin-bottom': '10px'}),
        dbc.Row(html.Hr(),style={'margin-bottom': '10px'}),

        dbc.Row(id='descriptionsTable', style={'margin-bottom': '10px'}),

        dbc.Row(html.Hr(),style={'margin-bottom': '10px'}),
        dbc.Row(dmc.Text("Peer Comparison Summary", fw=700, size="xl"), style={'margin-bottom': '10px'}),
        dbc.Row(id='peerTBLRow'),
        dbc.Row(html.Hr(),style={'margin-bottom': '10px', 'margin-top': '20px'}),

        dbc.Row(dmc.Text("Valuation", fw=700, size="xl"), style={'margin-bottom': '10px'}),
        dbc.Row(dcc.Dropdown(valuation_items, 'Price to Earnings', id='dropdown1')),
        dbc.Row(dcc.Graph(id="Graph1")),

        dbc.Row(dmc.Text("Efficiency / Margins", fw=700, size="xl"), style={'margin-bottom': '10px'}),
        dbc.Row(dcc.Dropdown(efficiency_items, 'Return on Equity', id='dropdown2')),
        dbc.Row(dcc.Graph(id="Graph2")),

        dbc.Row(dmc.Text("Growth", fw=700, size="xl"), style={'margin-bottom': '10px'}),
        dbc.Row(dcc.Dropdown(growth_items, 'Revenue Growth', id='dropdown3')),
        dbc.Row(dcc.Graph(id="Graph3")),

        dbc.Row(dmc.Text("Other Useful Metrics", fw=700, size="xl"), style={'margin-bottom': '10px'}),
        dbc.Row(dcc.Dropdown(other_items, 'Debt to Equity', id='dropdown4')),
        dbc.Row(dcc.Graph(id="Graph4")),
    ]
),color='primary',delay_hide=10,delay_show=15,spinner_style={"position":"absolute", "top":"20%"})



@callback(
     [Output("peerTBLRow", "children"),
      Output("target_dict", "data"),
      Output("peer1_dict", "data"),
      Output("peer2_dict", "data"),
      Output("peer3_dict", "data"),
      Output("peer4_dict", "data"),
      Output("peer5_dict", "data"),
      Output("peers", "data"),
      Output("peers_shown", "data")],
    Input("ticker", "data"),
)
def get_peer_tbl(ticker):
    if ticker is None:
        ticker = "TPG_AU"
    symbol = ticker[0:-3]
    query = "SELECT * FROM Peers WHERE Ticker = :ticker;"
    params = {"ticker": symbol}
    row = get_cursor(query,params)

    if row:
        dfs = []
        dfs_graph_df = []
        company_list = list(row)
        for i in range(len(company_list)):
            try:
                name = company_list[i] + '_AU_annual_summary'
                company_df = get_df_tblName(name)
                company_df.columns = ['Item',company_list[i]]
                dfs.append(company_df)
            except:
                pass
            try:
                name = company_list[i] + '_AU_peers'
                peer_df = get_df_tblName(name)
                if peer_df.shape[1] > 6:
                    peer_df = pd.concat([peer_df.iloc[:, 0], peer_df.iloc[:, -5:]], axis=1)
                dfs_graph_df.append(peer_df.to_dict())
            except:
                dfs_graph_df.append({})
        left = dfs[0]
        for i in range(1,len(dfs)):
            left = pd.merge(left, dfs[i], on='Item', how='outer')
    else:
        print("No row found with 'AAPL' in the first column.")

    sorted_columns = [left.columns[0], left.columns[1]] + sorted(left.columns[2:])
    left = left[sorted_columns]

    desired_order = ['Market Cap','EV','P/E','P/BV','EV/FCF','ROE','ROA','ROIC','Gross Margin','Operating Margin',
                     'Net Income Margin','Revenue Growth (Y/Y)','EBITDA Growth (Y/Y)','Net Income Growth (Y/Y)',
                     'D/E','Current Ratio','Net Debt','Share Count']

    format_units = ['Market Cap','EV','Net Debt','Share Count']
    format_percentage = ['ROE','ROA','ROIC']
    format_round = ['P/E','P/BV','EV/FCF','D/E','Current Ratio']

    left['Item'] = pd.Categorical(left['Item'], categories=desired_order, ordered=True)
    left = left.sort_values('Item').reset_index(drop=True)

    for item in format_units:
        mask = left['Item'] == item
        for col in left.columns:
            if col != 'Item':
                left.loc[mask, col] = left.loc[mask, col].map(format_number)

    for item in format_round:
        mask = left['Item'] == item
        for col in left.columns:
            if col != 'Item':
                left.loc[mask, col] = left.loc[mask, col].map(round_to_two_decimal_places)

    for item in format_percentage:
        mask = left['Item'] == item
        for col in left.columns:
            if col != 'Item':
                left.loc[mask, col] = left.loc[mask, col].map(convert_to_percentage)


    table = dbc.Table.from_dataframe(left, striped=True, bordered=True, hover=True)
    companies = left.columns.to_list()
    companies_shown = companies[1:]

    return table, dfs_graph_df[0], dfs_graph_df[1], dfs_graph_df[2], dfs_graph_df[3], dfs_graph_df[4], dfs_graph_df[5],company_list,companies_shown




@callback(
    Output('Graph1', 'figure'),
    [Input('target_dict', 'data'),
     Input('peer1_dict', 'data'),
     Input('peer2_dict', 'data'),
     Input('peer3_dict', 'data'),
     Input('peer4_dict', 'data'),
     Input('peer5_dict', 'data'),
     Input('peers', 'data'),
     Input('dropdown1', 'value'),]
)
def create_chart1(target,dict1,dict2,dict3,dict4,dict5,peers,dropdown1):
    dicts = [target,dict1,dict2,dict3,dict4,dict5]
    dfs = [pd.DataFrame(d) for d in dicts]
    dfs_filtered = []
    for i in range(len(dfs)):
        df = dfs[i]
        if not df.empty and dropdown1 in df.iloc[:, 0].values:
            dff = df[df.iloc[:, 0] == dropdown1]
            dff = dff.reset_index(drop=True)
            dff.iloc[0, 0] = peers[i]
            dff.columns = [col[:4] for col in dff.columns]
            dfs_filtered.append(dff)

    df = pd.concat(dfs_filtered, axis=0, ignore_index=True)
    df = pd.concat([df.iloc[:, 0], df.reindex(sorted(df.columns[1:], key=int), axis=1)], axis=1)
    df_melted = df.melt(id_vars="Item", var_name="Year", value_name="Value")
    df_melted = df_melted.dropna(subset=['Value'])
    df_melted['Value'] = df_melted['Value'].apply(lambda x: convert_to_float(x) if pd.notnull(x) else None)
    df_melted['Year'] = pd.to_datetime(df_melted['Year'], format='%Y')
    df_melted['Value'] = df_melted['Value'].astype(float)  # Ensure Value is a float
    df_melted = df_melted.sort_values(by=['Year', 'Value'])

    fig = px.line(df_melted, x="Year", y="Value", color="Item", markers=True,
                  color_discrete_map={peers[0]: "blue", peers[1]: "red", peers[2]: "green",
                                      peers[3]: "goldenrod", peers[4]: "purple", peers[5]: "cyan"})
    fig.update_layout(
        xaxis_title="Year",
        yaxis_title="Value",
        xaxis=dict(tickformat="%Y", nticks=5),
        yaxis=dict(title='', gridcolor='lightgray'),
        plot_bgcolor = 'white',  # Set background color
        paper_bgcolor = 'white',  # Set plot area background color
        font_color = 'black',  # Set text color
    )

    return fig



@callback(
    Output('Graph2', 'figure'),
    [Input('target_dict', 'data'),
     Input('peer1_dict', 'data'),
     Input('peer2_dict', 'data'),
     Input('peer3_dict', 'data'),
     Input('peer4_dict', 'data'),
     Input('peer5_dict', 'data'),
     Input('peers', 'data'),
     Input('dropdown2', 'value'),]
)
def create_chart2(target,dict1,dict2,dict3,dict4,dict5,peers,dropdown1):
    dicts = [target,dict1,dict2,dict3,dict4,dict5]
    dfs = [pd.DataFrame(d) for d in dicts]
    dfs_filtered = []
    for i in range(len(dfs)):
        df = dfs[i]
        if not df.empty and dropdown1 in df.iloc[:, 0].values:
            dff = df[df.iloc[:, 0] == dropdown1]
            dff = dff.reset_index(drop=True)
            dff.iloc[0, 0] = peers[i]
            dff.columns = [col[:4] for col in dff.columns]
            dfs_filtered.append(dff)

    df = pd.concat(dfs_filtered, axis=0, ignore_index=True)
    df = pd.concat([df.iloc[:, 0], df.reindex(sorted(df.columns[1:], key=int), axis=1)], axis=1)
    df_melted = df.melt(id_vars="Item", var_name="Year", value_name="Value")
    df_melted = df_melted.dropna(subset=['Value'])
    df_melted['Value'] = df_melted['Value'].apply(lambda x: convert_to_float(x) if pd.notnull(x) else None)
    df_melted['Year'] = pd.to_datetime(df_melted['Year'], format='%Y')
    df_melted['Value'] = df_melted['Value'].astype(float)  # Ensure Value is a float
    df_melted = df_melted.sort_values(by=['Year', 'Value'])

    fig = px.line(df_melted, x="Year", y="Value", color="Item", markers=True,
                  color_discrete_map={peers[0]: "blue", peers[1]: "red", peers[2]: "green",
                                      peers[3]: "goldenrod", peers[4]: "purple", peers[5]: "cyan"})
    fig.update_layout(
        xaxis_title="Year",
        yaxis_title="Value",
        xaxis=dict(tickformat="%Y", nticks=5),
        yaxis=dict(title='', gridcolor='lightgray'),
        plot_bgcolor = 'white',  # Set background color
        paper_bgcolor = 'white',  # Set plot area background color
        font_color = 'black',  # Set text color
    )
    return fig



@callback(
    Output('Graph3', 'figure'),
    [Input('target_dict', 'data'),
     Input('peer1_dict', 'data'),
     Input('peer2_dict', 'data'),
     Input('peer3_dict', 'data'),
     Input('peer4_dict', 'data'),
     Input('peer5_dict', 'data'),
     Input('peers', 'data'),
     Input('dropdown3', 'value'),]
)
def create_chart3(target,dict1,dict2,dict3,dict4,dict5,peers,dropdown1):
    dicts = [target,dict1,dict2,dict3,dict4,dict5]
    dfs = [pd.DataFrame(d) for d in dicts]
    dfs_filtered = []
    for i in range(len(dfs)):
        df = dfs[i]
        if not df.empty and dropdown1 in df.iloc[:, 0].values:
            dff = df[df.iloc[:, 0] == dropdown1]
            dff = dff.reset_index(drop=True)
            dff.iloc[0, 0] = peers[i]
            dff.columns = [col[:4] for col in dff.columns]
            dfs_filtered.append(dff)

    df = pd.concat(dfs_filtered, axis=0, ignore_index=True)
    df = pd.concat([df.iloc[:, 0], df.reindex(sorted(df.columns[1:], key=int), axis=1)], axis=1)
    df_melted = df.melt(id_vars="Item", var_name="Year", value_name="Value")
    df_melted = df_melted.dropna(subset=['Value'])
    df_melted['Value'] = df_melted['Value'].apply(lambda x: convert_to_float(x) if pd.notnull(x) else None)
    df_melted['Year'] = pd.to_datetime(df_melted['Year'], format='%Y')
    df_melted['Value'] = df_melted['Value'].astype(float)  # Ensure Value is a float
    df_melted = df_melted.sort_values(by=['Year', 'Value'])

    fig = px.line(df_melted, x="Year", y="Value", color="Item", markers=True,
                  color_discrete_map={peers[0]: "blue", peers[1]: "red", peers[2]: "green",
                                      peers[3]: "goldenrod", peers[4]: "purple", peers[5]: "cyan"})
    fig.update_layout(
        xaxis_title="Year",
        yaxis_title="Value",
        xaxis=dict(tickformat="%Y", nticks=5),
        yaxis=dict(title='', gridcolor='lightgray'),
        plot_bgcolor = 'white',  # Set background color
        paper_bgcolor = 'white',  # Set plot area background color
        font_color = 'black',  # Set text color
    )
    return fig



@callback(
    Output('Graph4', 'figure'),
    [Input('target_dict', 'data'),
     Input('peer1_dict', 'data'),
     Input('peer2_dict', 'data'),
     Input('peer3_dict', 'data'),
     Input('peer4_dict', 'data'),
     Input('peer5_dict', 'data'),
     Input('peers', 'data'),
     Input('dropdown4', 'value'),]
)
def create_chart4(target,dict1,dict2,dict3,dict4,dict5,peers,dropdown1):
    dicts = [target,dict1,dict2,dict3,dict4,dict5]
    dfs = [pd.DataFrame(d) for d in dicts]
    dfs_filtered = []
    for i in range(len(dfs)):
        df = dfs[i]
        if not df.empty and dropdown1 in df.iloc[:, 0].values:
            dff = df[df.iloc[:, 0] == dropdown1]
            dff = dff.reset_index(drop=True)
            dff.iloc[0, 0] = peers[i]
            dff.columns = [col[:4] for col in dff.columns]
            dfs_filtered.append(dff)

    df = pd.concat(dfs_filtered, axis=0, ignore_index=True)
    df = pd.concat([df.iloc[:, 0], df.reindex(sorted(df.columns[1:], key=int), axis=1)], axis=1)
    df_melted = df.melt(id_vars="Item", var_name="Year", value_name="Value")
    df_melted = df_melted.dropna(subset=['Value'])
    df_melted['Value'] = df_melted['Value'].apply(lambda x: convert_to_float(x) if pd.notnull(x) else None)
    df_melted['Year'] = pd.to_datetime(df_melted['Year'], format='%Y')
    df_melted['Value'] = df_melted['Value'].astype(float)  # Ensure Value is a float
    df_melted = df_melted.sort_values(by=['Year', 'Value'])

    fig = px.line(df_melted, x="Year", y="Value", color="Item", markers=True,
                  color_discrete_map={peers[0]: "blue", peers[1]: "red", peers[2]: "green",
                                      peers[3]: "goldenrod", peers[4]: "purple", peers[5]: "cyan"})
    fig.update_layout(
        xaxis_title="Year",
        yaxis_title="Value",
        xaxis=dict(tickformat="%Y", nticks=5),
        yaxis=dict(title='', gridcolor='lightgray'),
        plot_bgcolor = 'white',  # Set background color
        paper_bgcolor = 'white',  # Set plot area background color
        font_color = 'black',  # Set text color
    )
    return fig


@callback(
    Output('descriptionsTable', 'children'),
     [Input('peers_shown', 'data'),
      Input('ticker', 'data')]
)
def create_desc_tbl(peers,ticker):
    peers_str = ', '.join(f"'{peer}'" for peer in peers)
    query = f"SELECT symbol, name, description FROM metadataTBL WHERE symbol IN ({peers_str})"
    df = get_df_query(query)
    df = df.drop_duplicates(subset='symbol')
    first_row = df[df['symbol'] == ticker[0:-3]]
    other_rows = df[df['symbol'] != ticker[0:-3]].sort_values(by='symbol')
    df = pd.concat([first_row, other_rows], ignore_index=True)
    df.columns = [col.capitalize() for col in df.columns]
    table = dbc.Table.from_dataframe(df)
    return table