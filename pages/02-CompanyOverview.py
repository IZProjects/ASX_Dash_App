import dash
from dash import dcc, html, Input, Output, callback, clientside_callback
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from io import StringIO
import dash_mantine_components as dmc
from mysql_connect_funcs import get_df_tblName, get_df_query


pd.options.mode.chained_assignment = None  # default='warn'


dash.register_page(__name__, name='Company Overview')


TABLE_SIZE = 16
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

def convert_to_percentage(df):
    # Convert the second column from decimal string to float
    df[''] = df[''].astype(float)
    # Convert to percentage and format as string
    df[''] = df[''].apply(lambda x: f"{x * 100:.2f}%")
    return df

def round_decimal_strings(df):
    # Convert the second column from decimal string to float
    df[''] = df[''].astype(float)
    # Round to two decimal places and convert back to string
    df[''] = df[''].apply(lambda x: f"{x:.2f}")
    return df


def create_link_announcements(item):
    return dcc.Link('Link', href=item)

def get_total_page(page_size, total_data):
  data_div_page_size = total_data // page_size
  data_mod_page_size = total_data % page_size
  total_page = data_div_page_size if data_mod_page_size == 0 else (data_div_page_size+1)
  return total_page


button_group1 = dmc.SegmentedControl(
    id="radios_tf",
    color='indigo',
    data=[
        {"label": "3m", "value": '3m'},
        {"label": "6m", "value": '6m'},
        {"label": "1y", "value": '1y'},
        {"label": "3y", "value": '3y'},
        {"label": "5y", "value": '5y'},
        {"label": "10y", "value": '10y'},
        {"label": "All", "value": 'All'},
    ],
    value='1y',
    size='md'
)


button_group2 = dmc.SegmentedControl(
    id="radios_type",
    color='indigo',
    data=[
        {"label": "Line", "value": "line"},
        {"label": "Candle", "value": "candle"},
    ],
    value="line",
    size='md'
)

# Layout
layout = dbc.Spinner(dbc.Container([
    dcc.Store(id="dict_daily", storage_type='session', data={}),
    dcc.Store(id="dict_weekly", storage_type='session', data={}),
    dcc.Store(id="dict_monthly", storage_type='session', data={}),
    dcc.Store(id="announcementsTBLStore", storage_type='session', data={}),

    dbc.Row([
        dbc.Col([dbc.Row(html.H2(id='stock_name')),
                 dbc.Row(html.Span([
                     dbc.Badge(id='currency_badge', color="primary", className="me-1"),
                     dbc.Badge(id='sector_badge', color="warning", className="me-1"),
                     dbc.Badge(id='industry_badge', color="danger", className="me-1"),
                     dbc.Badge(id='category_badge', color="dark", className="me-1")],))
                 ], width=10),
        dbc.Col([dbc.Row(html.H2(id='stock_price')),
                 dbc.Row(html.P(id="price_change"),id='price_change_row')],
                width=2, style={'text-align': 'right'}),
    ], style={'margin-bottom': '10px'}),

    dbc.Row(html.Hr()),

    dbc.Row([dbc.Card([
            dbc.CardHeader(dbc.Stack([button_group1,
                                              button_group2,
                                              dmc.Button("Show/Hide", id='collapse-button', color='indigo', size='md')],
                                              direction="horizontal", gap=3, className="justify-content-between")

            ),
            dbc.Collapse(
                dbc.CardBody([html.H4(id='chart_heading'),
                              html.Div([html.P("Return over the period: ", style={'display': 'inline'}),
                                        html.P(id='period_return'),
                                        ]),
                              dcc.Graph(id='price_chart1'),
                              dcc.Graph(id='volume_chart1', style={'height': '250px'})
                              ]),
                id="collapse", is_open=True)
            ])
        ],
        style={'margin-bottom': '20px'}),

    dbc.Row([
        dbc.Card(
            dbc.CardBody([
                dbc.Row([
                    dbc.Col(id='table1', width=4),
                    dbc.Col(id='table2', width=4),
                    dbc.Col(id='table3', width=4)
                ]),
                dbc.Row([
                    dbc.Col(id='table4', width=4),
                    dbc.Col(id='table5', width=4),
                    dbc.Col(id='table6', width=4)
                ]),
            ]))
    ], style={'margin-bottom': '20px'}),

    dbc.Row([dbc.Card(dbc.CardBody([dmc.Text("About the Company", fw=700, size='xl'),
                                    html.P(id='description'), dbc.Row(id='peter_lynch')]))], style={'margin-bottom': '25px'}),
    dbc.Row(dmc.Text("Announcements", fw=700, size='xl'), style={'margin-bottom': '3px', 'margin-top': '10px'}),
    dbc.Row(html.Small("*Ctrl-Click to open link in new tab")),
    dbc.Row([
        dbc.Table(id='stockAnnoucementsTBL', style={'margin-bottom': '-10px'}),
        dbc.Pagination(id="pagination_stockAnnouncement", max_value=5)
    ])
]),color="primary",delay_hide=10,delay_show=15,spinner_style={"position":"absolute", "top":"20%"})

