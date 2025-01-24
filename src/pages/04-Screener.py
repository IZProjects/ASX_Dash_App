import dash
from dash import dcc, html, Input, Output, State, callback, ALL
import dash_bootstrap_components as dbc
import re
from src.mysql_connect_funcs import get_df_query

dash.register_page(__name__, name='Screener')


general = ['Sector', 'Industry', 'Number of Basic Shares', 'Number of Shares Diluted', 'Exchange', 'Market Cap', 'Enterprise Value']

valuation = ['Price to Earnings', 'Price to Book Value', 'Price to Tangible Book Value', 'Price to Sales','Price to Free Cash Flow', 'Price to Pretax Income', 'Enterprise Value to Earnings', 'Enterprise Value to Book Value',
             'Enterprise Value to Tangible Book Value','Enterprise Value to Sales','Enterprise Value to Free Cash Flow', 'Enterprise Value to Pretax Income']

efficiency = ['Return on Assets', 'Return on Equity', 'Return on Invested Capital', 'Return on Capital Employed','Return on Average Tangible Common Equity', 'Return on Investment', 'Average 5 Yr Return on Invested Capital']

IS = ['Revenue', 'Cost of Goods Sold', 'Gross Profit', 'Selling, General and Admin Expenses', 'Research & Development', 'Total Operating Expenses','EBITDA',
     'Operating Income', 'Pre-tax Income', 'Net Income', 'EPS - Basic', 'EPS - Diluted', 'Revenue per Share', 'EBITDA per Share', 'Operating Income per Share', 'Pretax Income per Share']

margins = ['Gross Margin', 'EBITDA Margin', 'Operating Margin', 'Pretax Margin', 'Net Income Margin', 'Underwriting Margin', 'Free Cash Flow Margin']

IS_growth = ['Revenue Growth', 'Gross Profit Growth', 'EBITDA Growth', 'Operating Income Growth', 'Pre-Tax Income Growth', 'Net Income Growth', 'Diluted EPS Growth', 'Number of Diluted Shares Growth', 'Net Interest Margin',
             'Net Interest Income Growth','Policy Revenue Growth']

BS = ['Cash & Cash Equivalent', 'Receivables', 'Inventories', 'Total Current Assets','Plant, Property & Equipment (Net)', 'Intangible Assets', 'Total Assets', 'Accounts Payble', 'Short Term Debt',
      'Long Term Debt', 'Capital Leases','Total Liabilities', 'Total Equity', 'Long Term Debt & Capital Lease Obligations', 'Loans (Net)','Total Investments',
      'Total Non-Current Assets', 'Total Non-Current Liabilities','Net Debt', 'Book Value', 'Tangible Book Value']

BS_ratios = ['Current Ratio', 'Asset to Equity','Equity to Assets', 'Debt to Equity', 'Debt to Assets', 'Earning Asset to Equity', 'Loans to Deposits', 'Loan Loss Reserve to Loans']

BS_growth = ['Cash & Cash Equivilants Growth', 'Plant, Property and Equipment Growth', 'Total Asset Growth', 'Total Equity Growth', 'Capital Expenditure Growth', 'Gross Loans Growth',
             'Net Loans Growth', 'Deposits Growth','Earning Assets Growth','Total Investments Growth', 'Premiums Growth']

CF = ['Cash from Operations', 'Acquisitions (Net)', 'Investments (Net)', 'Intangibles (Net)', 'Cash from Investing','Net Common Stock Issued', 'Net Preferred Stock Issued', 'Net Debt Issued', 'Cash from Financing', 'Net Change in Cash',
     'Capital Expenditure', 'Common Stock Issued', 'Common Stock Repurchased', 'Preferred Stock Issued', 'Preferred Stock Repurchased', 'Debt Issued', 'Debt Repaid', 'Free Cash Flow per Share','Payout Ratio']

CF_growth = ['Free Cash Flow Growth','Operating Cash Flow Growth','Capital Expenditure Growth','Dividends per Share Growth']



