
import dash
   
# Define tus nombres de usuario y contraseñas

# Inicialización de la aplicación Dash
dash.register_page(__name__, path='/', name="Mapas")

from dash import dcc, html,callback
import logging  
from dash.dependencies import Input, Output, State
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import geopandas as gpd
import json
from shapely.geometry import Point
from sklearn.cluster import KMeans
import urllib.parse
from scipy.spatial.distance import cdist
import io
import numpy as np
from ETL import UEN_FINAL
# Cargar los datos
#clientes_con_geozona = pd.read_excel(r'C:\Users\analistabi.comercial\Downloads\UEN.xlsx')
clientes_con_geozona=UEN_FINAL

# Cargar GeoJSON desde una URL
geojson_url = "https://raw.githubusercontent.com/jjagu98/geojson/refs/heads/main/map%20(5).geojson"
try:
    zonas_geojson = gpd.read_file(geojson_url)
    zonas_geojson_json = json.loads(zonas_geojson.to_json())
except Exception as e:
    print(f"Error cargando GeoJSON: {e}")

layout = html.Div([
    # Filtros y KPIs
    html.Div([
        # Filtro de UEN
        html.Div([
            html.Label("UEN"),
            dcc.Dropdown(
                id='uen-dropdown',
                options=[{'label': uen, 'value': uen} for uen in clientes_con_geozona['UEN'].unique() if pd.notnull(uen)],
                value=None,
                multi=False,
                style={'width': '100%', 'fontSize': '10px', 'fontFamily': 'Arial'}
            )
        ], style={'display': 'inline-block', 'width': '12%', 'margin-right': '0.5%'}),

        # Filtro de Municipio
        html.Div([
            html.Label("Municipio"),
            dcc.Dropdown(
                id='ciudad-dropdown',
                options=[{'label': ciudad, 'value': ciudad} for ciudad in clientes_con_geozona['MUNICIPIO'].unique() if pd.notnull(ciudad)],
                value=None,
                multi=False,
                style={'width': '100%', 'fontSize': '10px', 'fontFamily': 'Arial'}
            )
        ], style={'display': 'inline-block', 'width': '12%', 'margin-right': '0.5%'}),

        # Filtro de Comuna/Localidad
        html.Div([
            html.Label("Comuna/Localidad"),
            dcc.Dropdown(
                id='zona-dropdown',
                options=[{'label': zona, 'value': zona} for zona in clientes_con_geozona['name'].unique() if pd.notnull(zona)],
                value=None,
                multi=False,
                style={'width': '100%', 'fontSize': '10px', 'fontFamily': 'Arial'}
            )
        ], style={'display': 'inline-block', 'width': '12%', 'margin-right': '0.5%'}),

        # Filtro de Día de entrega
        html.Div([
            html.Label("Día de entrega"),
            dcc.Dropdown(
                id='dia-entrega-dropdown',
                options=[{'label': dia, 'value': dia} for dia in clientes_con_geozona['Dia de entrega'].unique() if pd.notnull(dia)],
                value=None,
                multi=False,
                style={'width': '100%', 'fontSize': '10px', 'fontFamily': 'Arial'}
            )
        ], style={'display': 'inline-block', 'width': '12%', 'margin-right': '0.5%'}),

        # Filtro de Vendedor
        html.Div([
            html.Label("Vendedor"),
            dcc.Dropdown(
                id='vendedor-dropdown',
                options=[{'label': vendedor, 'value': vendedor} for vendedor in clientes_con_geozona['vendedor'].unique() if pd.notnull(vendedor)],
                value=None,
                multi=False,
                style={'width': '100%', 'fontSize': '10px', 'fontFamily': 'Arial'}
            )
        ], style={'display': 'inline-block', 'width': '12%', 'margin-right': '0.5%'}),

        # Filtro de Canal
        html.Div([
            html.Label("Canal"),
            dcc.Dropdown(
                id='canal-dropdown',
                options=[{'label': canal, 'value': canal} for canal in clientes_con_geozona['CANAL'].unique() if pd.notnull(canal)],
                value=None,
                multi=False,
                style={'width': '100%', 'fontSize': '10px', 'fontFamily': 'Arial'}
            )
        ], style={'display': 'inline-block', 'width': '12%', 'margin-right': '0.5%'}),

        # Filtro de Punteo
        html.Div([
            html.Label("Estado cliente"),
            dcc.Dropdown(
                id='condiciones-dropdown',
                options=[{'label': etiqueta, 'value': etiqueta} for etiqueta in clientes_con_geozona['Estado cliente'].unique() if pd.notnull(etiqueta)],
                value=None,
                multi=False,
                style={'width': '100%', 'fontSize': '10px', 'fontFamily': 'Arial'}
            )
        ], style={'display': 'inline-block', 'width': '12%'}),

        # KPIs
        html.Div([
            html.Label("Número de clientes", style={'text-align': 'center', 'display': 'block'}),
            html.Div(id='num-clients', style={'padding': '10px', 'border': 'none', 'font-size': '15px', 'text-align': 'center', 'fontFamily': 'Arial'})
        ], style={'display': 'inline-block', 'width': '8%', 'vertical-align': 'top', 'text-align': 'center'}),

        html.Div([
            html.Label("Venta Total", style={'text-align': 'center', 'display': 'block'}),
            html.Div(id='venta-promedio', style={'padding': '10px', 'border': 'none', 'font-size': '15px', 'text-align': 'center', 'fontFamily': 'Arial'})
        ], style={'display': 'inline-block', 'width': '8%', 'vertical-align': 'top', 'text-align': 'center'}),

        html.Div([
            html.Label("Kilos totales", style={'text-align': 'center', 'display': 'block'}),
            html.Div(id='venta-promedio-kg', style={'padding': '10px', 'border': 'none', 'font-size': '15px', 'text-align': 'center', 'fontFamily': 'Arial'})
        ], style={'display': 'inline-block', 'width': '8%', 'vertical-align': 'top', 'text-align': 'center'}),
    ], style={'display': 'flex', 'justify-content': 'space-between', 'padding-top': '20px'}),

    # Mapa
    html.Div([
        dcc.Graph(id='mapa', config={'scrollZoom': True, 'displayModeBar': True}, style={'width': '100%', 'height': '90vh'})
    ]),
   html.Div([
    html.Button('Borrar Polígono', id='borrar-poligono', n_clicks=0, style={'margin-right': '20px', 'margin-bottom': '10px', 'display': 'inline-block'}),
    html.Button('Exportar a Excel', id='exportar-excel', n_clicks=0, style={'margin-right': '20px', 'margin-bottom': '10px', 'display': 'inline-block'}),
    html.Button('Ver KPIs', id='go-to-kpis', n_clicks=0, style={'margin-bottom': '10px', 'display': 'inline-block'})
], style={'text-align': 'left', 'padding-top': '20px'}),
    
    dcc.Download(id="download-excel"),
    dcc.Location(id='url', refresh=True)
])