@callback(
    [Output("stock_price", "children"),
    Output("price_change", "children"),
    Output("price_change_row", "style")],
    Input("ticker", "data"),
)
def get_prices(ticker):
    if ticker is None:
        ticker = "TPG_AU"

    code = ticker.replace('_', '.')
    query = f"SELECT * FROM real_time WHERE code = '{code}'"
    df = get_df_query(query)


    price = '$' + str(df.at[0, 'close'])
    change = df.at[0, 'change']
    change_p = df.at[0, 'change_p']
    if change == 'NA':
        change_line = 'NA'
        style = {'color': 'black'}
    elif float(change) > 0:
        change_line = '+'+str(change)+' (+'+ str(round(float(change_p), 2))+'%)'
        style = {'color': 'green'}
    else:
        change_line = str(change) + ' (' + str(round(float(change_p), 2)) + '%)'
        style = {'color': 'red'}
    return price, change_line, style

@callback(
    [Output("table1", "children"),
     Output("table2", "children"),
     Output("table3", "children"),
     Output("table4", "children"),
     Output("table5", "children"),
     Output("table6", "children"),],
    Input("ticker", "data"),
)
def get_tbl(ticker):
    if ticker is None:
        ticker = "TPG_AU"

    name = ticker+'_annual_summary'
    df = get_df_tblName(name)

    df1 = df[0:3]
    df1.columns = ['General', '']
    df1[''] = df1[''].apply(format_number)
    df2 = df[3:6]
    df2.columns = ['Valuation', '']
    df2 = round_decimal_strings(df2)
    df3 = df[6:9]
    df3.columns = ['Financial Position', '']
    df3 = round_decimal_strings(df3)
    df3[''] = df3[''].apply(format_number)
    df4 = df[9:12]
    df4.columns = ['Growth', '']
    df5 = df[12:15]
    df5.columns = ['Efficiency', '']
    df5 = convert_to_percentage(df5)
    df6 = df[15:18]
    df6.columns = ['Margins', '']

    tbl1 = dbc.Table.from_dataframe(df1, borderless=False, hover=True, size='sm', className='summary_table')
    tbl2 = dbc.Table.from_dataframe(df2, borderless=False, hover=True, size='sm', className='summary_table')
    tbl3 = dbc.Table.from_dataframe(df3, borderless=False, hover=True, size='sm', className='summary_table')
    tbl4 = dbc.Table.from_dataframe(df4, borderless=False, hover=True, size='sm', className='summary_table')
    tbl5 = dbc.Table.from_dataframe(df5, borderless=False, hover=True, size='sm', className='summary_table')
    tbl6 = dbc.Table.from_dataframe(df6, borderless=False, hover=True, size='sm', className='summary_table')
    return tbl1,tbl2,tbl3,tbl4,tbl5,tbl6


@callback(
    [Output("description", "children"),
     Output("chart_heading", "children")],
     Input("single_ticker_metadata", "data")
)
def print_description(metadata):
    df_metadata = pd.DataFrame.from_dict(metadata)
    df_metadata = df_metadata.reset_index()
    description = df_metadata.at[0, 'description']
    df_metadata['title'] = df_metadata['name'] + ' (' + df_metadata['symbol'] + ')'
    name = df_metadata.at[0, 'title']
    return description,name