checklists_details = [[general,'General'], [valuation, 'Valuations'], [efficiency, 'Efficiency'], [IS, 'Income Statement Items'], [margins, 'Margins'],
                      [IS_growth, 'Income Statement Growth'], [BS, 'Balance Sheet Items'], [BS_ratios, 'Balance Sheet Ratios'],
                      [BS_growth, 'Balance Sheet Growth'], [CF, 'Cash Flow Statement Items'], [CF_growth, 'Cash Flow Statement Growth']]

initially_checked = ["Sector","Market Cap","Price to Earnings"]


#for formatting
percentages = ['Gross Margin', 'EBITDA Margin', 'Operating Margin', 'Pretax Margin', 'Net Income Margin', 'Revenue Growth', 'Gross Profit Growth', 'EBITDA Growth', 'Operating Income Growth', 'Pre-Tax Income Growth',
               'Net Income Growth', 'Diluted EPS Growth', 'Number of Diluted Shares Growth', 'Net Interest Margin', 'Net Interest Income Growth',
               'Underwriting Margin', 'Policy Revenue Growth','Income Tax Rate', 'Cash & Cash Equivilants Growth', 'Plant, Property and Equipment Growth', 'Total Asset Growth', 'Total Equity Growth', 'Capital Expenditure Growth',
               'Gross Loans Growth', 'Net Loans Growth', 'Deposits Growth','Earning Assets Growth', 'Premiums Growth',
               'Total Investments Growth', 'Free Cash Flow Margin', 'Free Cash Flow Growth','Operating Cash Flow Growth','Capital Expenditure Growth','Payout Ratio',
               'Dividends per Share Growth', 'Return on Assets', 'Return on Equity', 'Return on Invested Capital', 'Return on Capital Employed',
               'Return on Average Tangible Common Equity', 'Number of Diluted Shares Growth', 'Return on Investment', 'Average 5 Yr Return on Invested Capital']

twoDP = ['EBITDA','Revenue per Share', 'EBITDA per Share', 'Operating Income per Share', 'Pretax Income per Share', 'Asset to Equity','Equity to Assets', 'Debt to Equity', 'Debt to Assets',
         'Earning Asset to Equity', 'Loans to Deposits', 'Loan Loss Reserve to Loans', 'Premiums per Share', 'Current Ratio', 'Free Cash Flow per Share', 'Price to Earnings', 'Price to Book Value', 'Price to Tangible Book Value', 'Price to Sales',
         'Price to Free Cash Flow', 'Price to Pretax Income', 'Enterprise Value to Earnings', 'Enterprise Value to Book Value', 'Enterprise Value to Tangible Book Value','Enterprise Value to Sales', 'Enterprise Value to Free Cash Flow', 'Enterprise Value to Pretax Income']

