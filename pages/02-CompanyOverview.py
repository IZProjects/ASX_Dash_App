import dash
from dash import dcc, html, Input, Output, callback
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from io import StringIO
import dash_mantine_components as dmc
from mysql_connect_funcs import get_df_tblName, get_df_query
from utils.df_to_mantineTBL import genTBLContent
import numpy as np

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


layout = dmc.Box([
    dcc.Store(id="dict_daily", storage_type='session', data={}),
    dcc.Store(id="dict_weekly", storage_type='session', data={}),
    dcc.Store(id="dict_monthly", storage_type='session', data={}),
    dcc.Store(id="announcementsTBLStore", storage_type='session', data={}),

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
                     ], span={"base": 8, "md": 10}),
        dmc.GridCol([dmc.Grid(dmc.Title(id='stock_price', order=2), style={'margin-bottom': '10px'}),
                     dmc.Grid(dmc.Text(id="price_change", size='md'), id='price_change_row')],
                    span='content', offset='auto'),
    ], justify='space-between',
        style={'margin-bottom': '20px', 'margin-top': '20px', 'margin-left': '20px', 'margin-right': '20px'}),

    dmc.Container(html.Hr(), fluid=True),

    dmc.Container([
        dmc.Card([
            dmc.Group([button_group1,button_group2,dmc.Button("Show/Hide", id='collapse-button', color='indigo', size='md')], gap='md', justify='space-between', className="justify-content-between"),

            dmc.Collapse(
                dmc.Container([dmc.Title(id='chart_heading', order=4, style={'margin-top': '30px'}),
                              html.Div([dmc.Text("Return over the period: ", style={'display': 'inline'}),
                                        dmc.Text(id='period_return'),
                                        ]),
                              dcc.Graph(id='price_chart1'),
                              dcc.Graph(id='volume_chart1', style={'height': '250px'})
                              ], fluid=True),
                id="collapse", opened=True)
        ],withBorder=True, radius="md",)
    ],fluid=True, style={'margin-bottom': '20px'}),

dmc.Container([
        dmc.Card([
            dmc.Grid([
                dmc.GridCol(id='sumtable1', span=4),
                dmc.GridCol(id='sumtable2', span=4),
                dmc.GridCol(id='sumtable3', span=4)
            ]),
            dmc.Grid([
                dmc.GridCol(id='sumtable4', span=4),
                dmc.GridCol(id='sumtable5', span=4),
                dmc.GridCol(id='sumtable6', span=4)
            ]),
        ], withBorder=True, radius="md",)
    ], fluid=True, style={'margin-bottom': '20px'}, visibleFrom='md'),

dmc.Container([
        dmc.Card(id='sumtable_mobile', withBorder=True, radius="md",)
    ], fluid=True, style={'margin-bottom': '20px'}, hiddenFrom='md'),

    dmc.Container([dmc.Card([dmc.Text("About the Company", fw=700, size='xl'),
                                    dmc.Text(id='description'), dmc.CardSection(dmc.Container(id='peter_lynch', fluid=True))], withBorder=True, radius="md")],
            style={'margin-bottom': '25px'}, fluid=True),


], style={'margin-left': '30px'})


@callback(
    [Output("stock_price", "children"),
    Output("price_change", "children"),
    Output("price_change_row", "style")],
    Input("ticker", "data"),
)
def get_prices(ticker):
    if ticker is None:
        ticker = "TPG_AU"
    try:
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
    except:
        return '', '', {}

@callback(
    [Output("sumtable1", "children"),
     Output("sumtable2", "children"),
     Output("sumtable3", "children"),
     Output("sumtable4", "children"),
     Output("sumtable5", "children"),
     Output("sumtable6", "children"),
     Output("sumtable_mobile", "children"),],
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
    df_mob = pd.DataFrame(np.vstack([df1.to_numpy(), df2.to_numpy(), df3.to_numpy(),
                                     df4.to_numpy(), df5.to_numpy(), df6.to_numpy()]))
    df_mob.columns = ['Summary', '']

    tbl1 = dmc.Table(data=genTBLContent(df1), highlightOnHover=True, className='summary_table')
    tbl2 = dmc.Table(data=genTBLContent(df2), highlightOnHover=True, className='summary_table')
    tbl3 = dmc.Table(data=genTBLContent(df3), highlightOnHover=True, className='summary_table')
    tbl4 = dmc.Table(data=genTBLContent(df4), highlightOnHover=True, className='summary_table')
    tbl5 = dmc.Table(data=genTBLContent(df5), highlightOnHover=True, className='summary_table')
    tbl6 = dmc.Table(data=genTBLContent(df6), highlightOnHover=True, className='summary_table')
    tbl_mob = dmc.Table(data=genTBLContent(df_mob), highlightOnHover=True, className='summary_table')


    return tbl1,tbl2,tbl3,tbl4,tbl5,tbl6,tbl_mob


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
    Output("collapse", "opened"),
    [Input("collapse-button", "n_clicks"),
     Input("collapse", "opened")],
)
def toggle_collapse(n, is_open):
    if n:
        return not is_open
    return is_open

