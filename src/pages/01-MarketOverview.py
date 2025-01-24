import dash
from dash import dcc, html, callback, Output, Input
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
from src.mysql_connect_funcs import get_df_tblName, get_df_query

TABLE_SIZE = 16

dash.register_page(__name__, path='/', name='Market Overview') # '/' is home page


df_asx200 = get_df_tblName("AXJO")
df_spy = get_df_tblName("SPY")
df_AUDUSD = get_df_tblName("AUDUSD")
df_losers = get_df_tblName("losers")
df_winners = get_df_tblName("winners")
df_active = get_df_tblName("active")
au_sectors = get_df_tblName("AU_Sectors")

query = r"SELECT * FROM announcements_today LIMIT 100"
df_announcements = get_df_query(query)

df_insider = get_df_tblName("insiderTrades_today")
df_insider = df_insider.dropna(how='all')


def create_link_announcements(item):
    return dcc.Link('Link', href=item)

df_announcements['Links'] = df_announcements['Links'].apply(create_link_announcements)

def create_linkGBA(item):
    return dcc.Link(item, href='/02-companyoverview?data='+item+'_AU', id=f'link-{item}')
def gen_chart_text(df):
    close = round(df['Close'].iloc[-1],2)
    open = round(df['Open'].iloc[0],2)
    pct = round(((close-open)/open)*100,2)

    if pct>0:
        colour = 'green'
    else:
        colour = 'red'
    return close, pct, colour


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

asx200_close, asx200_pct, asx200_colour = gen_chart_text(df_asx200)
fig_asx200 = gen_chart(df_asx200, asx200_colour)

spy_close, spy_pct, spy_colour = gen_chart_text(df_spy)
fig_spy = gen_chart(df_spy, spy_colour)

AUDUSD_close, AUDUSD_pct, AUDUSD_colour = gen_chart_text(df_AUDUSD)
fig_AUDUSD = gen_chart(df_AUDUSD, AUDUSD_colour)


cardGLA = dbc.Card(
    [
        dbc.CardHeader(
            dbc.Tabs(
                [
                        dbc.Tab(label="Most Gains", tab_id="gains"),
                        dbc.Tab(label="Most Losses", tab_id="losses"),
                        dbc.Tab(label="Most Active", tab_id="active"),
                    ],
                    id="tabs",
                    active_tab="gains",
            )
        ),
        dbc.CardBody(id="GLA_content"),
    ]
)

cardSector = dbc.Card(dbc.CardBody(dbc.Table.from_dataframe(au_sectors, bordered=True, hover=True)))


def get_total_page(page_size, total_data):
  data_div_page_size = total_data // page_size
  data_mod_page_size = total_data % page_size
  total_page = data_div_page_size if data_mod_page_size == 0 else (data_div_page_size+1)
  return total_page