KMB = ['Policy Revenue', 'Underwriting Profit','Net Operating Profit After Tax', 'Share Count', 'Market Cap', 'Enterprise Value', 'Earning Assets', 'Net Debt','Net Income', 'Depreciation & Amortization', 'Accounts Receivable', 'Inventory', 'Prepaid Expenses', 'Other Working Capital', 'Change in Working Capital', 'Deferred Tax',
     'Stock Compensation', 'Other Non Cash Items', 'Cash from Operations', 'Plant, Property   Equipment  Net ', 'Acquisitions  Net ', 'Investments  Net ', 'Intangibles  Net ', 'Other', 'Cash from Investing',
     'Net Common Stock Issued', 'Net Preferred Stock Issued', 'Net Debt Issued', 'Dividends Paid', 'Cash from Financing', 'Forex', 'Net Change in Cash',
     'Capital Expenditure', 'Purchases of Plant  Property   Equipment', 'Sales of Plant  Property   Equipment', 'Acquisitions', 'Divestitures', 'Investment Purchases', 'Investment Sales',
     'Common Stock Issued', 'Common Stock Repurchased', 'Preferred Stock Issued', 'Preferred Stock Repurchased', 'Debt Issued', 'Debt Repaid', 'Cash   Cash Equivalent', 'Short Term Investments', 'Receivables', 'Inventories', 'Other Current Assets', 'Total Current Assets', 'Equity   Other Investments', 'Plant, Property   Equipment  Gross ',
      'Accumulated Depreciation', 'Plant  Property   Equipment  Net ', 'Intangible Assets', 'Goodwill', 'Other Long Term Assets', 'Total Assets', 'Accounts Payble', 'Tax Payable', 'Current Accrued Liabilities', 'Short Term Debt',
      'Current Deferred Revenue', 'Current Deferred Tax Liability', 'Long Term Debt', 'Capital Leases', 'Pension Liabilities', 'Non current Deferred Revenue', 'Other Non Current Liabilities',
      'Total Liabilities', 'Common Stock', 'Preferred Stock', 'Retained Earnings', 'Accumulated Other Comprehensive Income', 'Additional Paid In Capital', 'Treasury Stock', 'Other Equity', 'Minority Interest Liability',
      'Total Equity', 'Total Liabilities   Equity', 'Long Term Debt   Capital Lease Obligations', 'Loans  gross ', 'Allowance For Loan Losses', 'Loans  Net ','Total Investments', 'Deposit Liability', 'Deferred Policy Acquisition Cost', 'Unearned Premiums',
      'Future Policy Benifits', 'Current Capital Leases', 'Total Non Current Assets', 'Total Non Current Liabilities', 'Unearned Income', 'Revenue', 'Cost of Goods Sold', 'Gross Profit', 'Selling  General and Admin Expenses', 'Research   Development', 'One time Charges', 'Other Operating Expenses', 'Total Operating Expenses',
     'Operating Income', 'Net Interest Income', 'Other Non Operating Expense', 'Pre tax Income', 'Income Tax', 'Net Income from Continuing Operations', 'Interest Income', 'Interest Expense',
     'Net Income from Discontinued Operations', 'Income Allocated to Minority Interest', 'Other', 'Net Income', 'Preferred Dividends', 'Net Income Avaliable to Shareholders', 'EPS - Basic',
     'EPS   Diluted', 'Number of Basic Shares', 'Number of Shares Diluted', 'Total Interest Income', 'Total Interest Expense', 'Total Non Interest Revenue',
     'Provision for Credit Losses', 'Net Income after Credit Loss Provisions', 'Total Non Interest Expense', 'Premiums Earned', 'Net Investment Income', 'Fees and Other Income',
     'Net Policy Holder Claims Expense', 'Policy Acquasition Expense', 'Book Value', 'Tangible Book Value']

def sanitize_column_name(col_name):
    return re.sub(r'\W+', '_', col_name)

def sanitize_column_name2(col_name):
    return re.sub(r'\W+', ' ', col_name)
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


def create_link(item):
    return dcc.Link(item[:-3], href='/02-companyoverview?data='+item, id=f'link-{item}')
def generate_checklists(main_list, label):
    """Generate rows of columns with checklists from a given valuation list, including a main label."""
    # Split the list into sublists of 4 items each
    sublists = [main_list[i:i + 3] for i in range(0, len(main_list), 3)]

    # Create rows with checklists in columns for each sublist
    rows = [dbc.Label(label, style={'fontSize': '16px', 'fontWeight': 'bold', 'margin-top': '20px'})]
    for sublist_index, sublist in enumerate(sublists):
        columns = []
        for item in sublist:
            if item in initially_checked:
                columns.append(
                    dbc.Col(
                        dcc.Checklist(
                            options=[{'label': html.Div(item, style={'font-size': 14, 'padding-left': 10}), 'value': item}],
                            value=[item],
                            id={'type': 'dynamic-checklist', 'index': f'{label}-{item}'},
                            labelStyle={'display': 'flex'}
                        ),
                        width=4  # Adjust column width as needed
                    )
                )
            else:
                columns.append(
                    dbc.Col(
                        dcc.Checklist(
                            options=[{'label': html.Div(item, style={'font-size': 14, 'padding-left': 10}), 'value': item}],
                            id={'type': 'dynamic-checklist', 'index': f'{label}-{item}'},
                            labelStyle={'display': 'flex'}
                        ),
                        width=4  # Adjust column width as needed
                    )
                )
        # Add a label before each row of sublist
        rows.append(dbc.Row(columns, style={'margin-bottom': '10px'}))
    return rows

