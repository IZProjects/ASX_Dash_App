import dash
from dash import html, Input, Output, callback, dash_table, clientside_callback
import dash_bootstrap_components as dbc
import pandas as pd
import dash_mantine_components as dmc
from mysql_connect_funcs import get_df_tblName

dash.register_page(__name__, name='Financials')
def convert_to_percentage(value):
    return f"{float(value) * 100:.2f}%"
def format_number(x):
    if pd.isna(x):  # Handle NaN values if present
        return ''
    elif x == int(x):
        return f"{int(x):,}"
    else:
        return f"{x:,.2f}"

def find_negative_values(df):
    negative_values = []
    first_column_skipped = False  # Flag to skip the first column
    for col in df.columns:
        if not first_column_skipped:
            first_column_skipped = True
            continue  # Skip the first column
        for index, value in df[col].items():
            if isinstance(value, str) and '-' in value:
                negative_values.append((col, index))
            elif isinstance(value, (int, float)) and value < 0:
                negative_values.append((col, index))
    return negative_values


def reverse_columns(df):
    # Copy the DataFrame to avoid modifying the original one
    df_copy = df.copy()

    # Reverse the order of columns except the first one
    cols = list(df.columns)
    cols = [cols[0]] + cols[1:][::-1]
    df_copy = df_copy[cols]

    return df_copy


button_group1 = dmc.SegmentedControl(
    id="radios_statement",
    value='income_statement',
    color='indigo',
    size='md',
    data=[
        {"label": "Income Statement", "value": 'income_statement'},
        {"label": "Balance Sheet", "value": 'balance_sheet'},
        {"label": "Cashflow Statement", "value": 'cash_flow_statement'},
        {"label": "Key Ratios", "value": 'key_ratios'},
    ],
)


button_group2 = dmc.SegmentedControl(
    id="radios_period",
    color='indigo',
    size='md',
    data=[
        {"label": "Annual", "value": "annual"},
        {"label": "Quarterly", "value": "quarterly"},
    ],
    value="annual"
)


button_group3 = dmc.SegmentedControl(
    id="radios_units",
    color='indigo',
    data=[
        {"label": "K", "value": "K"},
        {"label": "M", "value": "M"},
        {"label": "B", "value": "B"},
    ],
    value="M",
)


button_group4 = dmc.SegmentedControl(
    id="radios_direction",
    color='indigo',
    data=[
        {"label": "Forward", "value": "Forward"},
        {"label": "Reverse", "value": "Reverse"},
    ],
    value="Forward",
)

export_btn = dmc.Button("Export", id='exportBtn', color="gray")

export_btn2 = dmc.Button("Export", id='exportBtn2', color="gray")



# Layout
layout = dbc.Spinner(dbc.Container([
    dbc.Row([
        dbc.Col([dbc.Row(html.H2(id='stock_name')),
                 dbc.Row(html.Span([
                     dbc.Badge(id='currency_badge', color="primary", className="me-1"),
                     dbc.Badge(id='sector_badge', color="warning", className="me-1"),
                     dbc.Badge(id='industry_badge', color="danger", className="me-1"),
                     dbc.Badge(id='category_badge', color="dark", className="me-1")]))
                 ], width=10),
        dbc.Col([dbc.Row(html.H2(id='stock_price')),
                 dbc.Row(html.P(id="price_change"),id='price_change_row')],
                width=2, style={'text-align': 'right'}),
    ], style={'margin-bottom': '10px'}),
    dbc.Row(html.Hr()),

    dbc.Row([dbc.Col(button_group1, width=10),
             dbc.Col(button_group2, width=2)], style={'margin-bottom': '20px'}),

    dbc.Row([dbc.Card([dbc.CardHeader(dbc.Row([dbc.Col(html.H4(id='statement_name'), width=4),
                                               dbc.Col(button_group3, width=3),
                                               dbc.Col(button_group4, width=4),
                                               dbc.Col(export_btn, width=1)])),
                       dbc.CardBody([dbc.Row([dbc.Col(id='table-container', width=12)], style={'margin-bottom': '40px'}),
                                    dbc.Row([dbc.Col(width=11, id='sup_title'),
                                             dbc.Col(export_btn2, width=1, id='sup_title_row')]),
                                    dbc.Row([dbc.Col(id='table-container2', width=12)], id='table2_row')]
                                    )])])
]),color="primary",delay_hide=10,delay_show=15,spinner_style={"position":"absolute", "top":"20%"})


