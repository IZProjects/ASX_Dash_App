import dash
from dash import dcc, html, callback, Output, Input
import pandas as pd
import plotly.express as px
import dash_mantine_components as dmc
from mysql_connect_funcs import get_df_tblName, get_df_query, get_cursor
import plotly.graph_objects as go
from utils.df_to_mantineTBL import genTBLContent

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


layout = dmc.Box([
    dcc.Store(id="target_dict", storage_type='session', data={}),
    dcc.Store(id="peer1_dict", storage_type='session', data={}),
    dcc.Store(id="peer2_dict", storage_type='session', data={}),
    dcc.Store(id="peer3_dict", storage_type='session', data={}),
    dcc.Store(id="peer4_dict", storage_type='session', data={}),
    dcc.Store(id="peer5_dict", storage_type='session', data={}),
    dcc.Store(id="peers", storage_type='session', data=[]),
    dcc.Store(id="peers_shown", storage_type='session', data=[]),

    dmc.Grid([
        dmc.GridCol([dmc.Grid(dmc.Title(id='stock_name', order=2), style={'margin-bottom': '10px'}),
                     dmc.Grid(
                         dmc.Group([
                             dmc.Badge(id='currency_badge', color="indigo", className="me-1"),
                             dmc.Badge(id='sector_badge', color="red", className="me-1"),
                             dmc.Badge(id='industry_badge', color="violet", className="me-1"),
                             dmc.Badge(id='category_badge', color="gray", className="me-1")
                         ], gap='sm')
                     )
                     ], span='content'),
        dmc.GridCol([dmc.Grid(dmc.Title(id='stock_price', order=2), style={'margin-bottom': '10px'}),
                     dmc.Grid(dmc.Text(id="price_change", size='md'), id='price_change_row')],
                    span='content', offset='auto'),
    ], justify='space-between',
        style={'margin-bottom': '20px', 'margin-top': '20px', 'margin-left': '20px', 'margin-right': '20px'}),

    dmc.Container(html.Hr(), fluid=True, style={'margin-bottom': '10px', 'margin-top': '10px'}),

    dmc.Container(id='descriptionsTable', fluid=True, style={'margin-bottom': '10px'}),

    dmc.Container(html.Hr(), fluid=True, style={'margin-bottom': '10px', 'margin-top': '10px'}),
    dmc.Container(dmc.Title("Peer Comparison Summary", order=4), fluid=True, style={'margin-bottom': '10px'}),
    dmc.Container(id='peerTBLRow', fluid=True),
    dmc.Container(html.Hr(), fluid=True, style={'margin-bottom': '10px', 'margin-top': '10px'}),

    dmc.Container(dmc.Title("Valuation", order=4), fluid=True, style={'margin-bottom': '10px', 'margin-top': '20px'}),
    dmc.Container(dcc.Dropdown(valuation_items, 'Price to Earnings', style={'color':'black'}, id='dropdown1'), fluid=True),
    dmc.Container(dcc.Graph(id="Graph1"), fluid=True),

    dmc.Container(dmc.Title("Efficiency / Margins", order=4), fluid=True, style={'margin-bottom': '10px', 'margin-top': '20px'}),
    dmc.Container(dcc.Dropdown(efficiency_items, 'Return on Equity', style={'color':'black'}, id='dropdown2'), fluid=True),
    dmc.Container(dcc.Graph(id="Graph2"), fluid=True),

    dmc.Container(dmc.Title("Growth", order=4), fluid=True, style={'margin-bottom': '10px', 'margin-top': '20px'}),
    dmc.Container(dcc.Dropdown(growth_items, 'Revenue Growth', style={'color':'black'}, id='dropdown3'), fluid=True),
    dmc.Container(dcc.Graph(id="Graph3"), fluid=True),

    dmc.Container(dmc.Title("Other Useful Metrics", order=4), fluid=True, style={'margin-bottom': '10px', 'margin-top': '20px'}),
    dmc.Container(dcc.Dropdown(other_items, 'Debt to Equity', style={'color':'black'}, id='dropdown4'), fluid=True),
    dmc.Container(dcc.Graph(id="Graph4"), fluid=True),

])

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

    try:
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

        table = dmc.Table(data=genTBLContent(left), striped=True, withTableBorder=True, highlightOnHover=True, withColumnBorders=True,)

        companies = left.columns.to_list()
        companies_shown = companies[1:]

        return table, dfs_graph_df[0], dfs_graph_df[1], dfs_graph_df[2], dfs_graph_df[3], dfs_graph_df[4], dfs_graph_df[5],company_list,companies_shown
    except:
        alert = dmc.Alert(
            "Sorry! This data is not available.",
            id="alert-peers1",
            title="Error!",
            color="red",
            withCloseButton=True,
            hide=False
        ),
        return alert,{},{},{},{},{},{},[],[]




