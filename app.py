import dash
from dash import html
import dash_bootstrap_components as dbc

# Initialize the Dash app with Bootstrap theme
app = dash.Dash(
    __name__,
    use_pages=True,
    external_stylesheets=[
        dbc.themes.DARKLY,
        "https://use.fontawesome.com/releases/v5.15.4/css/all.css"
    ]
)

app.title = "Wall-ET"

# Define the navbar with navigation links
navbar = dbc.Navbar(
    dbc.Container([
        html.A(
            dbc.NavbarBrand([
                html.I(className="fas fa-robot me-2"),  # Robot icon for ET
                "Wall-ET"
            ], className="ms-2"),
            href="/",
            style={"textDecoration": "none"}
        ),
        dbc.Nav([
            dbc.NavItem(dbc.NavLink(
                page["name"],
                href=page["path"],
                active="exact"
            )) for page in dash.page_registry.values() if page.get("nav", True) is not False
        ], className="ms-auto")
    ]),
    dark=True,
    color="dark",
    className="mb-2"
)

# Main app layout
app.layout = html.Div([
    navbar,
    dbc.Container([
        dash.page_container
    ], fluid=True)
], className="bg-dark text-white min-vh-100")

if __name__ == '__main__':
    app.run_server(debug=True) 