logging.basicConfig(level=logging.INFO)

# Callback para actualizar la URL y redirigir
@callback(
    Output('url', 'href'),  # Actualizar el href para redirigir
    Input('go-to-kpis', 'n_clicks'),  # Detectar clic en el botón
    State('uen-dropdown', 'value'),
    State('ciudad-dropdown', 'value'),
    State('zona-dropdown', 'value'),
    State('dia-entrega-dropdown', 'value'),
    State('vendedor-dropdown', 'value'),
    State('canal-dropdown', 'value'),
    State('condiciones-dropdown', 'value'),
    prevent_initial_call=True  # Evitar ejecutar al cargar la página
)
def update_link(n_clicks, uen, ciudad, zona, dia_entrega, vendedor, canal, condiciones):
    if n_clicks > 0:
        filtros = {
            'uen': uen,
            'ciudad': ciudad,
            'zona': zona,
            'dia_entrega': dia_entrega,
            'vendedor': vendedor,
            'canal': canal,
            'condiciones': condiciones
        }
        
        # Convertir filtros a una cadena de consulta (query string)
        query_params = '&'.join([f"{k}={v}" for k, v in filtros.items() if v])
        
        # Redirigir a la página de KPIs con los parámetros
        return f"/kpis?{query_params}"
    
    return None

