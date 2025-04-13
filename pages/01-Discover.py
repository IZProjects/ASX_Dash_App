import dash
from dash import dcc, callback, Output, Input, dash_table, html
import pandas as pd
import plotly.graph_objects as go
import dash_mantine_components as dmc
from mysql_connect_funcs import get_df_tblName


dash.register_page(__name__, path='/', name='Discover') # '/' is home page

def gen_chart(df, colour):
    fig = go.Figure()
    fig.add_trace(go.Scatter(y=df['Close'], mode='lines', line=dict(color=colour)))
    fig.update_layout(
        showlegend=False,
        plot_bgcolor='white',
        xaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
        yaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
        margin=dict(l=0, r=0, t=0, b=0),
        height=50
    )
    return fig

def gen_chart_text(df):
    close = round(df['Close'].iloc[-1],2)
    open = round(df['Open'].iloc[0],2)
    pct = round(((close-open)/open)*100,2)

    if pct>0:
        colour = 'green'
    else:
        colour = 'red'
    return close, pct, colour

df_ann = get_df_tblName("announcements_today_wPrice")
df_ann['Date'] = pd.to_datetime(df_ann['Date'], format='%d %b %Y %I:%M%p')
df_ann = df_ann.sort_values('Date', ascending=False).reset_index(drop=True)
df_ann['Date'] = df_ann['Date'].dt.strftime('%d/%m/%Y')

"""table_ann = dash_table.DataTable(
    id='table_ann',
    columns=[{'id': x, 'name': x, 'type': 'text', 'presentation': 'markdown'} for x in df_ann.columns],
    data=df_ann.to_dict('records'),
    style_header={'backgroundColor': 'rgb(30, 30, 30)',
                  'color': 'white',
                  'fontWeight': 'bold',
                  'textAlign': 'center'},
    style_cell={'height': 'auto',
                'whiteSpace': 'normal'},
    sort_action='native',
    page_size=10,
    markdown_options={"link_target": "_self"},
    css=[{'selector': 'p', 'rule': 'margin: 0; text-align: center; padding-left: 5px; padding-right: 5px;'},
         {'selector': 'td[data-dash-column="Document Name"] p', 'rule': 'text-align: left;'},
         {'selector': 'td[data-dash-column="Type"] p', 'rule': 'text-align: left;'}],
    style_data_conditional=[
        {
            'if': {
                'filter_query': '{Price Change (%)} > 0',
                'column_id': 'Price Change (%)'
            },
            'color': 'green',
            'fontWeight': 'bold',
        },
        {
            'if': {
                'filter_query': '{Price Change (%)} < 0',
                'column_id': 'Price Change (%)'
            },
            'color': 'red',
            'fontWeight': 'bold'
        },
        {
            'if': {
                'filter_query': '{Price Change (%)} = 0',
                'column_id': 'Price Change (%)'
            },
            'fontWeight': 'bold',
        },
    ]
)"""


df_IT = get_df_tblName("insiderTrades_today")
df_IT['Date'] = pd.to_datetime(df_IT['Date'], format='%d %b %Y %I:%M%p')
df_IT = df_IT.sort_values('Date', ascending=False).reset_index(drop=True)
df_IT['Date'] = df_IT['Date'].dt.strftime('%d/%m/%Y')