layout_content = []
for checklists, label in checklists_details:
    layout_content.extend(generate_checklists(checklists, label))


modal = html.Div(
    [
        dbc.Button(children='+ add another filter', size='sz', outline=True, color="primary", n_clicks=0, id="open-centered"),
        dbc.Modal(
            [
                dbc.ModalHeader(dbc.ModalTitle("Stock Screener"), close_button=True, style={'margin-bottom': '-20px'}),
                dbc.ModalBody(html.Div(layout_content)),
                dbc.ModalFooter(
                    dbc.Button(
                        "Close",
                        id="close-centered",
                        className="ms-auto",
                        n_clicks=0,
                    )
                ),
            ],
            id="modal-centered",
            centered=True,
            is_open=False,
            scrollable=True,
            size='xl'
        ),
    ]
)


# Layout
layout = dbc.Spinner(dbc.Container([
    dcc.Store(id='store-selected-values', storage_type='session',data={}),
    dcc.Store(id='store-selected-values', storage_type='session',data={}),
    dcc.Store(id='store_numeric', storage_type='session',data={}),
    dcc.Store(id='store_singular', storage_type='session',data={}),
    dcc.Store(id='store_ratio', storage_type='session',data={}),
    dcc.Store(id='store_pct', storage_type='session',data={}),
    dcc.Store(id='store_sector', storage_type='session',data={}),
    dcc.Store(id='store_industry', storage_type='session',data={}),
    dcc.Store(id='store_exchange', storage_type='session',data={}),
    dcc.Store(id='query', storage_type='session',data={}),
    dbc.Row(id='cards_section', style={'margin-bottom': '20px'}),
    dbc.Row([dbc.Col(modal, width=11), dbc.Col(dbc.Button('Submit', id='submit_button', color='primary', outline=True))]),
    dbc.Row(id='output-container', style={'margin-top': '20px'}),
]),color="primary",delay_hide=10,delay_show=15,spinner_style={"position":"absolute", "top":"20%"})

