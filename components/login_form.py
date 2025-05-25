from dash import html
from dash_iconify import DashIconify
import dash_mantine_components as dmc

loginButtonStyle = {
    "background": "royalblue",
    "padding": "5px 20px",
    "border": "none",
    "borderRadius": "20px",
    "color": "white",
    "fontSize": "16px",
    "width": "100%"

}

loginWithGoogleStyle = {
    "textDecoration": "white",
    "borderRadius": "50px",
}


login = dmc.Paper(
                shadow='lg',
                withBorder=True,
                p="30px",
                mt=60,
                children=[
                    html.Form(
                        style={"width": '300px'},
                        method='POST',
                        children=[
                            dmc.Text("Sign in ", size='xl', fw=700),
                            dmc.Text("Please log in to continue. No registration required.", c='gray', size='xs', mb=10),
                            html.A(
                                href='/signingoogle',
                                style=loginWithGoogleStyle,
                                children=[
                                    dmc.Button(
                                        "Login with Google",
                                        variant="outline",
                                        color="royalblue",
                                        fullWidth=True,
                                        radius='xl',
                                        leftSection=DashIconify(icon="flat-color-icons:google"),
                                    ),
                                ]
                            ),
                        ]
                    )
                ]
            )