table_IT = dash_table.DataTable(
    id='table_IT',
    columns=[{'id': x, 'name': x, 'type': 'text', 'presentation': 'markdown'} for x in df_IT.columns],
    data=df_IT.to_dict('records'),
    style_header={'backgroundColor': 'rgb(30, 30, 30)',
                  'color': 'white',
                  'fontWeight': 'bold',
                  'textAlign': 'center'},
    style_cell={'height': 'auto',
                'whiteSpace': 'normal'},
    style_table = {'overflowX': 'auto'},
    sort_action='native',
    page_size= 10,
    markdown_options={"link_target": "_self"},
    css=[{'selector': 'p', 'rule': 'margin: 0; text-align: center; padding-left: 5px; padding-right: 5px;'},
         {'selector': 'td[data-dash-column="Director"] p', 'rule': 'text-align: left;'},
         {'selector': 'td[data-dash-column="Notes"] p', 'rule': 'text-align: left;'},
         {'selector': 'td[data-dash-column="Value"] p', 'rule': 'text-align: left;'},
         ],

    style_data_conditional=[
        {
            'if': {
                'filter_query': '{Type} = "Bought"',
                'column_id': 'Type'
            },
            'color': 'green',
            'fontWeight': 'bold'
        },
        {
            'if': {
                'filter_query': '{Type} = "Sold"',
                'column_id': 'Type'
            },
            'color': 'red',
            'fontWeight': 'bold'

        },
        {
            'if': {
                'filter_query': '{Type} = "Bought"',
                'column_id': 'Value'
            },
            'color': 'green',
            'fontWeight': 'bold'
        },
        {
            'if': {
                'filter_query': '{Type} = "Sold"',
                'column_id': 'Value'
            },
            'color': 'red',
            'fontWeight': 'bold'
        },
    ]
)


GLA_controls = dmc.SegmentedControl(
    id='GLA_controls',
    color="indigo",
    fullWidth=False,
    size='sm',
    data = [{"value": "gains", "label": "Most Gains"},
            {"value": "losses", "label": "Most Losses"},
            {"value": "active", "label": "Most Active"},],
    value="gains"
)

df_turnaround = get_df_tblName("discovery_turnaround")
table_turnaround = dash_table.DataTable(
    id='table_turnaround',
    columns=[{'id': x, 'name': x, 'type': 'text', 'presentation': 'markdown'} for x in df_turnaround.columns],
    data=df_turnaround.to_dict('records'),
    style_header={'backgroundColor': 'rgb(30, 30, 30)',
                  'color': 'white',
                  'fontWeight': 'bold',
                  'textAlign': 'center'},
    style_cell={'height': 'auto',
                'whiteSpace': 'normal'},
    style_table={'overflowX': 'auto'},
    sort_action='native',
    page_size= 10,
    markdown_options={"link_target": "_self"},
    css=[{'selector': 'p', 'rule': 'margin: 0; text-align: center; padding-left: 5px; padding-right: 5px;'},
         {'selector': 'td[data-dash-column="Story"] p', 'rule': 'text-align: left;'},
         ],
)

df_growthStory = get_df_tblName("discovery_growthStory")
table_growthStory = dash_table.DataTable(
    id='table_growthStory',
    columns=[{'id': x, 'name': x, 'type': 'text', 'presentation': 'markdown'} for x in df_growthStory.columns],
    data=df_growthStory.to_dict('records'),
    style_header={'backgroundColor': 'rgb(30, 30, 30)',
                  'color': 'white',
                  'fontWeight': 'bold',
                  'textAlign': 'center'},
    style_cell={'height': 'auto',
                'whiteSpace': 'normal'},
    style_table={'overflowX': 'auto'},
    sort_action='native',
    page_size= 10,
    markdown_options={"link_target": "_self"},
    css=[{'selector': 'p', 'rule': 'margin: 0; text-align: center; padding-left: 5px; padding-right: 5px;'},
         {'selector': 'td[data-dash-column="Story"] p', 'rule': 'text-align: left;'},
         ],
)