@callback(
    Output('Graph1', 'figure'),
    [Input('target_dict', 'data'),
     Input('peer1_dict', 'data'),
     Input('peer2_dict', 'data'),
     Input('peer3_dict', 'data'),
     Input('peer4_dict', 'data'),
     Input('peer5_dict', 'data'),
     Input('peers', 'data'),
     Input('dropdown1', 'value'),
     Input("mantine-provider", "forceColorScheme")]
)
def create_chart1(target,dict1,dict2,dict3,dict4,dict5,peers,dropdown1, theme):
    try:
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
        df_melted = df_melted.reset_index(drop=True)

        unique_items = df_melted['Item'].unique()
        colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728","#17becf", "#9467bd"]
        valid_peers = [peer for peer in peers if peer in unique_items]
        color_discrete_map = {item: color for item, color in zip(valid_peers, colors)}

        fig = go.Figure(layout=dict(template='plotly'))
        fig = px.line(df_melted, x="Year", y="Value", color="Item", markers=True,
                      color_discrete_map=color_discrete_map)
    except:
        fig = go.Figure()
    if theme == 'light':
        fig.update_layout(
            xaxis_title="Year",
            yaxis_title="Value",
            xaxis=dict(tickformat="%Y", nticks=5),
            yaxis=dict(title='', gridcolor='lightgray'),
            plot_bgcolor='white',  # Set background color
            paper_bgcolor='white',  # Set plot area background color
            font_color='black',  # Set text color
        )
    else:
        fig.update_layout(
            xaxis_title="Year",
            yaxis_title="Value",
            xaxis=dict(tickformat="%Y", nticks=5, gridcolor='rgb(50, 50, 50)'),
            yaxis=dict(title='', gridcolor='lightgray'),
            plot_bgcolor='rgb(50, 50, 50)',  # Set background color
            paper_bgcolor='rgb(50, 50, 50)',  # Set plot area background color
            font_color='white',  # Set text color
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
     Input('dropdown2', 'value'),
     Input("mantine-provider", "forceColorScheme")]
)
def create_chart2(target,dict1,dict2,dict3,dict4,dict5,peers,dropdown1,theme):
    try:
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
        df_melted = df_melted.reset_index(drop=True)

        unique_items = df_melted['Item'].unique()
        colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728","#17becf", "#9467bd"]
        valid_peers = [peer for peer in peers if peer in unique_items]
        color_discrete_map = {item: color for item, color in zip(valid_peers, colors)}

        fig = go.Figure(layout=dict(template='plotly'))
        fig = px.line(df_melted, x="Year", y="Value", color="Item", markers=True,
                      color_discrete_map=color_discrete_map)
    except:
        fig = go.Figure()

    if theme == 'light':
        fig.update_layout(
            xaxis_title="Year",
            yaxis_title="Value",
            xaxis=dict(tickformat="%Y", nticks=5),
            yaxis=dict(title='', gridcolor='lightgray'),
            plot_bgcolor='white',  # Set background color
            paper_bgcolor='white',  # Set plot area background color
            font_color='black',  # Set text color
        )
    else:
        fig.update_layout(
            xaxis_title="Year",
            yaxis_title="Value",
            xaxis=dict(tickformat="%Y", nticks=5, gridcolor='rgb(50, 50, 50)'),
            yaxis=dict(title='', gridcolor='lightgray'),
            plot_bgcolor='rgb(50, 50, 50)',  # Set background color
            paper_bgcolor='rgb(50, 50, 50)',  # Set plot area background color
            font_color='white',  # Set text color
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
     Input('dropdown3', 'value'),
     Input("mantine-provider", "forceColorScheme")]
)
def create_chart3(target,dict1,dict2,dict3,dict4,dict5,peers,dropdown1,theme):
    try:
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
        df_melted = df_melted.reset_index(drop=True)

        unique_items = df_melted['Item'].unique()
        colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#17becf", "#9467bd"]
        valid_peers = [peer for peer in peers if peer in unique_items]
        color_discrete_map = {item: color for item, color in zip(valid_peers, colors)}

        fig = go.Figure(layout=dict(template='plotly'))
        fig = px.line(df_melted, x="Year", y="Value", color="Item", markers=True,
                      color_discrete_map=color_discrete_map)
    except:
        fig = go.Figure()

    if theme == 'light':
        fig.update_layout(
            xaxis_title="Year",
            yaxis_title="Value",
            xaxis=dict(tickformat="%Y", nticks=5),
            yaxis=dict(title='', gridcolor='lightgray'),
            plot_bgcolor='white',  # Set background color
            paper_bgcolor='white',  # Set plot area background color
            font_color='black',  # Set text color
        )
    else:
        fig.update_layout(
            xaxis_title="Year",
            yaxis_title="Value",
            xaxis=dict(tickformat="%Y", nticks=5, gridcolor='rgb(50, 50, 50)'),
            yaxis=dict(title='', gridcolor='lightgray'),
            plot_bgcolor='rgb(50, 50, 50)',  # Set background color
            paper_bgcolor='rgb(50, 50, 50)',  # Set plot area background color
            font_color='white',  # Set text color
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
     Input('dropdown4', 'value'),
     Input("mantine-provider", "forceColorScheme")]
)
def create_chart4(target,dict1,dict2,dict3,dict4,dict5,peers,dropdown1,theme):
    try:
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
        df_melted = df_melted.reset_index(drop=True)

        unique_items = df_melted['Item'].unique()
        colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728","#17becf", "#9467bd"]
        valid_peers = [peer for peer in peers if peer in unique_items]
        color_discrete_map = {item: color for item, color in zip(valid_peers, colors)}

        fig = go.Figure(layout=dict(template='plotly'))
        fig = px.line(df_melted, x="Year", y="Value", color="Item", markers=True,
                      color_discrete_map=color_discrete_map)

    except:
        fig = go.Figure()

    if theme == 'light':
        fig.update_layout(
            xaxis_title="Year",
            yaxis_title="Value",
            xaxis=dict(tickformat="%Y", nticks=5),
            yaxis=dict(title='', gridcolor='lightgray'),
            plot_bgcolor='white',  # Set background color
            paper_bgcolor='white',  # Set plot area background color
            font_color='black',  # Set text color
        )
    else:
        fig.update_layout(
            xaxis_title="Year",
            yaxis_title="Value",
            xaxis=dict(tickformat="%Y", nticks=5, gridcolor='rgb(50, 50, 50)'),
            yaxis=dict(title='', gridcolor='lightgray'),
            plot_bgcolor='rgb(50, 50, 50)',  # Set background color
            paper_bgcolor='rgb(50, 50, 50)',  # Set plot area background color
            font_color='white',  # Set text color
        )
    return fig


@callback(
    Output('descriptionsTable', 'children'),
     [Input('peers_shown', 'data'),
      Input('ticker', 'data')]
)
def create_desc_tbl(peers,ticker):
    try:
        peers_str = ', '.join(f"'{peer}'" for peer in peers)
        query = f"SELECT symbol, name, description FROM metadataTBL WHERE symbol IN ({peers_str})"
        df = get_df_query(query)
        df = df.drop_duplicates(subset='symbol')
        first_row = df[df['symbol'] == ticker[0:-3]]
        other_rows = df[df['symbol'] != ticker[0:-3]].sort_values(by='symbol')
        df = pd.concat([first_row, other_rows], ignore_index=True)
        df.columns = [col.capitalize() for col in df.columns]
        #table = dbc.Table.from_dataframe(df)
        table = dmc.Table(data=genTBLContent(df), highlightOnHover=True,)
        return table
    except:
        alert = dmc.Alert(
            "Sorry! This data is not available.",
            id="alert-peers2",
            title="Error!",
            color="red",
            withCloseButton=True,
            hide=False
        ),
        return alert