@callback(
    [Output('uen-dropdown', 'value'),
     Output('ciudad-dropdown', 'value'),
     Output('zona-dropdown', 'value'),
     Output('dia-entrega-dropdown', 'value'),
     Output('vendedor-dropdown', 'value'),
     Output('canal-dropdown', 'value'),
     Output('condiciones-dropdown', 'value')],
    Input('url', 'search')  # Detectar los parámetros en la URL
)
def restore_filters_from_url(query_string):
    if query_string:
        # Decodificar la query string y obtener los filtros
        filtros = dict(urllib.parse.parse_qsl(query_string.lstrip('?')))
        
        return (
            filtros.get('uen'),
            filtros.get('ciudad'),
            filtros.get('zona'),
            filtros.get('dia_entrega'),
            filtros.get('vendedor'),
            filtros.get('canal'),
            filtros.get('condiciones')
        )
    
    # Si no hay filtros, devolver None para limpiar los dropdowns
    return [None] * 7


@callback(
    [
        Output('ciudad-dropdown', 'options'),
        Output('zona-dropdown', 'options'),
        Output('dia-entrega-dropdown', 'options'),
        Output('vendedor-dropdown', 'options'),
        Output('canal-dropdown', 'options'),
        Output('condiciones-dropdown', 'options')
    ],
    [
        Input('uen-dropdown', 'value'),
        Input('ciudad-dropdown', 'value'),
        Input('zona-dropdown', 'value'),
        Input('dia-entrega-dropdown', 'value'),
        Input('vendedor-dropdown', 'value'),
        Input('canal-dropdown', 'value'),
        Input('condiciones-dropdown', 'value')
    ])
def update_filters(uen, ciudad, zona, dia_entrega, vendedor, canal, condiciones):
    # Filtrar datos basados en la selección actual de cada filtro, excepto el propio
    base_filtered_data = clientes_con_geozona[
        (clientes_con_geozona['UEN'] == uen if uen else True) &
        (clientes_con_geozona['MUNICIPIO'] == ciudad if ciudad else True) &
        (clientes_con_geozona['name'] == zona if zona else True) &
        (clientes_con_geozona['Dia de entrega'] == dia_entrega if dia_entrega else True) &
        (clientes_con_geozona['vendedor'] == vendedor if vendedor else True) &
        (clientes_con_geozona['CANAL'] == canal if canal else True) &
        (clientes_con_geozona['Estado cliente'] == condiciones if condiciones else True)
    ]

    # Opciones dinámicas para cada dropdown basadas en los filtros actuales
    ciudad_options = [{'label': i, 'value': i} for i in base_filtered_data['MUNICIPIO'].unique()]
    zona_options = [{'label': i, 'value': i} for i in base_filtered_data['name'].dropna().unique()] if ciudad in ['BOGOTA', 'MEDELLIN'] else [{'label': 'N/A', 'value': 'N/A'}]
    dia_options = [{'label': i, 'value': i} for i in base_filtered_data['Dia de entrega'].dropna().unique()] if ciudad in ['BOGOTA', 'MEDELLIN'] else [{'label': 'N/A', 'value': 'N/A'}]
    vendedor_options = [{'label': i, 'value': i} for i in base_filtered_data['vendedor'].unique()]
    canal_options = [{'label': i, 'value': i} for i in base_filtered_data['CANAL'].unique()]
    condiciones_options = [{'label': i, 'value': i} for i in base_filtered_data['Estado cliente'].unique()]

    return ciudad_options, zona_options, dia_options, vendedor_options, canal_options, condiciones_options