layout = dmc.Box([
    dcc.Store(id="gain_store", storage_type='session', data=get_df_tblName("winners").to_dict()),
    dcc.Store(id="loss_store", storage_type='session', data=get_df_tblName("losers").to_dict()),
    dcc.Store(id="active_store", storage_type='session', data=get_df_tblName("active").to_dict()),
    dcc.Store(id="gain100M_store", storage_type='session', data=get_df_tblName("winners100M").to_dict()),
    dcc.Store(id="loss100M_store", storage_type='session', data=get_df_tblName("losers100M").to_dict()),
    dcc.Store(id="active100M_store", storage_type='session', data=get_df_tblName("active100M").to_dict()),
    dcc.Store(id="discovery_deep_value", storage_type='session', data=get_df_tblName("discovery_deep_value").to_dict()),
    dcc.Store(id="discovery_deep_value_100M", storage_type='session',
              data=get_df_tblName("discovery_deep_value_100M").to_dict()),
    dcc.Store(id="discovery_ROE", storage_type='session', data=get_df_tblName("discovery_ROE").to_dict()),
    dcc.Store(id="discovery_ROE_100M", storage_type='session', data=get_df_tblName("discovery_ROE_100M").to_dict()),
    dcc.Store(id="discovery_growth", storage_type='session', data=get_df_tblName("discovery_growth").to_dict()),
    dcc.Store(id="discovery_growth_100M", storage_type='session',
              data=get_df_tblName("discovery_growth_100M").to_dict()),

    dmc.Container(dmc.Text("Today's Movers", fw=700, size='xl'), style={'margin-bottom': '5px'}, fluid=True),
    dmc.Container(dmc.Group([GLA_controls, dmc.Checkbox(id='GLA_check', label="100M+ Only", size="md")],
                      gap='md'), style={'margin-bottom': '10px'}, fluid=True),
    dmc.Container(id='GLA_container', style={'margin-bottom': '20px'}, fluid=True),

    #dmc.Container(dmc.Text("Today's Announcements", fw=700, size='xl'), style={'margin-bottom': '5px'}, fluid=True),
    #dmc.Container(children=table_ann, style={'margin-bottom': '20px'}, fluid=True),

    dmc.Container(dmc.Text("Insider Trades", fw=700, size='xl'), style={'margin-bottom': '5px'}, fluid=True),
    dmc.Container(children=table_IT, style={'margin-bottom': '20px'}, fluid=True),

    dmc.Container(dmc.Text("Deep Value Candidates", fw=700, size='xl'), style={'margin-bottom': '5px'}, fluid=True),
    dmc.Container(dmc.Checkbox(id='DV_check', label="100M+ Only", size="md"), style={'margin-bottom': '10px'}, fluid=True),
    dmc.Container(id='DV_container', style={'margin-bottom': '20px'}, fluid=True),

    dmc.Container(dmc.Text("High ROE Candidates", fw=700, size='xl'), style={'margin-bottom': '5px'}, fluid=True),
    dmc.Container(dmc.Checkbox(id='ROE_check', label="100M+ Only", size="md"), style={'margin-bottom': '10px'}, fluid=True),
    dmc.Container(id='ROE_container', style={'margin-bottom': '20px'}, fluid=True),

    dmc.Container(dmc.Text("High Growth Candidates", fw=700, size='xl'), style={'margin-bottom': '5px'}, fluid=True),
    dmc.Container(dmc.Checkbox(id='growth_check', label="100M+ Only", size="md"), style={'margin-bottom': '10px'}, fluid=True),
    dmc.Container(id='Growth_container', style={'margin-bottom': '20px'}, fluid=True),

    dmc.Container(dmc.Text("Turnaround Stories", fw=700, size='xl'), style={'margin-bottom': '5px'}, fluid=True),
    dmc.Container(children=table_turnaround, style={'margin-bottom': '20px'}, fluid=True),

    dmc.Container(dmc.Text("Growth Stories", fw=700, size='xl'), style={'margin-bottom': '5px'}, fluid=True),
    dmc.Container(children=table_growthStory, style={'margin-bottom': '20px'}, fluid=True),

    dmc.Container(html.Hr(), fluid=True, style={'margin-top': '50px', 'margin-bottom': '20px'}),
    dmc.Container(dmc.Text("""All information and data presented on this website are for informational purposes only. 
                                        We are not financial advisers and none of the content on our website should be interpreted as financial advice. 
                                        Nothing on our website is intended to imply a recommendation or opinion about a financial product. 
                                        Before you make an investment decision based on any of the information contained on our website, 
                                        please consult a qualified financial adviser or stockbroker. 
                                        We do not guarentee the accuracy or completeness of any of the information provided.""", size='xs', c='gray'), fluid=True),
])

