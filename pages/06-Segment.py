import dash
from dash import html, callback, Output, Input, dash_table, dcc
import dash_mantine_components as dmc
from mysql_connect_funcs import get_cursor, get_df_query
import re

dash.register_page(__name__, name='Business Profile', title='Business Profile', description='Get a summary of all the key information about the business')

layout = dmc.Box([
    html.H1(children="Business Profile | Tickersight", hidden=True),
    dmc.Grid([
        dmc.GridCol([dmc.Grid(dmc.Title(id='stock_name', order=2), style={'margin-bottom': '10px'}),
                     dmc.Grid(
                         dmc.Group([
                             dmc.Badge(id='currency_badge', color="indigo", className="me-1"),
                             dmc.Badge(id='sector_badge', color="red", className="me-1"),
                             dmc.Badge(id='industry_badge', color="violet", className="me-1"),
                         ], gap='sm')
                     )
                     ], span={"base": 8, "md": 10}),
        dmc.GridCol([dmc.Grid(dmc.Title(id='stock_price', order=2), style={'margin-bottom': '10px'}),
                     dmc.Grid(dmc.Text(id="price_change", size='md'), id='price_change_row', style={'margin-bottom': '10px'}),
                     dmc.Grid(dmc.Text("Delayed price data ", style={"fontSize": 11,'margin-top': '10px'}, c="gray"))],
                    span='content', offset='auto'),
    ], justify='space-between',
        style={'margin-bottom': '20px', 'margin-top': '20px', 'margin-left': '20px', 'margin-right': '20px'}),

    dmc.Container(html.Hr(), fluid=True),

    dmc.Container(id='SegmentDescriptionRow', fluid=True, style={'margin-bottom': '20px'}),
    dmc.Container(id='SegmentResultsTitle', fluid=True, style={'margin-top': '20px', 'margin-bottom': '5px'}),

    dmc.Container(html.Hr(), fluid=True, style={'margin-top': '50px', 'margin-bottom': '20px'}),

    dmc.Group([dcc.Markdown(f'[Terms and Conditions](/toc)'),dcc.Markdown(f'[Privacy Policy](/privacy-policy)')], gap='md', justify='flex-end'),


])

@callback(
    Output(component_id='SegmentDescriptionRow', component_property='children'),
    Input("ticker", "data"),
)
def get_segmentDescriptions(ticker):
    try:
        if ticker is None:
            ticker = "TPG_AU"
        query = "SELECT content FROM companyDetails WHERE ticker = :ticker;"
        params = {"ticker": ticker[0:-3]}
        texts = get_cursor(query,params)
        texts = texts[0]
        texts = re.sub(r'^[\s\S]*?(?=(\*\*|##))', '', texts) if '**' in texts or '##' in texts else "No information available"

        lines = texts.split('\n')
        formatted_lines = []
        for i in range(len(lines)):
            formatted_lines.append(dcc.Markdown(lines[i]))
        return formatted_lines
    except:
        alert = dmc.Alert(
            "Sorry! This data is not available.",
            id="alert-segment",
            title="Error!",
            color="red",
            withCloseButton=True,
            hide=False
        ),
        return alert