@callback(
    [Output('mapa', 'selectedData'), Output('mapa', 'figure')],
    [Input('borrar-poligono', 'n_clicks'),
     Input('ciudad-dropdown', 'value'),
     Input('zona-dropdown', 'value'),
     Input('condiciones-dropdown', 'value'),
     Input('vendedor-dropdown', 'value'),
     Input('dia-entrega-dropdown', 'value'),
     Input('uen-dropdown', 'value'),
     Input('canal-dropdown', 'value')]
)
def clear_polygon(n_clicks, ciudad, zona, etiqueta, vendedor, dia_entrega,uens,canales):
    ctx = dash.callback_context
    if not ctx.triggered:
        raise dash.exceptions.PreventUpdate

    trigger = ctx.triggered[0]['prop_id'].split('.')[0]

    if trigger == 'borrar-poligono' and n_clicks > 0:
        figure = update_map(ciudad, zona, etiqueta, vendedor, dia_entrega,uens,canales)
        return None, figure

    figure = update_map(ciudad, zona, etiqueta, vendedor, dia_entrega,uens,canales)
    return dash.no_update, figure

def update_map(ciudad, zonas, etiqueta, vendedores, dias_entrega, uens, canales):
    # Filtrar los datos de clientes
    filtered_data = clientes_con_geozona
    if ciudad:
        filtered_data = filtered_data[filtered_data['MUNICIPIO'] == ciudad]
    if zonas:
        filtered_data = filtered_data[filtered_data['name'] == zonas]
    if etiqueta:
        filtered_data = filtered_data[filtered_data['Estado cliente'] == etiqueta]
    if vendedores:
        filtered_data = filtered_data[filtered_data['vendedor'] == vendedores]
    if dias_entrega:
        filtered_data = filtered_data[filtered_data['Dia de entrega'] == dias_entrega]
    if uens:
        filtered_data = filtered_data[filtered_data['UEN'] == uens]
    if canales:
        filtered_data = filtered_data[filtered_data['CANAL'] == canales]

    # Determinar las zonas que tienen clientes
    zonas_con_clientes = filtered_data['name'].unique()

    # Filtrar el archivo GeoJSON para mantener solo las zonas con clientes
    zonas_filtradas_geojson = {
        'type': 'FeatureCollection',
        'features': [feature for feature in zonas_geojson_json['features']
                     if feature['properties']['name'] in zonas_con_clientes]
    }

    # Calcular el centro geográfico basado en los datos filtrados
    if not filtered_data.empty:
        center_lat = filtered_data['Latitud'].mean()
        center_lon = filtered_data['Longitud'].mean()
    else:
        center_lat = 4.7110  # Default to Bogota latitude
        center_lon = -74.0721  # Default to Bogota longitude

    # Mapa de dispersión estándar
    fig = px.scatter_mapbox(
        filtered_data,
        lat='Latitud',
        lon='Longitud',
        hover_name='ALIAS',
        color='vendedor',
        size=[10] * len(filtered_data),  # Tamaño constante para todos los puntos
        size_max=8,
        zoom=10,
        height=600
    )

    # Capas de geo-zonas
    layers = []
    for feature in zonas_filtradas_geojson['features']:
        color = feature['properties']['stroke']
        opacity = 1.0
        layers.append({
            'sourcetype': 'geojson',
            'source': {'type': 'FeatureCollection', 'features': [feature]},
            'type': 'line',
            'color': color,
            'opacity': opacity
        })

    # Condición para agregar el mapa de calor si el estado del cliente es 'Activo'
    if etiqueta == 'Activo':
        heatmap_trace = px.density_mapbox(filtered_data, lat='Latitud', lon='Longitud', z='TotalVenta',hover_name='ALIAS', radius=10).data[0]
        fig.add_trace(heatmap_trace)
        fig.update_layout(coloraxis_showscale=False)  # Oculta la barra de colores

    fig.update_layout(
        mapbox=dict(
            style="open-street-map",
            layers=layers,
            center=dict(lat=center_lat, lon=center_lon),
            zoom=10
        ),
        margin={"r":0,"t":0,"l":0,"b":0},
        legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
    )
    
    return fig