@callback(
    [#Output("table_ann", "style_data"),
     Output("table_IT", "style_data"),
     Output("table_turnaround", "style_data"),
     Output("table_growthStory", "style_data"),],
     Input("mantine-provider", "forceColorScheme")
)
def table_themes(theme):
    if theme == 'light':
        theme_style = {
            'backgroundColor': 'rgb(255, 255, 255)',
            'color': 'black'
        }
    else:
        theme_style = {
            'backgroundColor': 'rgb(50, 50, 50)',
            'color': 'white'
        }

    return theme_style, theme_style, theme_style, #theme_style


@callback(
    Output("GLA_container", "children"),
    [Input("gain_store", "data"),
     Input("loss_store", "data"),
     Input("active_store", "data"),
     Input("gain100M_store", "data"),
     Input("loss100M_store", "data"),
     Input("active100M_store", "data"),
     Input("GLA_controls", "value"),
     Input("GLA_check", "checked"),
     Input("mantine-provider", "forceColorScheme")]
)
def get_timeline(gain, loss, active, gain100M, loss100M, active100M, controls, GLAchecked, theme):
    if GLAchecked == True:
        if controls == "gains":
            df = pd.DataFrame.from_dict(gain100M)
        elif controls == "losses":
            df = pd.DataFrame.from_dict(loss100M)
        else:
            df = pd.DataFrame.from_dict(active100M)
    else:
        if controls == "gains":
            df = pd.DataFrame.from_dict(gain)
        elif controls == "losses":
            df = pd.DataFrame.from_dict(loss)
        else:
            df = pd.DataFrame.from_dict(active)

    if theme == 'light':
        theme_style = {
            'backgroundColor': 'rgb(255, 255, 255)',
            'color': 'black'
        }
    else:
        theme_style = {
            'backgroundColor': 'rgb(50, 50, 50)',
            'color': 'white'
        }

    table = dash_table.DataTable(
        id='table',
        columns=[{'id': x, 'name': x, 'type': 'text', 'presentation': 'markdown'} for x in df.columns],
        data=df.to_dict('records'),
        style_header={'backgroundColor': 'rgb(30, 30, 30)',
                      'color': 'white',
                      'fontWeight': 'bold',
                      'textAlign': 'center'},
        style_cell={'height': 'auto',
                    'whiteSpace': 'normal'},
        sort_action='native',
        page_size=10,
        style_data=theme_style,
        style_table = {'overflowX': 'auto'},
        markdown_options={"link_target": "_self"},
        css=[{'selector': 'p', 'rule': 'margin: 0; text-align: center; padding-left: 5px; padding-right: 5px;'}],
        style_data_conditional=[
            {
                'if': {
                    'filter_query': '{Change} > 0%',
                    'column_id': 'Change'
                },
                'color': 'green',
                'fontWeight': 'bold',
            },
            {
                'if': {
                    'filter_query': '{Change} < 0%',
                    'column_id': 'Change'
                },
                'color': 'red',
                'fontWeight': 'bold'
            },
            {
                'if': {
                    'filter_query': '{Change} = 0%',
                    'column_id': 'Change'
                },
                'fontWeight': 'bold'
            },
        ]
    )

    return table



