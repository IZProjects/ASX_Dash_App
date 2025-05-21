import dash
from dash import dcc, Input, Output, callback, State, page_container, clientside_callback, ClientsideFunction, html
from dash.exceptions import PreventUpdate
from mysql_connect_funcs import get_df_tblName, get_df_query
from flask import Flask, Response, request, redirect, session, url_for
import dash_mantine_components as dmc
from components.header import header
from components.sidebar import sidebar
from flask import send_from_directory
import datetime
import os
from dotenv import load_dotenv
from sqlalchemy import Column, Integer, String
from sqlalchemy.exc import IntegrityError
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from authlib.integrations.flask_client import OAuth
from datetime import timedelta
from flask import make_response


#------------------------------------ LOAD TICKERS ---------------------------------------

df = get_df_tblName("metadataTBL")
df = df.drop_duplicates()
df['label'] = df['symbol'] + ': ' + df['name'] + ' (' + df['exchange'] + ')'
df['value'] = df['symbol'] + '_' + df['country']
label = df['label'].to_list()
value = df['value'].to_list()

options = [{"label": lbl, "value": val} for lbl, val in zip(label, value)]


#----------------------------- LOAD ENVIROMENT VARIABLES --------------------------------

load_dotenv()
port = int(os.getenv("mysql_port"))
user = os.getenv("mysql_user")
password = os.getenv("mysql_password")
host = os.getenv("mysql_host")
database = os.getenv("mysql_database")
DATABASE_URL = f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}"

#----------------------------- CREATE FLASK SERVER ---------------------------------------

server = Flask(__name__)
server.config.update(SECRET_KEY=os.getenv("SECRET_KEY"))
server.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
server.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
server.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=30)
db = SQLAlchemy(server)

#----------------------------- SETUP GOOGLE AUTH ---------------------------------------

oauth = OAuth(server)

google = oauth.register(
    name='google',
    client_id=os.getenv("CLIENT_ID"),
    client_secret=os.getenv("CLIENT_SECRET"),
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    api_base_url='https://www.googleapis.com/oauth2/v3/',
    client_kwargs={'scope': 'openid profile email'}
)


class User(db.Model):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    given_name = Column(String(255))
    family_name = Column(String(255))

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

@server.route('/signingoogle')
def google_login():
    redirect_uri = url_for('google_auth', _external=True)
    return google.authorize_redirect(redirect_uri)

@server.route('/auth')
def google_auth():
    google = oauth.create_client('google')
    token = google.authorize_access_token()
    resp = google.get('userinfo')
    resp.raise_for_status()
    user_info = resp.json()
    session.permanent = True  # This enables long-term sessions
    #print(user_info)
    session['email'] = user_info['email']
    session['given_name'] = user_info['given_name']
    session['family_name'] = user_info['family_name']
    return redirect('/')


#----------------------------- SETUP LOGOUT --------------------------------------------

@server.route('/logout')
def logout():
    session.clear()
    resp = make_response(redirect('/login'))
    resp.set_cookie('session', '', expires=0)
    return resp

#----------------------------- SETUP ROBOTS.TXT & SITEMAP ------------------------------

@server.route("/robots.txt")
def send_robots():
    return send_from_directory("assets", "robots.txt")

@server.route("/sitemap.xml")
def sitemap():
    # Optional: pull from dash.page_registry
    pages = [page["path"] for page in dash.page_registry.values()]

    sitemap_xml = ['<?xml version="1.0" encoding="UTF-8"?>']
    sitemap_xml.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')

    for path in pages:
        sitemap_xml.append(f"""
            <url>
                <loc>https://tickersight.com.au{path}</loc>
                <lastmod>{datetime.date.today().isoformat()}</lastmod>
                <changefreq>weekly</changefreq>
                <priority>0.8</priority>
            </url>
        """)

    sitemap_xml.append('</urlset>')
    return Response("\n".join(sitemap_xml), mimetype='application/xml')

#----------------------------- DASH APP CONFIG ----------------------------------------

dash._dash_renderer._set_react_version("18.2.0")
app = dash.Dash(__name__, server=server, use_pages=True, external_stylesheets=dmc.styles.ALL, title='ASX Stock Market Research & Analysis Tools')