# Layout
layout = dbc.Spinner(dbc.Container([
    dbc.Row([
        dbc.Col(dbc.Card([dbc.CardHeader(dbc.Row([dbc.Col('ASX 200 (AU)', width=6, style={'font-weight': 'bold'}),
                                                  dbc.Col('$'+str(asx200_close), width=3),
                                                  dbc.Col(str(asx200_pct)+'%', width=3, style = {'color': asx200_colour}),
                                                  ])
                                         ),
                          dbc.CardBody(dcc.Graph(figure=fig_asx200, config={'staticPlot': True}))]),
                width=4),


        dbc.Col(dbc.Card([dbc.CardHeader(dbc.Row([dbc.Col('S&P 500 (US)', width=6, style={'font-weight': 'bold'}),
                                                  dbc.Col('$' + str(spy_close), width=3),
                                                  dbc.Col(str(spy_pct) + '%', width=3,
                                                          style={'color': spy_colour}),
                                                  ])
                                         ),
                          dbc.CardBody(dcc.Graph(figure=fig_spy, config={'staticPlot': True}))]),
                width=4),

        dbc.Col(dbc.Card([dbc.CardHeader(dbc.Row([dbc.Col('AUD/USD', width=6, style={'font-weight': 'bold'}),
                                                  dbc.Col('$' + str(AUDUSD_close), width=3),
                                                  dbc.Col(str(AUDUSD_pct) + '%', width=3,
                                                          style={'color': AUDUSD_colour}),
                                                  ])
                                         ),
                          dbc.CardBody(dcc.Graph(figure=fig_AUDUSD, config={'staticPlot': True}))]),
                width=4),
             ], style={'margin-bottom':'40px'}),

    dbc.Row(html.H4("Today's Announcements", style={'font-weight': 'bold'})),
    dbc.Row(html.Small("*Ctrl-Click to open link in new tab")),
    dbc.Row([
        dbc.Col([
            dbc.Row([
                dbc.Table(id='annoucementsTBL', style={'margin-bottom':'-10px'}),
                dbc.Pagination(id="pagination", max_value=get_total_page(TABLE_SIZE, len(df_announcements))),
                ],style={'margin-right':'20px'})
        ], width=8),

        dbc.Col([
            dbc.Row([cardGLA], style={'margin-bottom':'20px'}),
            dbc.Row([cardSector])
        ],width=4),
    ], style={'margin-bottom':'40px'}),

    dbc.Row(html.H4("Insider Activity", style={'font-weight': 'bold'})),
    dbc.Row(html.Small("*Ctrl-Click to open link in new tab")),
    dbc.Row([
        dbc.Table(id='insiderActivityTBL', style={'margin-bottom': '-10px'}),
        dbc.Pagination(id="pagination2", max_value=get_total_page(TABLE_SIZE, len(df_insider))),
    ])
]),color="primary",delay_hide=10,delay_show=15,spinner_style={"position":"absolute", "top":"20%"})

@callback(Output("GLA_content", "children"),
          Input("tabs", "active_tab")
          )
def create_GLA_content(at):
    if at == "gains":
        df = df_winners
    elif at == "losses":
        df = df_losers
    else:
        df = df_active
    new_df = df.copy()
    new_df['Ticker'] = df['Ticker'].apply(create_linkGBA)
    table = dbc.Table.from_dataframe(new_df, bordered=True, hover=True)
    return table


@callback(
    Output('annoucementsTBL', 'children'),
    Input('pagination', 'active_page'),
)
def create_announcements_TBL(page):
    # convert active_page data to integer and set default value to 1
    int_page = 1 if not page else int(page)

    # define filter index range based on active page
    filter_index_1 = (int_page - 1) * TABLE_SIZE
    filter_index_2 = (int_page) * TABLE_SIZE

    # get data by filter range based on active page number
    fitlered_df = df_announcements[filter_index_1:filter_index_2]
    fitlered_df['Document Name'] = fitlered_df['Document Name'].str.upper()
    fitlered_df['Type'] = fitlered_df['Type'].str.upper()
    fitlered_df = fitlered_df.dropna(how='all')
    # load data to dash bootstrap table component
    table = dbc.Table.from_dataframe(fitlered_df, bordered=True, hover=True, striped=True)

    return table

@callback(
    Output('insiderActivityTBL', 'children'),
    Input('pagination2', 'active_page'),
)
def create_insiderActivity_TBL(page):
    # convert active_page data to integer and set default value to 1
    int_page = 1 if not page else int(page)

    # define filter index range based on active page
    filter_index_1 = (int_page - 1) * TABLE_SIZE
    filter_index_2 = (int_page) * TABLE_SIZE

    # get data by filter range based on active page number
    fitlered_df = df_insider[filter_index_1:filter_index_2]
    fitlered_df['Code'] = fitlered_df['Code'].apply(create_linkGBA)
    fitlered_df = fitlered_df.dropna(how='all')
    # load data to dash bootstrap table component
    table = dbc.Table.from_dataframe(fitlered_df, bordered=True, hover=True, striped=True)

    return table