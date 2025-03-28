import dash
from dash import dcc, html, callback, Output, Input
import pandas as pd
import dash_mantine_components as dmc
from mysql_connect_funcs import get_df_query

dash.register_page(__name__, name='History')

button = dmc.SegmentedControl(
    id='controls',
    color="indigo",
    fullWidth=True,
    size='md',
    data = [{"value": "Short", "label": "Summary"},
            {"value": "Long", "label": "Detailed"}]
)


layout = dmc.Box([
    dcc.Store(id="long_history", storage_type='session', data={}),
    dcc.Store(id="short_history", storage_type='session', data={}),

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

    dmc.Container(html.Hr(), fluid=True),

    dmc.Flex(children=[button], justify='flex-end', style={'margin-bottom': '20px', 'margin-right': '20px'}),

    dmc.Container(id='timeline', fluid=True, style={'margin-top': '10px', 'margin-bottom': '20px'}),

])

@callback(
    [Output(component_id='long_history', component_property='data'),
     Output(component_id='short_history', component_property='data')],
    Input("ticker", "data"),
)
def get_tbl(ticker):
    try:
        if ticker is None:
            ticker = "TPG_AU"

        query = "SELECT * FROM `History_long` WHERE ticker = '" + ticker[0:-3] + "'"
        df_longHistory = get_df_query(query)
        dict_longHistory = df_longHistory.to_dict()
        query = "SELECT * FROM `History_short` WHERE ticker = '" + ticker[0:-3] + "'"
        df_shortHistory = get_df_query(query)
        dict_shortHistory = df_shortHistory.to_dict()
        return dict_longHistory, dict_shortHistory

    except:
        return pd.DataFrame(), pd.DataFrame()


@callback(
    Output("timeline", "children"),
    [Input("long_history", "data"),
     Input("short_history", "data"),
     Input("controls", "value"),]
)
def get_timeline(long_history, short_history, controls):
    if controls == 'Long':
        df = pd.DataFrame.from_dict(long_history)
    else:
        df = pd.DataFrame.from_dict(short_history)
    if df.empty:
        alert = dmc.Alert(
            "Sorry! This data is not available.",
            id="alert-timeline",
            title="Error!",
            color="red",
            withCloseButton=True,
            hide=False
        ),
        return alert
    else:
        df['year'] = df['year'].astype(int)
        df = df.sort_values(by='year', ascending=False)
        years = df['year'].to_list()
        texts = df['content'].to_list()
        formatted_text = []
        for i in range(len(texts)):
            formatted_lines = []
            formatted_lines.append(dmc.Text(years[i], size='xl', fw=700, td='underline'))
            texts[i] = texts[i].replace(':', ':\n')
            texts[i] = texts[i].replace('*', '')
            lines = texts[i].split('\n')
            for i in range(len(lines)):
                if ':' in lines[i]:
                    formatted_lines.append(dmc.Text(lines[i], fw=500, style={'margin-top': '10px'}))
                elif '#' in lines[i]:
                    lines[i] = lines[i].replace('#', '')
                    formatted_lines.append(dmc.Text(lines[i], fw=700, style={'margin-top': '10px'}))
                elif i == 0 and controls == 'Long':
                    formatted_lines.append(dmc.Text(lines[i]))
                elif lines[i].strip() == '':
                    formatted_lines.append(dmc.Text(lines[i]))
                else:
                    lines[i] = lines[i][0:].lstrip('- ')
                    formatted_lines.append(dmc.List(dmc.ListItem(lines[i])))


            formatted_text.append(formatted_lines)
        contentForTimeline = []
        for i in range(len(years)):
            contentForTimeline.append(dmc.TimelineItem(children=formatted_text[i]))

        timeline = dmc.Timeline(contentForTimeline, active=len(years))
        return timeline