@callback(
     [Output("stock_name", "children"),
      Output("sector_badge", "children"),
     Output("industry_badge", "children"),
     Output("currency_badge", "children"),
      Output("category_badge", "children"),],
     [Input("single_ticker_metadata", "data"),
      Input("ticker", "data")]
)
def print_tags(metadata,ticker):
    df_metadata = pd.DataFrame.from_dict(metadata)
    df_metadata = df_metadata.reset_index()
    sector = df_metadata.at[0, 'morningstar_sector']
    industry = df_metadata.at[0, 'morningstar_industry']
    currency = df_metadata.at[0, 'currency']
    df_metadata['title'] = df_metadata['name'] + ' (' + df_metadata['symbol'] + ')'
    name = df_metadata.at[0, 'title']
    if ticker is None:
        ticker = "TPG_AU"

    df = get_df_tblName("Peter_Lynch_Category")
    if ticker[0:3] in df['ticker'].values:
        category = df[df['ticker'] == ticker[0:3]]
        category = category.reset_index(drop=True)
        category = category.at[0, 'content']
    else:
        category = ''
    return name,sector,industry,currency,category

@callback(
    Output("collapse", "is_open"),
    [Input("collapse-button", "n_clicks")],
    [Input("collapse", "is_open")],
)
def toggle_collapse(n, is_open):
    if n:
        return not is_open
    return is_open

@callback(
    [Output(component_id='dict_daily', component_property='data'),
     Output(component_id='dict_weekly', component_property='data'),
     Output(component_id='dict_monthly', component_property='data')],
    Input("ticker", "data")
)
def sql_get_prices(ticker):
    if ticker is None:
        ticker = "TPG_AU"

    name = ticker+'_daily'
    df_daily = get_df_tblName(name)
    dict_daily = df_daily.to_dict()
    name = ticker+'_weekly'
    df_weekly = get_df_tblName(name)
    dict_weekly = df_weekly.to_dict()
    name = ticker+'_monthly'
    df_monthly = get_df_tblName(name)
    dict_monthly = df_monthly.to_dict()
    return dict_daily, dict_weekly, dict_monthly

@callback(
    [Output(component_id='price_chart1', component_property='figure'),
     Output(component_id='volume_chart1', component_property='figure'),
     Output(component_id='period_return', component_property='children'),
     Output(component_id='period_return', component_property='style'),],
    [Input("dict_daily", "data"),
     Input("dict_weekly", "data"),
     Input("dict_monthly", "data"),
     Input(component_id='radios_tf', component_property='value'),
     Input(component_id='radios_type', component_property='value')]
)
def update_graph(dict_daily,dict_weekly,dict_monthly, value1, value2):
    df_daily = pd.DataFrame.from_dict(dict_daily)
    df_weekly = pd.DataFrame.from_dict(dict_weekly)
    df_monthly = pd.DataFrame.from_dict(dict_monthly)
    if value1 == '3m':
        filtered_df = df_daily[-60:]
    elif value1 == '6m':
        filtered_df = df_daily[-130:]
    elif value1 == '1y':
        filtered_df = df_daily
    elif value1 == '3y':
        filtered_df = df_weekly[-156:]
    elif value1 == '5y':
        filtered_df = df_weekly
    elif value1 == '10y':
        filtered_df = df_monthly[-120:]
    else:
        filtered_df = df_monthly


    filtered_df = filtered_df.reset_index()
    opening_price = filtered_df.loc[0, 'open']
    closing_price = filtered_df.loc[filtered_df.index[-1], 'close']
    change_pct = ((closing_price-opening_price)/opening_price)*100

    if change_pct < 0:
        change_style = {'display': 'inline', 'color': 'red'}
    else:
        change_style = {'display': 'inline', 'color': 'green'}

    change_pct = str(round(change_pct, 2)) + ' %'

    if value2=='line':
        fig1 = px.line(filtered_df, x='date', y='close', markers=False, color_discrete_sequence=['gold'])
    elif value2=='candle':
        fig1 = go.Figure(data=[go.Candlestick(x=filtered_df['date'],
                                              open=filtered_df['open'],
                                              high=filtered_df['high'],
                                              low=filtered_df['low'],
                                              close=filtered_df['close'],
                                              showlegend=False)]
                         )
    else:
        fig1 = px.line(filtered_df, x='date', y='close', markers=False, color_discrete_sequence=['gold'])

    # customise fig
    fig1.update_layout(
        plot_bgcolor='white',  # Set background color
        paper_bgcolor='white',  # Set plot area background color
        font_color='black',  # Set text color
        title='',  # Set title
        xaxis=dict(title=''),  # Set X-axis title and grid color
        yaxis=dict(title='', gridcolor='lightgray'),  # Set Y-axis title and grid color
        margin=dict(l=40, r=40, t=40, b=40),  # Add margin
        xaxis_ticks='outside',  # Place X-axis ticks outside
        xaxis_tickcolor='lightgray',  # Set X-axis tick color
        yaxis_ticks='outside',  # Place Y-axis ticks outside
        yaxis_tickcolor='lightgray',  # Set Y-axis tick color
        xaxis_rangeslider_visible=False
    )

    fig2 = px.bar(filtered_df, x='date', y='volume', color_discrete_sequence=['gold'])

    fig2.update_layout(
        plot_bgcolor='white',  # Set background color
        paper_bgcolor='white',  # Set plot area background color
        font_color='black',  # Set text color
        title=None,  # Set title
        xaxis=dict(title=''),  # Set X-axis title and grid color
        yaxis=dict(title='', gridcolor='lightgray'),  # Set Y-axis title and grid color
        margin=dict(l=40, r=40, t=40, b=40),  # Add margin
        xaxis_ticks='outside',  # Place X-axis ticks outside
        xaxis_tickcolor='lightgray',  # Set X-axis tick color
        yaxis_ticks='outside',  # Place Y-axis ticks outside
        yaxis_tickcolor='lightgray',  # Set Y-axis tick color
    )

    return fig1, fig2, change_pct, change_style


