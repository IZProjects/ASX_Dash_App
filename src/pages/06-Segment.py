import dash
from dash import html, callback, Output, Input, dash_table
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from src.mysql_connect_funcs import get_cursor, get_df_query

dash.register_page(__name__, name='Segment')

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
                 dbc.Row(html.P(id="price_change"), id='price_change_row')],
                width=2, style={'text-align': 'right'}),
    ], style={'margin-bottom': '10px'}),
    dbc.Row(html.Hr()),

    dbc.Row(id='SegmentDescriptionRow', style={'margin-bottom': '20px'}),
        dbc.Row(id='SegmentResultsTitle', style={'margin-top': '20px', 'margin-bottom': '5px'}),
    dbc.Row(id='SegmentResultsRow'),
]),color="primary",delay_hide=10,delay_show=15,spinner_style={"position":"absolute", "top":"20%"})

@callback(
    Output(component_id='SegmentDescriptionRow', component_property='children'),
    Input("ticker", "data"),
)
def get_segmentDescriptions(ticker):
    try:
        if ticker is None:
            ticker = "TPG_AU"
        #conn = sqlite3.connect('databases/AI_content.db')
        #cursor = conn.cursor()
        #query = "SELECT content FROM SegmentDescription WHERE ticker = " + ticker[0:-3]
        query = "SELECT content FROM SegmentDescription WHERE ticker = :ticker;"
        params = {"ticker": ticker[0:-3]}
        #cursor.execute(query)
        #texts = cursor.fetchone()
        texts = get_cursor(query,params)
        texts = texts[0]
        #conn.close()

        texts = texts.replace(':', ':\n')
        texts = texts.replace('*', '')
        lines = texts.split('\n')
        formatted_lines = []
        for i in range(len(lines)):
            if ':' in lines[i]:
                formatted_lines.append(dmc.Text(lines[i], fw=500, c="black", style={'margin-top': '10px'}))
            elif '#' in lines[i]:
                lines[i] = lines[i].replace('#', '')
                formatted_lines.append(dmc.Text(lines[i], fw=500, c="black", style={'margin-top': '10px'}))
            elif i == 0:
                formatted_lines.append(dmc.Text(lines[i]))
            elif lines[i].strip() == '':
                formatted_lines.append(dmc.Text(lines[i]))
            else:
                lines[i] = lines[i][0:].lstrip('- ')
                formatted_lines.append(dmc.List(dmc.ListItem(lines[i])))

        return formatted_lines
    except:
        return html.H5("No segement information avaliable at the moment", style={'margin-top': '40px'})


@callback(
    [Output(component_id='SegmentResultsRow', component_property='children'),
     Output(component_id='SegmentResultsTitle', component_property='children')],
    Input("ticker", "data"),
)
def get_segmentResults(ticker):
    try:
        if ticker is None:
            ticker = "TPG_AU"
        #conn = sqlite3.connect('databases/AI_content.db')
        query = "SELECT * FROM `" + ticker[0:-3] + "_segmentResults`"
        #df = pd.read_sql_query(query, conn)
        df = get_df_query(query)
        df.columns = df.columns.str.title()
        df['Year'] = df['Year'].astype(int)
        df = df.sort_values(by='Year', ascending=False)
        underlineIndex = df.index[df['Year'] != df['Year'].shift(-1)].tolist()

        body_style = [
                         {
                             'if': {'row_index': underlineIndex},
                             'borderBottom': '1px solid black',
                         }
                     ]

        table = dash_table.DataTable(
            id='table',
            columns=[{"name": i, "id": i} for i in df.columns],
            data=df.to_dict('records'),
            style_header={'backgroundColor': 'rgb(30, 30, 30)',
                          'color': 'white',
                          'fontWeight': 'bold',
                          'textAlign': 'center'},
            style_table = {'overflowX': 'auto', 'height': '800px', 'overflowY': 'auto','minWidth': '100%','z-index':'0'},
            style_cell={#'height': 'auto',
                        'minWidth': '120px', 'width': '120px', 'maxWidth': '600px',
                        #'whiteSpace': 'normal',
                        'textAlign': 'center'},
            style_data_conditional=body_style,
            editable=False,
            )
        return table, dmc.Text("Segment Results", fw=500, size='xl', c='black')
    except:
        return html.Div(" "), html.Div(" ")