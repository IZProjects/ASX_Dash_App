from dash import Input, Output, callback, html
import dash_mantine_components as dmc
import dash
from components.login_form import login

dash.register_page(__name__)

layout = dmc.Center(id='loginPageContainer')

@callback(
    Output("loginPageContainer", "children"),
    Input("user-store", "data")
)
def generate_loginPage(data):
    username = data.get("username", "guest")
    if username == 'guest':
        return login
    else:
        alreadylogged = dmc.Paper(
                            shadow='lg',
                            withBorder=True,
                            p="30px",
                            mt=60,
                            children=[
                                html.Form(
                                    style={"width": '300px'},
                                    method='POST',
                                    children=[
                                        dmc.Text("You are already logged in", size='xl', fw=700),
                                    ]
                                )
                            ]
                        )
        return alreadylogged