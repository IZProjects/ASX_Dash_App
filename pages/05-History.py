import dash
from dash import dcc, html, callback, Output, Input
import dash_bootstrap_components as dbc
import pandas as pd
import dash_mantine_components as dmc
from mysql_connect_funcs import get_df_query

dash.register_page(__name__, name='History')

button = dmc.SegmentedControl(
    id='controls',
    color="indigo",
    fullWidth=True,
    data = [{"value": "Short", "label": "Summary"},
            {"value": "Long", "label": "Detailed"}]
)

layout = dbc.Spinner(dbc.Container([
    dcc.Store(id="long_history", storage_type='session', data={}),
    dcc.Store(id="short_history", storage_type='session', data={}),
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
    dbc.Row(html.Hr()),
    dbc.Row([dbc.Col(html.Div(''), width = 9), dbc.Col(button, width=3)], style={'margin-bottom': '20px'}),
    dbc.Row(id='timeline', style={'margin-top': '10px', 'margin-bottom': '20px'}),
]),color="primary",delay_hide=10,delay_show=15,spinner_style={"position":"absolute", "top":"20%"})

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
        return html.H5("No history avaliable at the moment", style={'margin-top': '40px'})
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
