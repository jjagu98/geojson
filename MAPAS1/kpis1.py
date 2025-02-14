import dash

dash.register_page(__name__, path='/kpis', name="KPI")

import dash_table
from dash import dcc, html,callback
from dash.dependencies import Input, Output, State
import logging
from statsmodels.tsa.arima.model import ARIMA
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import geopandas as gpd
import json
from shapely.geometry import Point
from sklearn.cluster import KMeans
from scipy.spatial.distance import cdist
import io
import numpy as np
import urllib.parse 
from ETL import UEN_FINAL

data=UEN_FINAL

layout = html.Div([

    # KPIs en la parte superior
    html.Div([
        html.Div([
            html.H3("Efectividad"),
            html.Div(id="efectividad"),  # Este valor será actualizado dinámicamente
        ], style={'display': 'inline-block', 'width': '25%', 'vertical-align': 'top', 'text-align': 'center','fontSize': '15px', 'fontFamily': 'Arial'}),

        html.Div([
            html.H3("Cobertura"),
            html.Div(id="cobertura"),  # Este valor será actualizado dinámicamente
        ], style={'display': 'inline-block', 'width': '25%', 'vertical-align': 'top', 'text-align': 'center','fontSize': '15px', 'fontFamily': 'Arial'}),

        html.Div([
            html.H3("Dropsize Venta"),
            html.Div(id="dropsize_venta"),  # Este valor será actualizado dinámicamente
        ], style={'display': 'inline-block', 'width': '25%', 'vertical-align': 'top', 'text-align': 'center','fontSize': '15px', 'fontFamily': 'Arial'}),

        html.Div([
            html.H3("Dropsize Kilos"),
            html.Div(id="dropsize_kilos"),  # Este valor será actualizado dinámicamente
        ], style={'display': 'inline-block', 'width': '25%', 'vertical-align': 'top', 'text-align': 'center','fontSize': '15px', 'fontFamily': 'Arial'}),
    ], style={'text-align': 'center', 'margin-bottom': '20px'}),

    # Fila principal para las tablas y el gráfico
    html.Div([
        # Columna izquierda para tablas de frecuencia y clasificación
        html.Div([
            html.H2("Tabla de Frecuencia de Compra"),
            dash_table.DataTable(
                id='table_frecuencias',
                columns=[],  # Las columnas se definirán dinámicamente
                data=[],
                 row_selectable='single', 
                style_table={'height': '300px', 'overflowY': 'auto', 'width': '100%'}
            ),
            html.Div(style={'margin-bottom': '10px','margin-top': '-20px','fontSize': '15px', 'fontFamily': 'Arial'}),  # Espacio entre tablas

            html.H2("Clasificación de Clientes por Kilogramos"),
            dash_table.DataTable(
                id='table_clasificacion',
                columns=[],  # Las columnas se definirán dinámicamente
                data=[],
                 row_selectable='single', 
                style_table={'height': '300px', 'overflowY': 'auto', 'width': '100%'}
            )
        ], style={'display': 'inline-block', 'width': '40%', 'vertical-align': 'top','fontSize': '15px', 'fontFamily': 'Arial'}),

        # Columna derecha para el gráfico y la tabla de Clientes Creados por Vendedor
        html.Div([
            dcc.Graph(
                id='ventas_semanales',
                figure={},  # El gráfico se definirá dinámicamente
                style={'width': '100%', 'height': '300px', 'margin-bottom': '10px','margin-top': '-20px','fontSize': '15px', 'fontFamily': 'Arial'}
            ),

            html.Div([
                html.H2("Clientes Creados por Vendedor"),
                dash_table.DataTable(
                    id='table_clientes_creados',
                    columns=[],  # Las columnas se definirán dinámicamente
                    data=[],
                     row_selectable='single', 
                    style_table={'height': '300px', 'overflowY': 'auto', 'width': '100%'}
                )
            ], style={'margin-top': '60px', 'margin-left': '20px'})
        ], style={'display': 'inline-block', 'width': '59%', 'vertical-align': 'top','fontSize': '15px', 'fontFamily': 'Arial'}),
    ], style={'width': '100%'}),

    # Sección para seleccionar componente a exportar y botón de exportar
    html.Div([
        html.H2("Exportar Datos Seleccionados"),
        dcc.Dropdown(
            id='component-id',  # Identificador del componente
            options=[
                {'label': 'Tabla de Frecuencia de Compra', 'value': 'table_frecuencias'},
                {'label': 'Clasificación de Clientes', 'value': 'table_clasificacion'},
                {'label': 'Clientes Creados por Vendedor', 'value': 'table_clientes_creados'},
                {'label': 'Gráfico de Ventas Semanales', 'value': 'ventas_semanales'}
            ],
            placeholder="Selecciona el componente del cual exportar",
            style={'width': '50%', 'margin': '20px auto'}
        ),
        html.Button('Exportar a Excel', id='exportar-excel-kpis', n_clicks=0),
        dcc.Download(id="download-excel-kpis")  # Componente para la descarga
    ], style={'text-align': 'center','fontSize': '15px', 'fontFamily': 'Arial'})
])