@callback(
    [Output('cards_section', 'children'),
     Output('store_ratio', 'data'),
     Output('store_pct', 'data'),
     Output('store_singular', 'data'),
     Output('store_numeric', 'data'),
     Output('store_sector', 'data'),
     Output('store_industry', 'data'),
     Output('store_exchange', 'data')],
    Input({'type': 'dynamic-checklist', 'index': ALL}, 'value')
)
def generate_cards(*selected_values):
    selected_list = [item[0] for sublist in selected_values for item in sublist if item]

    rows = []

    ratio_items = valuation + BS_ratios + ['Payout Ratio']
    percentage_items = efficiency + margins + IS_growth + BS_growth + CF_growth
    singular_items = ['EPS - Basic', 'EPS - Diluted', 'Revenue per Share', 'EBITDA per Share', 'Operating Income per Share',
                'Pretax Income per Share', 'Free Cash Flow per Share']
    numeric = []
    singular = []
    ratio = []
    pct = []
    sector = []
    industry = []
    exchange = []

    morningstar_sectors = ['Utilities','Financial','Financial Services','Communication Services','Healthcare','Industrials',
                         'Energy','Consumer Cyclical','Consumer Defensive','Technology','Real Estate','N/A','None','Basic Materials']

    morningstar_industry = ['Entertainment','Beverages :  Brewers', 'Diagnostics & Research','Oil & Gas E&P','Health Information Services','Education & Training Services',
                            'Copper','REIT :  Retail','Security & Protection Services','Restaurants','Personal Services','Electrical Equipment & Parts',
                            'Software :  Infrastructure','Luxury Goods','Software :  Application','N/A','REIT :  Healthcare Facilities','REIT :  Diversified','Banks :  Diversified',
                            'Credit Services','Biotechnology','Medical Devices','Drug Manufacturers :  Specialty & Generic','Asset Management','Insurance :  Property & Casualty',
                            'Utilities :  Renewable','Electronic Gaming & Multimedia','Auto Parts','None','Grocery Stores','Gold','Telecom Services','Building Products & Equipment',
                            'Internet Retail','Engineering & Construction','Scientific & Technical Instruments','Software: Application','Banks :  Regional','Rental & Leasing Services',
                            'Information Technology Services','Oil & Gas Refining & Marketing','Staffing & Employment Services','Packaged Foods','Specialty Business Services','Specialty Chemicals',
                            'Medical Care Facilities','Electronic Components','Coking Coal','Other Precious Metals & Mining','Mortgage Finance','Other Industrial Metals & Mining','Internet Content & Information']

    for item in selected_list:
        cardNumeric = dbc.Card(
            dbc.CardBody(
                dbc.Row([
                    dbc.Col(html.Div(item, style={'font-size': 14, 'fontWeight': 'bold'}), width=3),
                    dbc.Col(dcc.Dropdown(['Greater than', 'Less Than', 'Equal to'], 'Greater than',id={'type': 'numeric_compare', 'index': item}, searchable=False, persistence=True, persistence_type ='memory'), width=2),
                    dbc.Col(dbc.Input(placeholder="Input goes here...",type="number", id={'type': 'numeric_input', 'index': item}, persistence=True, persistence_type ='memory'), width=3),
                    dbc.Col(dcc.Dropdown(['Thousands', 'Millions', 'Billions'], 'Millions', id={'type': 'numeric_unit', 'index': item}, searchable=False, persistence=True, persistence_type ='memory'), width=2),
                    dbc.Col(dcc.Dropdown(['Filter', 'Display'], 'Filter', id={'type': 'numeric_type', 'index': item}, searchable=False, persistence=True, persistence_type ='memory'), width=2)
                ])
            )
        )
        cardSingularNumeric = dbc.Card(
            dbc.CardBody(
                dbc.Row([
                    dbc.Col(html.Div(item, style={'font-size': 14, 'fontWeight': 'bold'}), width=3),
                    dbc.Col(dcc.Dropdown(['Greater than', 'Less Than', 'Equal to'], 'Greater than',id={'type': 'singular_compare', 'index': item}, searchable=False, persistence=True, persistence_type ='memory'), width=2),
                    dbc.Col(dbc.Input(placeholder="Input goes here...",type="number", id={'type': 'singular_input', 'index': item}, persistence=True, persistence_type ='memory', required = 'True'), width=5),
                    dbc.Col(dcc.Dropdown(['Filter', 'Display'], 'Filter', id={'type': 'singular_type', 'index': item}, searchable=False, persistence=True, persistence_type ='memory'), width=2)
                ])
            )
        )
        cardSector = dbc.Card(
            dbc.CardBody(
                dbc.Row([
                    dbc.Col(html.Div(item, style={'font-size': 14, 'fontWeight': 'bold'}), width=3),
                    dbc.Col(dcc.Dropdown(morningstar_sectors, id={'type': 'sector_select', 'index': item}, multi=True, persistence=True, persistence_type ='memory'), width=7),
                    dbc.Col(dcc.Dropdown(['Filter', 'Display'], 'Filter', id={'type': 'sector_type', 'index': item}, searchable=False, persistence=True, persistence_type ='memory'), width=2)
                ])
            )
        )
        cardIndustry = dbc.Card(
            dbc.CardBody(
                dbc.Row([
                    dbc.Col(html.Div(item, style={'font-size': 14, 'fontWeight': 'bold'}), width=3),
                    dbc.Col(dcc.Dropdown(morningstar_industry, id={'type': 'industry_select', 'index': item}, multi=True, persistence=True, persistence_type ='memory'), width=7),
                    dbc.Col(dcc.Dropdown(['Filter', 'Display'], 'Filter', id={'type': 'industry_type', 'index': item}, searchable=False, persistence=True, persistence_type ='memory'), width=2)
                ])
            )
        )
        cardExchange = dbc.Card(
            dbc.CardBody(
                dbc.Row([
                    dbc.Col(html.Div(item, style={'font-size': 14, 'fontWeight': 'bold'}), width=3),
                    dbc.Col(dcc.Dropdown(['ASX'], id={'type': 'exchange_select', 'index': item}, multi=True, persistence=True, persistence_type ='memory'), width=7),
                    dbc.Col(dcc.Dropdown(['Filter', 'Display'], 'Filter', id={'type': 'exchange_type', 'index': item}, searchable=False, persistence=True, persistence_type ='memory'), width=2)
                ])
            )
        )
        cardRatio = dbc.Card(
            dbc.CardBody(
                dbc.Row([
                    dbc.Col(html.Div(item, style={'font-size': 14, 'fontWeight': 'bold'}), width=3),
                    dbc.Col(dcc.Dropdown(['Greater than', 'Less Than', 'Equal to'], 'Greater than', id={'type': 'ratio_compare', 'index': item}, searchable=False, persistence=True, persistence_type ='memory'), width=2),
                    dbc.Col(dbc.Input(placeholder="Input goes here...",type="number", id={'type': 'ratio_input', 'index': item}, persistence=True, persistence_type ='memory'), width=3),
                    dbc.Col(dcc.Dropdown(['Ratio'], 'Ratio', id={'type': 'ratio_unit', 'index': item}, searchable=False), width=2),
                    dbc.Col(dcc.Dropdown(['Filter', 'Display'], 'Filter', id={'type': 'ratio_type', 'index': item}, searchable=False, persistence=True, persistence_type ='memory'), width=2)
                ])
            )
        )
        cardPercentage = dbc.Card(
            dbc.CardBody(
                dbc.Row([
                    dbc.Col(html.Div(item, style={'font-size': 14, 'fontWeight': 'bold'}), width=3),
                    dbc.Col(dcc.Dropdown(['Greater than', 'Less Than', 'Equal to'], 'Greater than', id={'type': 'pct_compare', 'index': item}, searchable=False, persistence=True, persistence_type ='memory'), width=2),
                    dbc.Col(dbc.Input(placeholder="Input goes here...",type="number", id={'type': 'pct_input', 'index': item}, min=-100, max=100, persistence=True, persistence_type ='memory'), width=3),
                    dbc.Col(dcc.Dropdown(['%'], '%', id={'type': 'pct_unit', 'index': item}, searchable=False), width=2),
                    dbc.Col(dcc.Dropdown(['Filter', 'Display'], 'Filter', id={'type': 'pct_type', 'index': item}, searchable=False, persistence=True, persistence_type ='memory'), width=2)
                ])
            )
        )

        if item == 'Sector':
            rows.append(
                dbc.Row(cardSector, style={'margin-bottom': '10px'})
            )
            sector.append(item)
        elif item == "Industry":
            rows.append(
                dbc.Row(cardIndustry, style={'margin-bottom': '10px'})
            )
            industry.append(item)
        elif item == "Exchange":
            rows.append(
                dbc.Row(cardExchange, style={'margin-bottom': '10px'})
            )
            exchange.append(item)
        elif item in ratio_items:
            rows.append(
                dbc.Row(cardRatio, style={'margin-bottom': '10px'})
            )
            ratio.append(item)
        elif item in percentage_items:
            rows.append(
                dbc.Row(cardPercentage, style={'margin-bottom': '10px'})
            )
            pct.append(item)
        elif item in singular_items:
            rows.append(
                dbc.Row(cardSingularNumeric, style={'margin-bottom': '10px'})
            )
            singular.append(item)
        else:
            rows.append(

                dbc.Row(cardNumeric, style={'margin-bottom': '10px'})
            )
            numeric.append(item)

    return rows, ratio, pct, singular, numeric, sector, industry, exchange