@callback(
    Output('stockAnnoucementsTBL', 'children'),
    [Input('ticker', 'data'),
     Input('pagination_stockAnnouncement', 'active_page')]
)
def create_announcements_TBL(ticker, page):
    # convert active_page data to integer and set default value to 1
    if ticker is None:
        ticker = "TPG_AU"
    table_name = ticker + '_announcements'
    query = f"SELECT * FROM {table_name} LIMIT 80"
    df_announcements = get_df_query(query)
    df_announcements['Links'] = df_announcements['Links'].apply(create_link_announcements)

    int_page = 1 if not page else int(page)

    # define filter index range based on active page
    filter_index_1 = (int_page - 1) * TABLE_SIZE
    filter_index_2 = (int_page) * TABLE_SIZE

    # get data by filter range based on active page number
    fitlered_df = df_announcements[filter_index_1:min(filter_index_2,len(df_announcements))]
    fitlered_df['Document Name'] = fitlered_df['Document Name'].str.upper()
    fitlered_df['Type'] = fitlered_df['Type'].str.upper()

    # load data to dash bootstrap table component
    table = dbc.Table.from_dataframe(fitlered_df, bordered=True, hover=True, striped=True)

    return table

@callback(
     Output(component_id='peter_lynch', component_property='children'),
    Input("ticker", "data")
)
def print_peter_lynch(ticker):
    if ticker is None:
        ticker = "TPG_AU"

    df = get_df_tblName("Peter_Lynch_Summary_TBL")

    if ticker[0:3] in df['ticker'].values:
        try:
            tsv = df[df['ticker'] == ticker[0:3]]
            tsv = tsv.reset_index(drop=True)
            tsv = tsv.at[0, 'content']
            tbltsv = pd.read_csv(StringIO(tsv), sep="\t")
            tbltsv = tbltsv.reset_index()
            tbltsv = tbltsv.dropna()
            tbltsv = tbltsv.drop(0).reset_index(drop=True)
            tbltsv.columns = [''] * len(tbltsv.columns)
            ctbl = dbc.Table.from_dataframe(tbltsv, bordered=False, hover=True, className='first_col_bold_tbl')
            return ctbl
        except:
            return ''
    else:
        return ''