@callback(
    [Output(component_id='dict_daily', component_property='data'),
     Output(component_id='dict_weekly', component_property='data'),
     Output(component_id='dict_monthly', component_property='data')],
    Input("ticker", "data"),

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
     Output(component_id='period_return', component_property='style')],
    [Input("dict_daily", "data"),
     Input("dict_weekly", "data"),
     Input("dict_monthly", "data"),
     Input(component_id='radios_tf', component_property='value'),
     Input(component_id='radios_type', component_property='value'),
     Input("mantine-provider", "forceColorScheme")]
)
def update_graph(dict_daily,dict_weekly,dict_monthly, value1, value2, theme):
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

    try:
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

        if theme == 'light':
            fig1.update_layout(
                plot_bgcolor='white',  # Set background color
                paper_bgcolor='white',  # Set plot area background color
                font_color='black',  # Set text color
                title='',  # Set title
                xaxis=dict(title='',),  # Set X-axis title and grid color
                yaxis=dict(title='', gridcolor='lightgray'),  # Set Y-axis title and grid color
                margin=dict(l=40, r=40, t=40, b=40),  # Add margin
                xaxis_ticks='outside',  # Place X-axis ticks outside
                xaxis_tickcolor='lightgray',  # Set X-axis tick color
                yaxis_ticks='outside',  # Place Y-axis ticks outside
                yaxis_tickcolor='lightgray',  # Set Y-axis tick color
                xaxis_rangeslider_visible=False
            )
        else:
            fig1.update_layout(
                plot_bgcolor='rgb(50, 50, 50)',  # Set background color
                paper_bgcolor='rgb(50, 50, 50)',  # Set plot area background color
                font_color='white',  # Set text color
                title='',  # Set title
                xaxis=dict(title='', gridcolor='rgb(50, 50, 50)'),  # Set X-axis title and grid color
                yaxis=dict(title='', gridcolor='lightgray'),  # Set Y-axis title and grid color
                margin=dict(l=40, r=40, t=40, b=40),  # Add margin
                xaxis_ticks='outside',  # Place X-axis ticks outside
                xaxis_tickcolor='lightgray',  # Set X-axis tick color
                yaxis_ticks='outside',  # Place Y-axis ticks outside
                yaxis_tickcolor='lightgray',  # Set Y-axis tick color
                xaxis_rangeslider_visible=False
            )

        fig2 = px.bar(filtered_df, x='date', y='volume', color_discrete_sequence=['gold'])

        if theme == 'light':
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
        else:
            fig2.update_layout(
                plot_bgcolor='rgb(50, 50, 50)',  # Set background color
                paper_bgcolor='rgb(50, 50, 50)',  # Set plot area background color
                font_color='white',  # Set text color
                title=None,  # Set title
                xaxis=dict(title='', gridcolor='rgb(50, 50, 50)'),  # Set X-axis title and grid color
                yaxis=dict(title='', gridcolor='lightgray'),  # Set Y-axis title and grid color
                margin=dict(l=40, r=40, t=40, b=40),  # Add margin
                xaxis_ticks='outside',  # Place X-axis ticks outside
                xaxis_tickcolor='lightgray',  # Set X-axis tick color
                yaxis_ticks='outside',  # Place Y-axis ticks outside
                yaxis_tickcolor='lightgray',  # Set Y-axis tick color
            )
        return fig1, fig2, change_pct, change_style

    except:
        change_pct = ""
        change_style = {}
        fig1 = go.Figure()
        fig2 = go.Figure()
        return fig1, fig2, change_pct, change_style


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
            ctbl = dmc.Table(data=genTBLContent(tbltsv), highlightOnHover=True, className='first_col_bold_tbl')
            return ctbl
        except:
            return ''
    else:
        return ''