logging.basicConfig(level=logging.INFO)

@callback(
    [
        Output('efectividad', 'children'),
        Output('cobertura', 'children'),
        Output('dropsize_venta', 'children'),
        Output('dropsize_kilos', 'children'),
        Output('table_frecuencias', 'data'),
        Output('table_frecuencias', 'columns'),
        Output('table_clasificacion', 'data'),
        Output('table_clasificacion', 'columns'),
        Output('ventas_semanales', 'figure'),
        Output('table_clientes_creados', 'data'),
        Output('table_clientes_creados', 'columns')
    ],
    Input('url', 'search')
)
def actualizar_dashboard(query_string):
    # Si no hay query string, no hacer nada
    if not query_string:
        return (
            dash.no_update, dash.no_update, dash.no_update, dash.no_update,
            [],  # table_frecuencias.data
            [{"name": "frecuencia_compra", "id": "frecuencia_compra"}, {"name": "total_clientes", "id": "total_clientes"}],  # table_frecuencias.columns
            [],  # table_clasificacion.data
            [{"name": "Calificación", "id": "Calificación"}, {"name": "total_clientes", "id": "total_clientes"}],  # table_clasificacion.columns
            {},  # ventas_semanales.figure
            [],  # table_clientes_creados.data
            [{"name": "vendedor", "id": "vendedor"}, {"name": "Clientes Creados", "id": "Clientes Creados"}]  # table_clientes_creados.columns
        )

    # Decodificar la query string
    filtros = dict(urllib.parse.parse_qsl(query_string.lstrip('?')))
    
    logging.info(f"Filtros recibidos en KPIs: {filtros}")
    logging.info(f"Datos antes del filtrado: {data.head()}")

    # Filtrar los datos según los filtros aplicados
    filtered_data = data.copy()

    if filtros.get('uen'):
        # Decodificar el filtro antes de comparar
        uen_decoded = urllib.parse.unquote(filtros['uen'])
        filtered_data = filtered_data[filtered_data['UEN'] == uen_decoded]
    
    if filtros.get('ciudad'):
        ciudad_decoded = urllib.parse.unquote(filtros['ciudad'])
        filtered_data = filtered_data[filtered_data['MUNICIPIO'] == ciudad_decoded]
    
    if filtros.get('zona'):
        zona_decoded = urllib.parse.unquote(filtros['zona'])
        filtered_data = filtered_data[filtered_data['name'] == zona_decoded]
    
    if filtros.get('dia_entrega'):
        dia_entrega_decoded = urllib.parse.unquote(filtros['dia_entrega'])
        filtered_data = filtered_data[filtered_data['Dia de entrega'] == dia_entrega_decoded]
    
    if filtros.get('vendedor'):
        vendedor_decoded = urllib.parse.unquote(filtros['vendedor'])
        filtered_data = filtered_data[filtered_data['vendedor'] == vendedor_decoded]
    
    if filtros.get('canal'):
        canal_decoded = urllib.parse.unquote(filtros['canal'])
        filtered_data = filtered_data[filtered_data['CANAL'] == canal_decoded]
    
    if filtros.get('condiciones'):
        condiciones_decoded = urllib.parse.unquote(filtros['condiciones'])
        filtered_data = filtered_data[filtered_data['Estado cliente'] == condiciones_decoded]

    logging.info(f"Datos después del filtrado: {filtered_data.head()}")    

    # Si el filtrado no produjo datos, devuelve un estado vacío
    if filtered_data.empty:
        return (
            dash.no_update, dash.no_update, dash.no_update, dash.no_update,
            [],  # table_frecuencias.data
            [{"name": "frecuencia_compra", "id": "frecuencia_compra"}, {"name": "total_clientes", "id": "total_clientes"}],  # table_frecuencias.columns
            [],  # table_clasificacion.data
            [{"name": "Calificación", "id": "Calificación"}, {"name": "total_clientes", "id": "total_clientes"}],  # table_clasificacion.columns
            {},  # ventas_semanales.figure
            [],  # table_clientes_creados.data
            [{"name": "vendedor", "id": "vendedor"}, {"name": "Clientes Creados", "id": "Clientes Creados"}]  # table_clientes_creados.columns
        )

    # KPIs y demás cálculos
    clientes_impactados = filtered_data[(filtered_data['Estado cliente'] == 'Activo') & (filtered_data['TotalVenta'] > 0)]
    facturas_unicas = clientes_impactados['FACTURA'].nunique()
    efectividad = clientes_impactados['Cliente'].nunique() / filtered_data[filtered_data['Estado cliente'] == 'Activo']['Cliente'].nunique()
    cobertura = clientes_impactados['Cliente'].nunique() / filtered_data['Cliente'].nunique()
    dropsize_kilos = clientes_impactados['TOTAL_KILOS'].sum() / facturas_unicas if facturas_unicas > 0 else 0
    dropsize_venta = clientes_impactados['TotalVenta'].sum() / facturas_unicas if facturas_unicas > 0 else 0

    # Frecuencias de compra
    frecuencia_data = clientes_impactados.drop_duplicates(subset=['NIT', 'frecuencia_compra'])
    frecuencias = frecuencia_data.groupby('frecuencia_compra').agg(
        total_clientes=('NIT', 'nunique')
    ).reset_index()
    frecuencias['% de clientes'] = (frecuencias['total_clientes'] / clientes_impactados['NIT'].nunique() * 100).round(2)

    # Clasificación de clientes
    kg_por_cliente = clientes_impactados.groupby('NIT')['TOTAL_KILOS'].sum().reset_index()

    def clasificar_cliente(kg):
        if 40 <= kg <= 70:
            return 'A'
        elif 71 <= kg <= 150:
            return 'AA'
        elif 151 <= kg <= 500:
            return 'AAA'
        elif 501 <= kg <= 1000:
            return 'Bronce'
        elif 1001 <= kg <= 2000:
            return 'Plata'
        elif kg > 2000:
            return 'Oro'
        else:
            return 'Sin clasificar'

    kg_por_cliente['Calificación'] = kg_por_cliente['TOTAL_KILOS'].apply(clasificar_cliente)
    clasificacion = kg_por_cliente.groupby('Calificación').agg(total_clientes=('NIT', 'count')).reset_index()

    # Gráfico de ventas semanales
    filtered_data['FECHA'] = pd.to_datetime(filtered_data['FECHA'])
    filtered_data['Semana'] = filtered_data['FECHA'].dt.isocalendar().week
    ventas_semanales = filtered_data[filtered_data['TotalVenta'] > 0].groupby('Semana')['Cliente'].nunique().reset_index()
    modelo = ARIMA(ventas_semanales['Cliente'], order=(1, 1, 1))
    resultado = modelo.fit()
    pronostico = resultado.get_forecast(steps=4)
    pronostico_semanas = pronostico.predicted_mean
    pronostico_ic = pronostico.conf_int()

    # Crear gráfico
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=ventas_semanales['Semana'], y=ventas_semanales['Cliente'], mode='lines+markers', name='Impactos de venta por Semana'))
    fig.add_trace(go.Scatter(x=list(range(ventas_semanales['Semana'].iloc[-1] + 1, ventas_semanales['Semana'].iloc[-1] + 5)),
                             y=pronostico_semanas, mode='lines+markers', name='Pronóstico de Impactos'))
    fig.add_trace(go.Scatter(x=list(range(ventas_semanales['Semana'].iloc[-1] + 1, ventas_semanales['Semana'].iloc[-1] + 5)) + 
                             list(range(ventas_semanales['Semana'].iloc[-1] + 4, ventas_semanales['Semana'].iloc[-1], -1)),
                             y=pd.concat([pronostico_ic.iloc[:, 0], pronostico_ic.iloc[::-1, 1]]),
                             fill='toself', fillcolor='rgba(0,100,80,0.2)', line=dict(color='rgba(255,255,255,0)'),
                             name='Intervalo de Confianza 95%'))
    # Agregar título al gráfico
    fig.update_layout(
    title={
        'text': 'Impactos y Pronósticos de Ventas por Semana',
        'y': 0.9,  
        'yanchor': 'top',
        'font': {
            'family': 'Arial',  # Cambia la fuente del título aquí
            'size': 24,  # Cambia el tamaño de la fuente aquí
            'color': 'black'  # Cambia el color de la fuente si es necesario
        }
    },
    xaxis_title="Semana",  # Título para el eje X
    yaxis_title="Impactos"  # Título para el eje Y
   )

    # Clientes creados por vendedor
    filtered_data['FECHA CREACION'] = pd.to_datetime(filtered_data['FECHA CREACION'])
    clientes_creados = filtered_data[filtered_data['FECHA CREACION'].notnull()]
    clientes_por_vendedor = clientes_creados.groupby('vendedor')['NIT'].nunique().reset_index()
    clientes_por_vendedor.columns = ['vendedor', 'Clientes Creados']

    # Retornar resultados calculados
    return (
        f"{efectividad:.2%}",
        f"{cobertura:.2%}",
        f"${dropsize_venta:,.2f}",
        f"{dropsize_kilos:,.2f} kilos",
        frecuencias.to_dict('records'),
        [{"name": i, "id": i} for i in frecuencias.columns],
        clasificacion.to_dict('records'),
        [{"name": i, "id": i} for i in clasificacion.columns],
        fig,
        clientes_por_vendedor.to_dict('records'),
        [{"name": i, "id": i} for i in clientes_por_vendedor.columns]
    )


