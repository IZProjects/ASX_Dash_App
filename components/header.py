from dash import dcc, callback, Input, Output
import dash_mantine_components as dmc
from utils.helpers import iconify

burger = dmc.Burger(id="burger-button", size="sm", hiddenFrom="sm", opened=False),

dropdown = dcc.Dropdown(id="my-dynamic-dropdown", placeholder="Search...", className='Dropdown-2')

menu = dmc.Menu(
            children=[
                dmc.MenuTarget(
                    dmc.Box(
                        id='avatar-indicator',
                        children=[dmc.ActionIcon(iconify(icon="solar:settings-outline", width=150), variant='subtle')]
                    )
                ),
                dmc.MenuDropdown(
                    [
                        dmc.MenuItem(
                            dmc.NavLink(
                                id='color-scheme-toggle',
                                n_clicks=0,
                                rightSection=iconify(icon="ic:baseline-light-mode",  color='100%'),
                            ),
                        ),
                    ]
                ),
            ]
        )

title = dmc.Title("ASX Dashboard", c="blue")

header = dmc.Grid(
    children=[
        dmc.GridCol(burger, span="content"),
        dmc.GridCol(title, span="content"),
        dmc.GridCol(dropdown, span="auto"),
        dmc.GridCol(menu, span="content"),
    ],
    gutter="xl",
    justify="space-around",
    align="center",
)

"""@callback(
    Output(component_id="my-dynamic-dropdown", component_property='className'),
     Input("mantine-provider", "forceColorScheme")
)
def change_dropdown_color(theme):
    if theme == "light":
        return 'dropdown_light'
    else:
        return 'dropdown_dark'"""