@callback(
    [Output(component_id='table-container', component_property='children'),
     Output(component_id='statement_name', component_property='children'),
     Output(component_id='sup_title', component_property='children')],
    [Input(component_id='radios_statement', component_property='value'),
     Input(component_id='radios_period', component_property='value'),
     Input(component_id='radios_units', component_property='value'),
     Input(component_id='radios_direction', component_property='value'),
     Input(component_id="ticker", component_property="data")]
)
def create_table(statement, period, units, direction, ticker):
    try:
        title = statement.replace('_', ' ')
        title = title.title()

        if ticker is None:
            ticker = "TPG_AU"

        table = ticker+'_'+period+'_'+statement

        df = get_df_tblName(table)

        if units =='K':
            divider = 1000
        elif units == 'M':
            divider = 1000000
        else:
            divider = 1000000000

        if statement != 'key_ratios':
            mask = ~df['Item'].isin(['EPS - Basic', 'EPS - Diluted'])
            df = df.astype('object')
            df.loc[mask, df.columns[1:]] = df.loc[mask, df.columns[1:]].astype(float).map(
                lambda x: format_number(x / divider))
        negatives = find_negative_values(df)

        boldIS = ['Revenue', 'Gross Profit', 'Operating Income', 'Net Income from Continuing Operations',
                  'Net Income from Discontinued Operations', 'Net Income', 'EPS - Basic', 'EPS - Diluted']
        boldBS = ['Total Current Assets', 'Total Assets', 'Total Liabilities', 'Total Equity', 'Total Liabilities & Equity',
                  'Total Non-Current Assets', 'Total Non-Current Liabilities']
        boldCF = ['Cash from Operations', 'Cash from Investing', 'Cash from Financing', 'Net Change in Cash']
        underlineIS = ['Revenue', 'Gross Profit', 'Operating Income', 'Net Income', 'EPS - Diluted']
        underlineBS = ['Total Assets', 'Total Liabilities', 'Total Equity', 'Total Liabilities & Equity']
        underlineCF = ['Cash from Operations', 'Cash from Investing', 'Cash from Financing', 'Net Change in Cash']

        if statement == 'income_statement':
            boldIndex = df.index[df['Item'].isin(boldIS)].tolist()
            underlineIndex = df.index[df['Item'].isin(underlineIS)].tolist()
        elif statement == 'balance_sheet':
            boldIndex = df.index[df['Item'].isin(boldBS)].tolist()
            underlineIndex = df.index[df['Item'].isin(underlineBS)].tolist()
        elif statement == 'cash_flow_statement':
            boldIndex = df.index[df['Item'].isin(boldCF)].tolist()
            underlineIndex = df.index[df['Item'].isin(underlineCF)].tolist()
        else:
            boldIndex = []
            underlineIndex = []

        body_style = [
                         {
                             'if': {'row_index': boldIndex},
                             'fontWeight': 'bold',
                         }
                     ] + [
                         {
                             'if': {'row_index': boldIndex},
                             'color': 'black',
                         }
                     ] + [
                         {
                             'if': {'row_index': underlineIndex},
                             'borderBottom': '2px solid black',
                         }
                     ] + [
                         {
                             'if': {'column_id': 'Item'},
                             'textAlign': 'left',
                         }
                     ] + [
                         {
                             'if': {'column_id': x, 'row_index': y},
                             'color': 'red',
                         } for x, y in negatives
                     ]

        firstColumn_style = [{
            'if': {'column_id': 'Item'},
            #'minWidth': '300px',
            'padding-right': '30px',
            'padding-left': '10px'
        }]

        firstColHeader_style = [{
            'if': {'column_id': 'Item'},
            'textAlign': 'left'
        }]


        OGcols = df.columns.tolist()
        reversed_columns = OGcols[:1] + OGcols[1:][::-1]
        df_reversed = df[reversed_columns]


        if direction == 'Forward':
            df_final = df
        else:
            df_final = df_reversed

        table = dash_table.DataTable(
            id='table',
            columns=[{"name": i, "id": i} for i in df_final.columns],
            data=df_final.to_dict('records'),
            style_header={'backgroundColor': 'rgb(30, 30, 30)',
                          'color': 'white',
                          'fontWeight': 'bold',
                          'textAlign': 'center'},
            style_header_conditional=firstColHeader_style,
            style_data_conditional=body_style,
            style_table = {'overflowX': 'auto', 'height': '800px', 'overflowY': 'auto','minWidth': '100%','z-index':'0'},
            style_cell={#'height': 'auto',
                        'minWidth': '120px', 'width': '120px', 'maxWidth': '600px',
                        #'whiteSpace': 'normal',
                        'textAlign': 'center'},
            #style_as_list_view=True,
            #fixed_columns={'headers': True, 'data': 1},
            #fixed_rows={'headers': True},
            style_cell_conditional=firstColumn_style,
            editable=False,
            export_format = 'xlsx',
            export_headers = 'display'
            )

        return table,title, html.H4("Supplementary Data")
    except:
        return '','',''


