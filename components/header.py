from dash import dcc, Input, Output, clientside_callback
import dash_mantine_components as dmc
from dash_iconify import DashIconify

burger = dmc.Burger(id="burger-button", size="sm", hiddenFrom="md", opened=False),

dropdown = dcc.Dropdown(id="my-dynamic-dropdown", placeholder="Search...", className='Dropdown-2', optionHeight=50)

theme_toggle = dmc.Switch(
    offLabel=DashIconify(icon="radix-icons:sun", width=15, color=dmc.DEFAULT_THEME["colors"]["yellow"][8]),
    onLabel=DashIconify(icon="radix-icons:moon", width=15, color=dmc.DEFAULT_THEME["colors"]["yellow"][6]),
    id="color-scheme-switch",
    persistence=True,
    persistence_type='local',
    checked=False
)

menu = dmc.Menu(
            children=[
                dmc.MenuTarget(
                    dmc.Box(
                        id='avatar-indicator',
                        children=[dmc.ActionIcon(DashIconify(icon="solar:settings-outline", width=150), variant='subtle')]
                    )
                ),
            ]
        )

title = dmc.Title("Tickersight", c="blue", visibleFrom='md')

header = dmc.Grid(
    children=[
        dmc.GridCol(burger, span="content"),
        dmc.GridCol(title, span="content"),
        dmc.GridCol(dropdown, span="auto", id='search-dropdown'),
        dmc.GridCol(theme_toggle, span="content"),
        dmc.GridCol(menu, span="content"),
    ],
    gutter="xl",
    justify="space-around",
    align="center",
)

clientside_callback(
    """
    function(theme) {
        if (theme === 'dark') {
            return 'darkDropdown';
        } else {
            return 'lightDropdown';
        }
    }
    """,
    Output("search-dropdown", "className"),
    Input("mantine-provider", "forceColorScheme")
)