@callback(
    Output("download-excel-kpis", "data"),
    [Input('exportar-excel-kpis', 'n_clicks'),
     Input('url', 'search')],
    [State('component-id', 'value'),
     State('table_frecuencias', 'data'),
     State('table_frecuencias', 'selected_rows'),
     State('table_clasificacion', 'data'),
     State('table_clasificacion', 'selected_rows'),
     State('table_clientes_creados', 'data'),
     State('table_clientes_creados', 'selected_rows'),
     State('ventas_semanales', 'selectedData')],
    prevent_initial_call=True
)
def exportar_datos(n_clicks, query_string, component_id, frecuencias_data, frecuencia_selected_row, clasificacion_data, clasificacion_selected_row, clientes_creados_data, clientes_creados_selected_row, graph_selected_data):
    if n_clicks > 0:
        # Si no hay parámetros en la URL, 'query_string' será None
        if query_string:
            filtros = dict(urllib.parse.parse_qsl(query_string.lstrip('?')))
        else:
            filtros = {}

        # Filtrar los datos según los filtros aplicados
        filtered_data = data.copy()

        if filtros.get('uen'):
            uen_decoded = urllib.parse.unquote(filtros['uen'])
            filtered_data = filtered_data[filtered_data['UEN'] == uen_decoded]
    
        if filtros.get('ciudad'):
            ciudad_decoded = urllib.parse.unquote(filtros['ciudad'])
            filtered_data = filtered_data[filtered_data['MUNICIPIO'] == ciudad_decoded]
    
        if filtros.get('zona'):
            zona_decoded = urllib.parse.unquote(filtros['zona'])
            filtered_data = filtered_data[filtered_data['name'] == zona_decoded]
    
        if filtros.get('dia_entrega'):
            dia_entrega_decoded = urllib.parse.unquote(filtros['dia_entrega'])
            filtered_data = filtered_data[filtered_data['Dia de entrega'] == dia_entrega_decoded]
    
        if filtros.get('vendedor'):
            vendedor_decoded = urllib.parse.unquote(filtros['vendedor'])
            filtered_data = filtered_data[filtered_data['vendedor'] == vendedor_decoded]
    
        if filtros.get('canal'):
            canal_decoded = urllib.parse.unquote(filtros['canal'])
            filtered_data = filtered_data[filtered_data['CANAL'] == canal_decoded]
    
        if filtros.get('condiciones'):
            condiciones_decoded = urllib.parse.unquote(filtros['condiciones'])
            filtered_data = filtered_data[filtered_data['Estado cliente'] == condiciones_decoded]

        logging.info(f"Datos filtrados: {filtered_data.head()}")

        # Añadir columna de clasificación al filtered_data
        clientes_impactados = filtered_data[(filtered_data['Estado cliente'] == 'Activo') & (filtered_data['TotalVenta'] > 0)]
        kg_por_cliente = clientes_impactados.groupby('NIT')['TOTAL_KILOS'].sum().reset_index()

        def clasificar_cliente(kg):
            if 40 <= kg <= 70:
                return 'A'
            elif 71 <= kg <= 150:
                return 'AA'
            elif 151 <= kg <= 500:
                return 'AAA'
            elif 501 <= kg <= 1000:
                return 'Bronce'
            elif 1001 <= kg <= 2000:
                return 'Plata'
            elif kg > 2000:
                return 'Oro'
            else:
                return 'Sin clasificar'

        kg_por_cliente['Calificación'] = kg_por_cliente['TOTAL_KILOS'].apply(clasificar_cliente)

        # Unir las clasificaciones de vuelta al DataFrame filtrado
        filtered_data = filtered_data.merge(kg_por_cliente[['NIT', 'Calificación']], on='NIT', how='left')

        logging.info(f"Datos con clasificaciones: {filtered_data.head()}")

        # Exportar datos según el componente seleccionado
        if component_id == 'table_frecuencias' and frecuencia_selected_row is not None:
            frecuencia_seleccionada = frecuencias_data[frecuencia_selected_row[0]]['frecuencia_compra']
            frecuencia_data_filtrada = filtered_data[filtered_data['Frecuencia'] == frecuencia_seleccionada]
            return dcc.send_data_frame(frecuencia_data_filtrada.to_excel, "frecuencia_compra.xlsx", sheet_name="Frecuencia")
        
        elif component_id == 'table_clasificacion' and clasificacion_selected_row is not None:
            # Filtrar por clasificación seleccionada
            clasificacion_seleccionada = clasificacion_data[clasificacion_selected_row[0]]['Calificación']
            logging.info(f"Clasificación seleccionada: {clasificacion_seleccionada}")
            
            # Filtrar los datos por la clasificación seleccionada
            clasificacion_data_filtrada = filtered_data[filtered_data['Calificación'] == clasificacion_seleccionada]
            return dcc.send_data_frame(clasificacion_data_filtrada.to_excel, "clasificacion_clientes.xlsx", sheet_name="Clasificación")

        elif component_id == 'table_clientes_creados' and clientes_creados_selected_row is not None:
            vendedor_seleccionado = clientes_creados_data[clientes_creados_selected_row[0]]['vendedor']
            clientes_creados_filtrados = filtered_data[filtered_data['vendedor'] == vendedor_seleccionado]
            return dcc.send_data_frame(clientes_creados_filtrados.to_excel, "clientes_creados.xlsx", sheet_name="Clientes Creados")
            
        elif component_id == 'ventas_semanales' and graph_selected_data is not None:
            puntos_seleccionados = pd.DataFrame(graph_selected_data['points'])
            return dcc.send_data_frame(puntos_seleccionados.to_excel, "ventas_semanales.xlsx", sheet_name="Ventas Semanales")

    raise dash.exceptions.PreventUpdate