app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        <meta charset="UTF-8">
        <title>Tickersight Main App</title>
        <!-- Google tag (gtag.js) -->
        <script async src="https://www.googletagmanager.com/gtag/js?id=G-1M51GV8PK8"></script>
        <script>
          window.dataLayer = window.dataLayer || [];
          function gtag(){dataLayer.push(arguments);}
          gtag('js', new Date());
          gtag('config', 'G-1M51GV8PK8');
        </script>
        {%metas%}
        {%favicon%}
        {%css%}
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

#----------------------------- APP LAYOUT ----------------------------------------

layout = dmc.AppShell(
    [
        dcc.Location(id='url', refresh=True),
        dcc.Store(id="ticker", storage_type='session', data={}),
        dcc.Store(id='single_ticker_metadata', storage_type='session', data={}),
        dcc.Store(id='user-store', storage_type='session', data={}),
        dmc.AppShellHeader(header, style={'padding-left': '20px', 'padding-right': '20px'}),
        dmc.AppShellNavbar(sidebar, style={'padding-left': '10px', 'padding-right': '10px', 'padding-top': '20px'}),
        dcc.Loading([
            dmc.AppShellMain(page_container),
        ], style={"position":"absolute", "top":"20%"})
    ],
    header={"height": 48},
    navbar={"width": 250, "breakpoint": "md", "collapsed": {"mobile": True}},
    padding="md",
    id="appshell",
)

app.layout = dmc.MantineProvider(id="mantine-provider",children=[layout])



#----------------------------- NAVBAR CALLBACK ----------------------------------------

clientside_callback(
    ClientsideFunction(
        namespace='clientside',
        function_name='side_bar_toggle'
    ),
    Output("appshell", "navbar"),
    Input("burger-button", "opened"),
    State("appshell", "navbar"),
)


#----------------------------- THEME CALLBACK ----------------------------------------

clientside_callback(
    """
    function(path, opened) {
        if (opened) {
            return !opened;
        }
        return opened;
    }
    """,
    Output("burger-button", "opened"),
    Input("url", "pathname"),
    State("burger-button", "opened"),
    prevent_initial_call=True
)

clientside_callback(
    ClientsideFunction(
        namespace='clientside',
        function_name='update_theme'
    ),
    Output("mantine-provider", "forceColorScheme"),
    Output("mantine-provider", "theme"),
    Input("color-scheme-switch", "checked"),
)


#----------------------------- STORE USER SESSION INFO ----------------------------------------

@callback(
    Output("user-store", "data"),
    Input("url", "pathname"),
)
def store_username(_):
    #print(session.get("given_name", "guest"))
    return {"username": session.get("given_name", "guest")}

#----------------------------- DROPDOWN CALLBACK ----------------------------------------

@callback(
    Output("my-dynamic-dropdown", "options"),
    Input("my-dynamic-dropdown", "search_value")
)
def update_options(search_value):
    if not search_value:
        raise PreventUpdate
    return [o for o in options if search_value.lower() in o["label"].lower()]

@callback(
    Output("ticker", "data"),
    [Input("my-dynamic-dropdown", "value"),
     Input('url', 'search')],
    State("ticker", "data")
)
def get_stockID(dropdown, url, store_state):
    if dropdown:
        return dropdown
    elif url:
        return url[6:]
    else:
        if store_state:
            return store_state
        else:
            return 'TPG_AU'


#----------------------------- SETUP SELECTED TICKER STORE ----------------------------------------
@callback(
    Output("single_ticker_metadata", "data"),
    Input("ticker", "data"),
)
def meta_data_store(ticker):
    if ticker is None:
        ticker = "TPG_AU"
    symbol = ticker[0:-3]
    query = "SELECT * FROM metadataTBL WHERE symbol = " + "'" + symbol + "'"
    df = get_df_query(query)
    dict = df.to_dict()
    return dict

#----------------------------- CONFIG URL ----------------------------------------
@callback(
    Output('url', 'href'),
    Input("my-dynamic-dropdown", "value")
)
def update_url(value):
    if value:
        return f'/02-companyoverview?data={value}'


#----------------------------- RUN ----------------------------------------

if __name__ == "__main__":
    app.run(debug=False)