@callback(
    Output('output-container', 'children'),
    [Input('submit_button', 'n_clicks'),
     Input('store_ratio', 'data'),
     Input('store_pct', 'data'),
     Input('store_singular', 'data'),
     Input('store_numeric', 'data'),
     Input('store_sector', 'data'),
     Input('store_industry', 'data'),
     Input('store_exchange', 'data'),],
    State({'type': 'numeric_compare', 'index': ALL}, 'value'),
    State({'type': 'numeric_input', 'index': ALL}, 'value'),
    State({'type': 'numeric_unit', 'index': ALL}, 'value'),
    State({'type': 'numeric_type', 'index': ALL}, 'value'),
    State({'type': 'singular_compare', 'index': ALL}, 'value'),
    State({'type': 'singular_input', 'index': ALL}, 'value'),
    State({'type': 'singular_type', 'index': ALL}, 'value'),
    State({'type': 'sector_select', 'index': ALL}, 'value'),
    State({'type': 'sector_type', 'index': ALL}, 'value'),
    State({'type': 'industry_select', 'index': ALL}, 'value'),
    State({'type': 'industry_type', 'index': ALL}, 'value'),
    State({'type': 'exchange_select', 'index': ALL}, 'value'),
    State({'type': 'exchange_type', 'index': ALL}, 'value'),
    State({'type': 'ratio_compare', 'index': ALL}, 'value'),
    State({'type': 'ratio_input', 'index': ALL}, 'value'),
    State({'type': 'ratio_type', 'index': ALL}, 'value'),
    State({'type': 'pct_compare', 'index': ALL}, 'value'),
    State({'type': 'pct_input', 'index': ALL}, 'value'),
    State({'type': 'pct_type', 'index': ALL}, 'value')
)
def print_values(n_clicks, ratio_items, pct_items, singular_items, numeric_items, sector_items, industry_items, exchange_items, numeric_compare, numeric_input, numeric_unit, numeric_type, singular_compare,singular_input,
                 singular_type,sector_select,sector_type,industry_select,industry_type,exchange_select,exchange_type,ratio_compare,
                 ratio_input,ratio_type,pct_compare,pct_input,pct_type):
    if n_clicks is None:
        return ''

    text_to_symbol = {
        'Greater than': '>',
        'Less Than': '<',
        'Equal to': '='
    }

    try:
        sql_query_conditions = []
        sql_query_conditions = []
        if len(numeric_items) > 0:
            numeric_symbols = [text_to_symbol[text] for text in numeric_compare]
            for i in range(len(numeric_unit)):
                if numeric_type[i] == 'Filter':
                    if numeric_unit[i] == 'Thousands':
                        numeric_input[i] = numeric_input[i] * 1000
                    elif numeric_unit[i] == 'Millions':
                        numeric_input[i] = numeric_input[i] * 1000000
                    else:
                        numeric_input[i] = numeric_input[i] * 1000000000
            numeric_items = [s.replace(' ', '_') for s in numeric_items]
            for items in zip(numeric_items, numeric_symbols, numeric_input, numeric_type):
                if items[3] == 'Filter':
                    sql_query_conditions.append(' '.join(map(str, items[:3])))

        if len(singular_items) > 0:
            singular_symbols = [text_to_symbol[text] for text in singular_compare]
            singular_items = [s.replace(' ', '_') for s in singular_items]
            for items in zip(singular_items, singular_symbols, singular_input, singular_type):
                if items[3] == 'Filter':
                    sql_query_conditions.append(' '.join(map(str, items[:3])))

        if len(ratio_items) > 0:
            ratio_symbols = [text_to_symbol[text] for text in ratio_compare]
            ratio_items = [s.replace(' ', '_') for s in ratio_items]
            for items in zip(ratio_items, ratio_symbols, ratio_input, ratio_type):
                if items[3] == 'Filter':
                    sql_query_conditions.append(' '.join(map(str, items[:3])))

        if len(pct_items) > 0:
            pct_symbols = [text_to_symbol[text] for text in pct_compare]
            pct_input = [pct_input[i]/100 for i in range(len(pct_input)) if pct_type[i]=='Filter']
            pct_items = [s.replace(' ', '_') for s in pct_items]
            for items in zip(pct_items, pct_symbols, pct_input, pct_type):
                if items[3] == 'Filter':
                    sql_query_conditions.append(' '.join(map(str, items[:3])))

        if len(sector_items) > 0:
            if sector_type[0] == "Filter":
                sector_select = str(sector_select[0]).replace('[', '(').replace(']', ')')
                sql_query_conditions.append('Sector IN '+sector_select)

        if len(industry_items) > 0:
            if industry_type[0] == "Filter":
                industry_select = str(industry_select[0]).replace('[', '(').replace(']', ')')
                sql_query_conditions.append('Industry IN '+industry_select)

        if len(exchange_items) > 0:
            if exchange_type[0] == "Filter":
                exchange_select = str(exchange_select[0]).replace('[', '(').replace(']', ')')
                sql_query_conditions.append('Exchange IN '+exchange_select)

        items = ratio_items + pct_items + singular_items + numeric_items + sector_items + industry_items + exchange_items
        items = [s.replace(' ', '_') for s in items]
        items = [sanitize_column_name(col) for col in items]
        select = ', '.join(items)

        if len(sql_query_conditions) > 0:
            sql_query_conditions[0] = 'WHERE ' + sql_query_conditions[0]
            for i in range(1,len(sql_query_conditions)):
                sql_query_conditions[i] = 'AND ' + sql_query_conditions[i]
            sql_query_conditions[-1] = sql_query_conditions[-1] + ';'
            conditions = ' '.join(sql_query_conditions)
        else:
            conditions=''
        #query = "SELECT Item, Name, " + select + " FROM Screener_TBL " + conditions
        query = (
                "SELECT Screener_TBL1.Item, Screener_TBL2.Name, " + select + " " +
                "FROM Screener_TBL1 " +
                "JOIN Screener_TBL2 " +
                "ON Screener_TBL1.Item = Screener_TBL2.Item " +
                conditions
        )
    except:
        return html.H4("ERROR: Please check the filters and submit again")

    if 'None' in query:
        return html.H4("ERROR: Please check the filters and submit again")

    else:

        #conn = sqlite3.connect('databases/Financials_DB.db')
        #df = pd.read_sql_query(query, conn)
        #conn.close()
        df = get_df_query(query)
        df.columns = df.columns.str.replace('_', ' ')
        df = df.drop_duplicates(subset=["Item"], keep="first")
        df = df.reset_index(drop=True)
        new_df = df.copy()
        new_df['Item'] = df['Item'].apply(create_link)
        twoDPUpdated = [col for col in twoDP if col in new_df.columns]
        new_df[twoDPUpdated] = new_df[twoDPUpdated].map(lambda x: round(float(x), 2))
        KMBUpdated = [col for col in KMB if col in new_df.columns]
        KMBUpdated = list(set(KMBUpdated))
        new_df[KMBUpdated] = new_df[KMBUpdated].map(format_number)
        table = dbc.Table.from_dataframe(new_df, striped=True, bordered=True, hover=True)
        return table



@callback(
    Output("modal-centered", "is_open"),
    [Input("open-centered", "n_clicks"), Input("close-centered", "n_clicks")],
    [State("modal-centered", "is_open")],
)
def toggle_modal(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open