@callback(
    [Output('num-clients', 'children'),
     Output('venta-promedio', 'children'),
     Output('venta-promedio-kg', 'children')],
    [Input('mapa', 'selectedData'),
     Input('ciudad-dropdown', 'value'),
     Input('zona-dropdown', 'value'),
     Input('condiciones-dropdown', 'value'),
     Input('vendedor-dropdown', 'value'),
     Input('dia-entrega-dropdown', 'value'),
     Input('uen-dropdown', 'value'),
     Input('canal-dropdown', 'value')]
)
def update_kpis(selectedData, ciudad, zonas, etiqueta, vendedores, dias_entrega,uens,canales):
    # Filtrar los datos de clientes basado en los filtros seleccionados
    filtered_data = clientes_con_geozona
    if ciudad:
        filtered_data = filtered_data[filtered_data['MUNICIPIO'] == ciudad]
    if zonas:
        filtered_data = filtered_data[filtered_data['name']==zonas]
    if etiqueta:
        filtered_data = filtered_data[filtered_data['Estado cliente'] == etiqueta]
    if vendedores:
        filtered_data = filtered_data[filtered_data['vendedor']==vendedores]
    if dias_entrega:
        filtered_data = filtered_data[filtered_data['Dia de entrega']==dias_entrega]
    if uens:
        filtered_data = filtered_data[filtered_data['UEN']==uens]
    if canales:
        filtered_data = filtered_data[filtered_data['CANAL']==canales]
        
    if selectedData and 'points' in selectedData:
        selected_points = selectedData['points']
        selected_indices = [point['pointIndex'] for point in selected_points]
        if not all(idx < len(filtered_data) for idx in selected_indices):
            return 0, 0, 0
        filtered_data = filtered_data.iloc[selected_indices]

    # Calcular el número de clientes
    num_clients_filtered = filtered_data['Cliente'].nunique()

    # Calcular Venta Promedio y Venta Promedio KG
    venta_total = filtered_data['TotalVenta'].sum() if 'TotalVenta' in filtered_data.columns else 0
    venta_total_kg = filtered_data['TOTAL_KILOS'].sum() if 'TOTAL_KILOS' in filtered_data.columns else 0

    return num_clients_filtered, f"${venta_total:,.0f}", f"{venta_total_kg:,.2f} KG"


@callback(
    Output("download-excel", "data"),
    [Input('exportar-excel', 'n_clicks')],
    [State('ciudad-dropdown', 'value'),
     State('zona-dropdown', 'value'),
     State('condiciones-dropdown', 'value'),
     State('vendedor-dropdown', 'value'),
     State('dia-entrega-dropdown', 'value'),
     State('uen-dropdown', 'value'),
     State('canal-dropdown', 'value')],
    prevent_initial_call=True
)
def export_to_excel(n_clicks, ciudad, zonas, etiqueta, vendedores, dias_entrega,uens,canales):
    if n_clicks > 0:
        filtered_data = clientes_con_geozona
        if ciudad:
            filtered_data = filtered_data[filtered_data['MUNICIPIO'] == ciudad]
        if zonas:
            filtered_data = filtered_data[filtered_data['name']==zonas]
        if etiqueta:
            filtered_data = filtered_data[filtered_data['Estado cliente'] == etiqueta]
        if vendedores:
            filtered_data = filtered_data[filtered_data['vendedor']==vendedores]
        if dias_entrega:
            filtered_data = filtered_data[filtered_data['Dia de entrega']==dias_entrega]
        if uens:
            filtered_data = filtered_data[filtered_data['UEN']==uens]
        if canales:
            filtered_data = filtered_data[filtered_data['CANAL']==canales]
        

        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            filtered_data.to_excel(writer, index=False, sheet_name='Clientes')
        output.seek(0)

        return dcc.send_data_frame(filtered_data.to_excel, "clientes_seleccionados.xlsx", sheet_name="Clientes")
    else:
        raise dash.exceptions.PreventUpdate
        