clientside_callback(
    """
    function(n_clicks) {
        if (n_clicks > 0)
            document.querySelector("#table button.export").click()
        return ""
    }
    """,
    Output("exportBtn", "data-dummy"),
    [Input("exportBtn", "n_clicks")]
)

##### sup table

@callback(
    [Output(component_id='table-container2', component_property='children'),
     Output(component_id='sup_title', component_property='style'),
     Output(component_id='sup_title_row', component_property='style'),
     Output(component_id='table2_row', component_property='style')],
    [Input(component_id='radios_statement', component_property='value'),
     Input(component_id='radios_period', component_property='value'),
     Input(component_id='radios_units', component_property='value'),
     Input(component_id='radios_direction', component_property='value'),
     Input(component_id="ticker", component_property="data")]
)
def create_table(statement, period, units, direction, ticker):
    try:
        if ticker is None:
            ticker = "TPG_AU"

        if statement == 'income_statement':
            supName = 'sup_IS'
        elif statement == 'balance_sheet':
            supName = 'sup_BS'
        elif statement == 'cash_flow_statement':
            supName = 'sup_CF'
        else:
            supName = 'Other'

        if supName != 'Other':
            table = ticker+'_'+period+'_'+supName
            df = get_df_tblName(table)
        else:
            df = pd.DataFrame(columns=['Item'])

        if units =='K':
            divider = 1000
        elif units == 'M':
            divider = 1000000
        else:
            divider = 1000000000

        noDivide = ['Gross Margin', 'EBITDA Margin', 'Operating Margin', 'Pretax Margin', 'Net Income Margin',
                'Revenue per Share', 'EBITDA per Share', 'Operating Income per Share', 'Pretax Income per Share',
                'Revenue Growth', 'Gross Profit Growth', 'EBITDA Growth', 'Operating Income Growth',
                'Pre-Tax Income Growth', 'Net Income Growth', 'Diluted EPS Growth', 'Number of Diluted Shares Growth',
                'Net Interest Margin', 'Net Interest Income Growth', '10 Yr Revenue CAGR', '10 Yr Diluted EPS CAGR',
                '10 Yr Net Interest Income CAGR', 'Underwriting Margin', 'Policy Revenue Growth', 'Income Tax Rate',
                'Asset to Equity', 'Equity to Assets', 'Debt to Equity', 'Debt to Assets',
                'Cash & Cash Equivilants Growth', 'Plant, Property and Equipment Growth', 'Total Asset Growth',
                'Total Equity Growth', 'Capital Expenditure Growth', '10 Yr Total Assets CAGR',
                '10 Yr Total Equity CAGR', 'Earning Asset to Equity', 'Loans to Deposits', 'Loan Loss Reserve to Loans',
                'Gross Loans Growth', 'Net Loans Growth', 'Deposits Growth', 'Earning Assets Growth',
                '10 Yr Gross Loan CARG', '10 Yr Earning Assets CAGR', '10 Yr Deposits CAGR', 'Premiums per Share',
                'Premiums Growth','Total Investments Growth', '10 Yr Premiums CAGR', '10 Yr Total Investments CAGR',
                'Current Ratio','Free Cash Flow Margin', 'Free Cash Flow per Share', 'Free Cash Flow Growth',
                'Operating Cash Flow Growth', 'Capital Expenditure Growth', 'Payout Ratio', 'Dividends per Share Growth',
                '10 Yr Dividends per Share CAGR', '10 Year Free Cash Flow CAGR', '10 Yr Operating Cash Flow CAGR']

        if statement == 'key_ratios':
            sup_title_style = {'margin-bottom': '20px', 'display': 'none'}
            sup_title_style2 = {'margin-bottom': '20px', 'display': 'none'}
            table_style = {'display': 'none'}
        else:
            sup_title_style = {'margin-bottom': '20px', 'display': 'block'}
            sup_title_style2 = {'margin-bottom': '20px', 'display': 'block'}
            table_style = {'display': 'block'}

        if statement != 'key_ratios':
            mask = ~df['Item'].isin(noDivide)
            df = df.astype('object')
            df.loc[mask, df.columns[1:]] = df.loc[mask, df.columns[1:]].astype(float).map(
                lambda x: format_number(x / divider))
        negatives = find_negative_values(df)

        body_style = [
                         {
                             'if': {'column_id': 'Item'},
                             'textAlign': 'left',
                         }
                     ] + [
                         {
                             'if': {'column_id': x, 'row_index': y},
                             'color': 'red',
                         } for x, y in negatives
                     ]

        firstColumn_style = [{
            'if': {'column_id': 'Item'},
            #'minWidth': '300px',
            'padding-right': '30px',
            'padding-left': '10px'
        }]

        firstColHeader_style = [{
            'if': {'column_id': 'Item'},
            'textAlign': 'left'
        }]


        OGcols = df.columns.tolist()
        reversed_columns = OGcols[:1] + OGcols[1:][::-1]
        df_reversed = df[reversed_columns]


        if direction == 'Forward':
            df_final = df
        else:
            df_final = df_reversed

        table = dash_table.DataTable(
            id='table2',
            columns=[{"name": i, "id": i} for i in df_final.columns],
            data=df_final.to_dict('records'),
            style_header={'backgroundColor': 'rgb(30, 30, 30)',
                          'color': 'white',
                          'fontWeight': 'bold',
                          'textAlign': 'center'},
            style_header_conditional=firstColHeader_style,
            style_data_conditional=body_style,
            style_table = {'overflowX': 'auto', 'height': '800px', 'overflowY': 'auto','minWidth': '100%','z-index':'0'},
            style_cell={#'height': 'auto',
                        'minWidth': '120px', 'width': '120px', 'maxWidth': '600px',
                        #'whiteSpace': 'normal',
                        'textAlign': 'center'},
            #style_as_list_view=True,
            style_cell_conditional=firstColumn_style,
            fixed_columns={'headers': True, 'data': 1},
            #fixed_rows={'headers': True},
            editable=False,
            export_format = 'xlsx',
            export_headers = 'display'
            )

        return table, sup_title_style, sup_title_style2, table_style
    except:
        return '','','',''

clientside_callback(
    """
    function(n_clicks) {
        if (n_clicks > 0)
            document.querySelector("#table2 button.export").click()
        return ""
    }
    """,
    Output("exportBtn2", "data-dummy"),
    [Input("exportBtn2", "n_clicks")]
)
