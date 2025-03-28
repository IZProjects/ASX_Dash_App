import dash_mantine_components as dmc
from utils.helpers import iconify


sidebar = dmc.Box(
    children = [
         dmc.NavLink(
            label="Discover",
            leftSection=iconify(icon="lets-icons:search-alt", width = 20),
            href='/',
            variant = "filled",
            active="exact",
            color = "indigo",
        ),
        dmc.NavLink(
            label="Company Overview",
            leftSection=iconify(icon="solar:buildings-linear", width=20),
            href="/02-companyoverview",
            active="exact",
            variant="filled",
            color="indigo",
        ),
        dmc.NavLink(
            label="Financials",
            leftSection=iconify(icon="map:bank", width=20),
            href="/03-financials",
            active="exact",
            variant="filled",
            color="indigo",
        ),
        dmc.NavLink(
            label="Screener",
            leftSection=iconify(icon="meteor-icons:filter", width=20),
            href="/04-screener",
            active="exact",
            variant="filled",
            color="indigo",
        ),
        dmc.NavLink(
            label="History",
            leftSection=iconify(icon="material-symbols:calendar-clock", width=20),
            href="/05-history",
            active="exact",
            variant="filled",
            color="indigo",
        ),
        dmc.NavLink(
            label="Segment",
            leftSection=iconify(icon="typcn:flow-merge", width=20),
            href="/06-segment",
            active="exact",
            variant="filled",
            color="indigo",
        ),
        dmc.NavLink(
            label="Peers",
            leftSection=iconify(icon="typcn:group-outline", width=20),
            href="/07-peers",
            active="exact",
            variant="filled",
            color="indigo",
        ),
        ]
    )