@callback(
    Output("DV_container", "children"),
    [Input("discovery_deep_value", "data"),
     Input("discovery_deep_value_100M", "data"),
     Input("DV_check", "checked"),
     Input("mantine-provider", "forceColorScheme")]
)
def get_DV(DV, DV100, DVchecked, theme):

    if DVchecked == True:
        dfDV = pd.DataFrame.from_dict(DV100)
    else:
        dfDV = pd.DataFrame.from_dict(DV)

    if theme == 'light':
        theme_style = {
            'backgroundColor': 'rgb(255, 255, 255)',
            'color': 'black'
        }
    else:
        theme_style = {
            'backgroundColor': 'rgb(50, 50, 50)',
            'color': 'white'
        }

    tableDV = dash_table.DataTable(
        id='table',
        columns=[{'id': x, 'name': x, 'type': 'text', 'presentation': 'markdown'} for x in dfDV.columns],
        data=dfDV.to_dict('records'),
        style_header={'backgroundColor': 'rgb(30, 30, 30)',
                      'color': 'white',
                      'fontWeight': 'bold',
                      'textAlign': 'center'},
        style_cell={'height': 'auto',
                    'whiteSpace': 'normal'},
        style_table={'overflowX': 'auto'},
        sort_action='native',
        style_data=theme_style,
        markdown_options={"link_target": "_self"},
        css=[{'selector': 'p', 'rule': 'margin: 0; text-align: center; padding-left: 5px; padding-right: 5px;'}],
    )

    return tableDV

@callback(
    Output("ROE_container", "children"),
    [Input("discovery_ROE", "data"),
     Input("discovery_ROE_100M", "data"),
     Input("ROE_check", "checked"),
     Input("mantine-provider", "forceColorScheme")]
)
def get_ROE(ROE, ROE100, ROEchecked, theme):

    if ROEchecked == True:
        dfROE = pd.DataFrame.from_dict(ROE100)
    else:
        dfROE = pd.DataFrame.from_dict(ROE)

    if theme == 'light':
        theme_style = {
            'backgroundColor': 'rgb(255, 255, 255)',
            'color': 'black'
        }
    else:
        theme_style = {
            'backgroundColor': 'rgb(50, 50, 50)',
            'color': 'white'
        }

    tableROE = dash_table.DataTable(
        id='table',
        columns=[{'id': x, 'name': x, 'type': 'text', 'presentation': 'markdown'} for x in dfROE.columns],
        data=dfROE.to_dict('records'),
        style_header={'backgroundColor': 'rgb(30, 30, 30)',
                      'color': 'white',
                      'fontWeight': 'bold',
                      'textAlign': 'center'},
        style_cell={'height': 'auto',
                    'whiteSpace': 'normal'},
        style_table={'overflowX': 'auto'},
        sort_action='native',
        style_data=theme_style,
        markdown_options={"link_target": "_self"},
        css=[{'selector': 'p', 'rule': 'margin: 0; text-align: center; padding-left: 5px; padding-right: 5px;'}],
    )

    return tableROE

@callback(
    Output("Growth_container", "children"),
    [Input("discovery_growth", "data"),
     Input("discovery_growth_100M", "data"),
     Input("growth_check", "checked"),
     Input("mantine-provider", "forceColorScheme")]
)
def get_growth(growth, growth100, growthchecked, theme):

    if growthchecked == True:
        dfgrowth = pd.DataFrame.from_dict(growth100)
    else:
        dfgrowth = pd.DataFrame.from_dict(growth)

    if theme == 'light':
        theme_style = {
            'backgroundColor': 'rgb(255, 255, 255)',
            'color': 'black'
        }
    else:
        theme_style = {
            'backgroundColor': 'rgb(50, 50, 50)',
            'color': 'white'
        }

    tablegrowth = dash_table.DataTable(
        id='table',
        columns=[{'id': x, 'name': x, 'type': 'text', 'presentation': 'markdown'} for x in dfgrowth.columns],
        data=dfgrowth.to_dict('records'),
        style_header={'backgroundColor': 'rgb(30, 30, 30)',
                      'color': 'white',
                      'fontWeight': 'bold',
                      'textAlign': 'center'},
        style_cell={'height': 'auto',
                    'whiteSpace': 'normal'},
        sort_action='native',
        style_table={'overflowX': 'auto'},
        style_data=theme_style,
        markdown_options={"link_target": "_self"},
        css=[{'selector': 'p', 'rule': 'margin: 0; text-align: center; padding-left: 5px; padding-right: 5px;'}],
    )

    return tablegrowth