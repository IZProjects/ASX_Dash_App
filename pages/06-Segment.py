import dash
from dash import html, callback, Output, Input, dash_table
import dash_mantine_components as dmc
from mysql_connect_funcs import get_cursor, get_df_query

dash.register_page(__name__, name='Segment')

layout = dmc.Box([
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

    dmc.Container(id='SegmentDescriptionRow', fluid=True, style={'margin-bottom': '20px'}),
    dmc.Container(id='SegmentResultsTitle', fluid=True, style={'margin-top': '20px', 'margin-bottom': '5px'}),
    dmc.Container(id='SegmentResultsRow', fluid=True),

])

@callback(
    Output(component_id='SegmentDescriptionRow', component_property='children'),
    Input("ticker", "data"),
)
def get_segmentDescriptions(ticker):
    try:
        if ticker is None:
            ticker = "TPG_AU"
        query = "SELECT content FROM SegmentDescription WHERE ticker = :ticker;"
        params = {"ticker": ticker[0:-3]}
        texts = get_cursor(query,params)
        texts = texts[0]


        texts = texts.replace(':', ':\n')
        texts = texts.replace('*', '')
        lines = texts.split('\n')
        formatted_lines = []
        for i in range(len(lines)):
            if ':' in lines[i]:
                formatted_lines.append(dmc.Title(lines[i], order=5, style={'margin-top': '10px'}))
            elif '#' in lines[i]:
                lines[i] = lines[i].replace('#', '')
                formatted_lines.append(dmc.Title(lines[i], order=5, style={'margin-top': '10px'}))
            elif i == 0:
                formatted_lines.append(dmc.Text(lines[i]))
            elif lines[i].strip() == '':
                formatted_lines.append(dmc.Text(lines[i]))
            else:
                lines[i] = lines[i][0:].lstrip('- ')
                formatted_lines.append(dmc.List(dmc.ListItem(lines[i])))

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


@callback(
    [Output(component_id='SegmentResultsRow', component_property='children'),
     Output(component_id='SegmentResultsTitle', component_property='children')],
    [Input("ticker", "data"),
     Input("mantine-provider", "forceColorScheme")],
)
def get_segmentResults(ticker,theme):
    try:
        if ticker is None:
            ticker = "TPG_AU"
        query = "SELECT * FROM `" + ticker[0:-3] + "_segmentResults`"
        df = get_df_query(query)
        df.columns = df.columns.str.title()
        df['Year'] = df['Year'].astype(int)
        df = df.sort_values(by='Year', ascending=False)
        underlineIndex = df.index[df['Year'] != df['Year'].shift(-1)].tolist()

        body_style = [
                         {
                             'if': {'row_index': underlineIndex},
                             'borderBottom': '1px solid',
                         }
                     ]

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
            columns=[{"name": i, "id": i} for i in df.columns],
            data=df.to_dict('records'),
            style_header={'backgroundColor': 'rgb(30, 30, 30)',
                          'color': 'white',
                          'fontWeight': 'bold',
                          'textAlign': 'center'},
            style_table = {'overflowX': 'auto', 'height': '800px', 'overflowY': 'auto','minWidth': '100%','z-index':'0'},
            style_cell={'minWidth': '120px', 'width': '120px', 'maxWidth': '600px',
                        'textAlign': 'center'},
            style_data_conditional=body_style,
            style_data=theme_style,
            editable=False,
            )
        return table, dmc.Title("Segment Results", order=4)
    except:
        return html.Div(" "), html.Div(" ")