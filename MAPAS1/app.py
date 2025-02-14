import dash
from dash import Dash, html, dcc,callback
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc

# Inicializar la aplicación
app = dash.Dash(
    __name__, external_stylesheets=[dbc.themes.BOOTSTRAP], use_pages=True,
    pages_folder="c:/Users/analistabi.comercial/OneDrive - FEDERAL SAS/MAPAS1"
)

app.config.suppress_callback_exceptions = True

# Navbar para la navegación entre páginas
navbar = dbc.NavbarSimple(
    dbc.DropdownMenu(
        [
            dbc.DropdownMenuItem(page["name"], href=page["path"])
            for page in dash.page_registry.values()
            if page["module"] != "pages.not_found_404"
        ]
    )
)

# Layout global con dcc.Store globales
app.layout = dbc.Container(html.Div([
    dcc.Location(id='url', refresh=False),  #
    dash.page_container  # Aquí se cargan las páginas (Mapas y KPIs)
]), fluid=True)


# Correr la aplicación
if __name__ == "__main__":
    app.run_server(debug=True)
