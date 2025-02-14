import pandas as pd
import json
import numpy as np
import pyodbc
import geopandas as gpd
from shapely.geometry import Point
#clientes activos de DC para unir
clientes_activos_DC = pd.read_excel(r'C:\Users\analistabi.comercial\OneDrive - FEDERAL SAS\2024\SEPTIEMBRE\ACTIVOS_DC.xlsx')
clientes_inactivos_UEN=pd.read_excel(r'C:\Users\analistabi.comercial\OneDrive - FEDERAL SAS\2024\SEPTIEMBRE\INACTIVOS_Q3.xlsx')

# Conexión a SQL Server
conn = pyodbc.connect(
    'DRIVER={ODBC Driver 17 for SQL Server};'
    'SERVER=FEDERALBD;'
    'DATABASE=FEDERAL;'
    'Trusted_Connection=yes;'
    )

# Consulta SQL
query_DC_ACTIVOS ="""WITH CLIENTES_TOTALES AS (
    SELECT
	    'DISTRITOS CULINARIOS' AS UEN,
		C.CONTRIBUYENTE AS NIT,
		C.CLIENTE AS Cliente,
		C.ALIAS,
		CC.DESCRIPCION AS CANAL,
		C.U_LATITUD  AS Latitud,
        C.U_LONGITUD AS Longitud,
		DIV2.NOMBRE AS MUNICIPIO,
		'Activo' AS 'Estado cliente',
		CAST(C.DIRECCION AS VARCHAR(255)) AS Direcciones,
		C.U_BARRIO AS Barrios,
		CONCAT(V.VENDEDOR,'-',V.NOMBRE) AS vendedor
        FROM
        FEDERAL.FEDERAL.CLIENTE C
        INNER JOIN FEDERAL.FEDERAL.VENDEDOR V ON C.VENDEDOR = V.VENDEDOR
        INNER JOIN FEDERAL.FEDERAL.DIVISION_GEOGRAFICA2 DIV2 ON C.DIVISION_GEOGRAFICA2 = DIV2.DIVISION_GEOGRAFICA2 
            AND C.DIVISION_GEOGRAFICA1 = DIV2.DIVISION_GEOGRAFICA1
        INNER JOIN FEDERAL.FEDERAL.CATEGORIA_CLIENTE CC ON C.CATEGORIA_CLIENTE = CC.CATEGORIA_CLIENTE
    WHERE
         C.ACTIVO='S' 
        AND C.U_CC_CLIENTE IN('1-01-002-1214', '1-01-002-1216') AND C.U_LATITUD IS NOT NULL AND C.U_LONGITUD IS NOT NULL
        AND V.VENDEDOR IN('125','126','383','408','413','419','420','422','423','424','425','436')
    GROUP BY 
        C.CLIENTE, 
        C.CONTRIBUYENTE,
        C.ALIAS,
        CC.DESCRIPCION,
        CONCAT(V.VENDEDOR,'-',V.NOMBRE),
        DIV2.NOMBRE,
        -- También hacemos el CAST en el GROUP BY
        CAST(C.DIRECCION AS VARCHAR(255)),
		C.U_BARRIO,
        C.U_LATITUD,
        C.U_LONGITUD 
)
SELECT * FROM CLIENTES_TOTALES""" 

query_CP_ACTIVOS="""WITH CLIENTES_TOTALES AS (
    SELECT
	    'COCINAS PROFESIONALES' AS UEN,
		C.CONTRIBUYENTE AS NIT,
		C.CLIENTE AS Cliente,
		C.ALIAS,
		CC.DESCRIPCION AS CANAL,
		C.U_LATITUD AS Latitud,
        C.U_LONGITUD AS Longitud,
		DIV2.NOMBRE AS MUNICIPIO,
		'Activo' AS 'Estado cliente',
		CAST(C.DIRECCION AS VARCHAR(255)) AS Direcciones,
		C.U_BARRIO AS Barrios,
		CONCAT(V.VENDEDOR,'-',V.NOMBRE) AS vendedor
        FROM
        FEDERAL.FEDERAL.CLIENTE C
        INNER JOIN FEDERAL.FEDERAL.VENDEDOR V ON C.VENDEDOR = V.VENDEDOR
        INNER JOIN FEDERAL.FEDERAL.DIVISION_GEOGRAFICA2 DIV2 ON C.DIVISION_GEOGRAFICA2 = DIV2.DIVISION_GEOGRAFICA2 
            AND C.DIVISION_GEOGRAFICA1 = DIV2.DIVISION_GEOGRAFICA1
        INNER JOIN FEDERAL.FEDERAL.CATEGORIA_CLIENTE CC ON C.CATEGORIA_CLIENTE = CC.CATEGORIA_CLIENTE
    WHERE
         C.ACTIVO='S' 
        AND C.U_CC_CLIENTE IN('1-01-002-1210',
'1-01-002-1211',
'1-01-002-1212',
'1-01-002-1213',
'1-01-002-1217',
'1-01-002-1298')  
AND V.VENDEDOR IN('113','111','232','410','426')
AND C.U_LATITUD IS NOT NULL AND C.U_LONGITUD IS NOT NULL
    GROUP BY 
        C.CLIENTE, 
        C.CONTRIBUYENTE,
        C.ALIAS,
        CC.DESCRIPCION,
        CONCAT(V.VENDEDOR,'-',V.NOMBRE),
        DIV2.NOMBRE,
        -- También hacemos el CAST en el GROUP BY
        CAST(C.DIRECCION AS VARCHAR(255)),
		C.U_BARRIO,
        C.U_LATITUD,
        C.U_LONGITUD 
)
SELECT * FROM CLIENTES_TOTALES"""

query_DH_ACTIVOS="""WITH CLIENTES_TOTALES AS (
    SELECT
	    'DIRECTO AL HOGAR' AS UEN,
		C.CONTRIBUYENTE AS NIT,
		C.CLIENTE AS Cliente,
		C.ALIAS,
		CC.DESCRIPCION AS CANAL,
		C.U_LATITUD AS Latitud,
        C.U_LONGITUD AS Longitud,
		DIV2.NOMBRE AS MUNICIPIO,
		'Activo' AS 'Estado cliente',
		CAST(C.DIRECCION AS VARCHAR(255)) AS Direcciones,
		C.U_BARRIO AS Barrios,
		CONCAT(V.VENDEDOR,'-',V.NOMBRE) AS vendedor
        FROM
        FEDERAL.FEDERAL.CLIENTE C
        INNER JOIN FEDERAL.FEDERAL.VENDEDOR V ON C.VENDEDOR = V.VENDEDOR
        INNER JOIN FEDERAL.FEDERAL.DIVISION_GEOGRAFICA2 DIV2 ON C.DIVISION_GEOGRAFICA2 = DIV2.DIVISION_GEOGRAFICA2 
            AND C.DIVISION_GEOGRAFICA1 = DIV2.DIVISION_GEOGRAFICA1
        INNER JOIN FEDERAL.FEDERAL.CATEGORIA_CLIENTE CC ON C.CATEGORIA_CLIENTE = CC.CATEGORIA_CLIENTE
    WHERE
         C.ACTIVO='S' 
        AND C.U_CC_CLIENTE IN('1-01-003-1301',
'1-01-003-1302',
'1-01-003-1304',
'1-01-003-1305',
'1-01-003-1316'
)
AND V.VENDEDOR IN('34','298','70','427')  
AND C.U_LATITUD IS NOT NULL AND C.U_LONGITUD IS NOT NULL
    GROUP BY 
        C.CLIENTE, 
        C.CONTRIBUYENTE,
        C.ALIAS,
        CC.DESCRIPCION,
        CONCAT(V.VENDEDOR,'-',V.NOMBRE),
        DIV2.NOMBRE,
        -- También hacemos el CAST en el GROUP BY
        CAST(C.DIRECCION AS VARCHAR(255)),
		C.U_BARRIO,
        C.U_LATITUD,
        C.U_LONGITUD 
)
SELECT * FROM CLIENTES_TOTALES"""

query_IMPACTOS_UEN="""WITH VENTAS AS (
    SELECT
		C.CLIENTE AS Cliente,
		A.DESCRIPCION AS 'Nombre referencia',
        FL.FACTURA,
		SUM(CASE 
                WHEN FL.TIPO_DOCUMENTO = 'D' THEN (FL.PRECIO_TOTAL - FL.DESCUENTO_VOLUMEN - FL.DESC_TOT_GENERAL) * -1 
                ELSE (FL.PRECIO_TOTAL - FL.DESCUENTO_VOLUMEN - FL.DESC_TOT_GENERAL) 
            END) AS TotalVenta,
        SUM(CASE 
                WHEN F.TIPO_DOCUMENTO = 'D' THEN (FL.CANTIDAD * A.PESO_BRUTO) * -1 
                ELSE (FL.CANTIDAD * A.PESO_BRUTO) 
            END) AS TOTAL_KILOS,
        CONVERT(DATE,F.FECHA) AS FECHA
        
    FROM
        FEDERAL.FEDERAL.CLIENTE C
        INNER JOIN FEDERAL.FEDERAL.FACTURA F ON C.CLIENTE = F.CLIENTE
        INNER JOIN FEDERAL.FEDERAL.FACTURA_LINEA FL ON F.FACTURA = FL.FACTURA
		INNER JOIN FEDERAL.FEDERAL.VENDEDOR V ON C.VENDEDOR = V.VENDEDOR
		INNER JOIN FEDERAL.FEDERAL.ARTICULO A ON FL.ARTICULO = A.ARTICULO
    WHERE
        CONVERT(DATE, F.FECHA)> '2024-07-01' 
        AND A.CLASIFICACION_1 = '02'
        AND C.ACTIVO='S' 
        AND C.U_CC_CLIENTE IN('1-01-002-1214', '1-01-002-1216','1-01-002-1210',
'1-01-002-1211',
'1-01-002-1212',
'1-01-002-1213',
'1-01-002-1217',
'1-01-002-1298',
'1-01-003-1301',
'1-01-003-1302',
'1-01-003-1304',
'1-01-003-1305',
'1-01-003-1316') 
AND V.VENDEDOR IN('125','126','383','408','413','419','420','422','423','424','425','436','111','113','232','410','426'
,'34','298','70','427')
    GROUP BY 
        F.FECHA,
        C.CLIENTE,
		A.DESCRIPCION,
        FL.FACTURA
)  
SELECT * FROM VENTAS
"""
query_frecuencia_venta = """
WITH compras_trimestrales AS (
    SELECT 
        C.CLIENTE AS Cliente,
        DATEPART(YEAR, F.FECHA) AS anio,
        DATEPART(QUARTER, F.FECHA) AS trimestre,
        COUNT(*) AS total_compras,
        DATEDIFF(DAY, MIN(F.FECHA), MAX(F.FECHA)) AS dias_diferencia
    FROM 
        FEDERAL.FEDERAL.CLIENTE C 
        INNER JOIN FEDERAL.FEDERAL.FACTURA F ON C.CLIENTE = F.CLIENTE 
        INNER JOIN FEDERAL.FEDERAL.FACTURA_LINEA FL ON F.FACTURA = FL.FACTURA  
        INNER JOIN FEDERAL.FEDERAL.ARTICULO A ON FL.ARTICULO = A.ARTICULO
        INNER JOIN FEDERAL.FEDERAL.VENDEDOR V ON C.VENDEDOR = V.VENDEDOR
    WHERE
        CONVERT(DATE, F.FECHA) > '2024-07-01'  
        AND A.CLASIFICACION_1 = '02'
        AND C.ACTIVO = 'S' 
        AND C.U_CC_CLIENTE IN ('1-01-002-1214', '1-01-002-1216', '1-01-002-1210',
                                '1-01-002-1211', '1-01-002-1212', '1-01-002-1213',
                                '1-01-002-1217', '1-01-002-1298', '1-01-003-1301',
                                '1-01-003-1302', '1-01-003-1304', '1-01-003-1305', 
                                '1-01-003-1316') 
        AND V.VENDEDOR IN ('125', '126', '383', '408', '413', '419', '420', '422', 
                           '423', '424', '425', '436', '111', '113', '232', '410', 
                           '426', '34', '298', '70', '427')
    GROUP BY 
        C.CLIENTE, 
        DATEPART(YEAR, F.FECHA), 
        DATEPART(QUARTER, F.FECHA)
)
SELECT 
    Cliente,
    anio,
    trimestre,
    total_compras,
    dias_diferencia,
    CASE 
        WHEN total_compras >= 12 THEN 'Semanal'
        WHEN total_compras >= 6 THEN 'Quincenal'
        WHEN total_compras >= 3 THEN 'Mensual'
        ELSE 'Ocasional'
    END AS frecuencia_compra
FROM 
    compras_trimestrales
"""
query_fecha_creacion_cliente = """
SELECT 
N.NIT,
C.CLIENTE AS Cliente,
CONVERT(DATE, N.CreateDate) AS [FECHA CREACION]
FROM FEDERAL.FEDERAL.NIT N 
INNER JOIN FEDERAL.FEDERAL.CLIENTE C ON N.NIT=C.CONTRIBUYENTE
WHERE 
CONVERT(DATE, N.CreateDate) > '2024-07-01' 
AND C.VENDEDOR IN ('125', '126', '383', '408', '413', '419', '420', '422', '423', '424', '425', '436', '111', '113', '232', '410', '426', '34', '298', '70', '427')
"""


# Ejecuta la consulta y guarda los resultados en un DataFrame
Actitvos_distritos = pd.read_sql(query_DC_ACTIVOS, conn)
Activos_cocinas=pd.read_sql(query_CP_ACTIVOS, conn)
Activos_DH=pd.read_sql(query_DH_ACTIVOS, conn)
ventas_uen=pd.read_sql(query_IMPACTOS_UEN, conn)
frecuencia_trimestral=pd.read_sql(query_frecuencia_venta, conn)
fecha_creacion=pd.read_sql(query_fecha_creacion_cliente, conn)
# Cierra la conexión
conn.close()

# Asegurar que ambas columnas 'Cliente' sean del mismo tipo (en este caso, tipo str)
#clientes_activos_DC['Cliente'] = clientes_activos_DC['Cliente'].astype(int)
#Actitvos_distritos['Cliente'] = Actitvos_distritos['Cliente'].astype(int)

# Unión de los DataFrames por la columna 'Cliente'
#clientes_activos_DC = pd.merge(clientes_activos_DC, Actitvos_distritos[['Cliente', 'TotalVenta', 'TOTAL_KILOS', 'FECHA']], 
                               #on='Cliente', how='left')

#UEN=pd.concat([clientes_activos_DC,Activos_cocinas,Activos_DH,clientes_inactivos_UEN])
#UEN.to_excel(r'C:\Users\analistabi.comercial\OneDrive - FEDERAL SAS\2024\SEPTIEMBRE\UEN_FINAL.xlsx')

clientes_activos_DC['Cliente'] = clientes_activos_DC['Cliente'].astype(int)
Actitvos_distritos['Cliente'] = Actitvos_distritos['Cliente'].astype(int)
ventas_uen['Cliente'] = ventas_uen['Cliente'].astype(int)
frecuencia_trimestral['Cliente']=frecuencia_trimestral['Cliente'].astype(int)
fecha_creacion['Cliente']=fecha_creacion['Cliente'].astype(int)

# Realizamos el primer merge
clientes_activos_DC = pd.merge(clientes_activos_DC, Actitvos_distritos[['Cliente', 'vendedor']], 
                               on='Cliente', how='left')

# Realizamos el segundo merge
clientes_activos_DC_VENTAS = pd.merge(clientes_activos_DC, ventas_uen[['Cliente','Nombre referencia','FACTURA', 'TotalVenta', 'TOTAL_KILOS', 'FECHA']], 
                                      on='Cliente', how='left')


clientes_CP_DH=pd.concat([Activos_cocinas,Activos_DH])

clientes_CP_DH['Cliente'] = clientes_CP_DH['Cliente'].astype(int)

clientes_CP_DH_VENTAS = pd.merge(clientes_CP_DH, ventas_uen[['Cliente','Nombre referencia','FACTURA', 'TotalVenta', 'TOTAL_KILOS', 'FECHA']], 
                               on='Cliente', how='left')

clientes_UEN_activos=pd.concat([clientes_activos_DC_VENTAS,clientes_CP_DH_VENTAS])

clientes_UEN_activos = pd.merge(clientes_UEN_activos, frecuencia_trimestral[['Cliente','frecuencia_compra']], 
                               on='Cliente', how='left')

clientes_UEN_activos = pd.merge(clientes_UEN_activos, fecha_creacion[['Cliente','FECHA CREACION']], 
                               on='Cliente', how='left')

clientes_UEN_activos['Latitud'] = pd.to_numeric(clientes_UEN_activos['Latitud'], errors='coerce')
clientes_UEN_activos['Longitud'] = pd.to_numeric(clientes_UEN_activos['Longitud'], errors='coerce')

# Ahora puedes concatenar tus DataFrames
UEN = pd.concat([clientes_UEN_activos, clientes_inactivos_UEN])


# Supongamos que tienes un DataFrame llamado UEN con las columnas 'Latitud' y 'Longitud'
# Paso 1: Validar si hay valores vacíos en Latitud o Longitud
missing_coords = UEN[['Latitud', 'Longitud']].isnull().sum()
print("Valores faltantes en las coordenadas:")
print(missing_coords)

# Paso 2: Verificar si las coordenadas están dentro del rango válido para Colombia
lat_min, lat_max = -4.227, 13.394
lon_min, lon_max = -81.728, -66.876

# Crear una máscara booleana para detectar valores fuera de rango
coords_out_of_range = UEN[
(UEN['Latitud'] < lat_min) | (UEN['Latitud'] > lat_max) |
(UEN['Longitud'] < lon_min) | (UEN['Longitud'] > lon_max)]

print("Coordenadas fuera del rango:")
print(coords_out_of_range)


# O crear una columna adicional que indique si la coordenada es válida:
UEN['Coordenada_Valida'] = (
    (UEN['Latitud'] >= lat_min) & (UEN['Latitud'] <= lat_max) &
    (UEN['Longitud'] >= lon_min) & (UEN['Longitud'] <= lon_max)
)

# Cargar GeoJSON desde una URL
geojson_url = "https://raw.githubusercontent.com/jjagu98/geojson/refs/heads/main/map%20(5).geojson"
try:
    zonas_geojson = gpd.read_file(geojson_url)
    zonas_geojson_json = json.loads(zonas_geojson.to_json())
except Exception as e:
    print(f"Error cargando GeoJSON: {e}")


geometry = [Point(xy) for xy in zip(UEN['Longitud'], UEN['Latitud'])]
UEN = gpd.GeoDataFrame(UEN, geometry=geometry)

UEN = gpd.sjoin(UEN, zonas_geojson, how='left', op='within')

codigos_a_actualizar = [6580,
7115,
25714,
22275,
26137,
5061,
26042,
21899,
196,
14714,
22098,
26409,
14804,
25457,
11786,
19516,
6023,
19606,
25604,
5150,
29419,
26845,
27796,
12381,
29984,
14670,
5095,
22981,
22589,
20655,
29483,
6578,
29682,
12308,
26089,
11774,
28624,
14326,
22059,
29734,
17098,
24007,
21718,
19886,
25503,
30074,
2782,
29812,
21907,
20325,
25333,
14831,
22328,
23054,
26431,
20236,
29305,
15027,
21935,
25195,
14978,
20914,
2693,
29805,
17029,
9392,
15878,
22214,
22170,
18156,
27251,
22097,
25393,
26381,
28428,
25633,
23186,
16237,
22992,
26967,
28280,
15033,
29470,
22003,
26260,
15591,
21991,
21934,
12309,
28685,
28695,
29762,
30043,
13676,
22288,
19138,
27420,
29999,
29978,
27000,
22229,
26259,
6616,
29791,
15410,
9389,
21953,
25407,
14984,
14255,
28648,
28651,
28635,
26024,
17809,
26689,
12867,
28462,
30104,
26078,
6426,
26038,
28763,
4066,
29052,
9983,
26170,
25678,
29493,
30094,
20645,
30169,
28315,
28392,
30178,
29400,
9329,
28637,
29785,
28877,
30230,
5941,
28178,
30206,
25692,
28417,
30239,
26069
]

UEN.loc[UEN['Cliente'].isin(codigos_a_actualizar), 'vendedor'] = 'NUEVO VENDEDOR'
#La importación de valores numericos para Latitud y Longitud debe hacerse desde la consulta SQL
UEN_FINAL = UEN[(UEN['Coordenada_Valida'] == True) & UEN['vendedor'].notna()]

# Suponiendo que UEN_FINAL es tu DataFrame y ya está cargado

# Lista de municipios aledaños a Medellín
municipios_medellin = ['MEDELLÍN','ENVIGADO','CALDAS', 'SABANETA','ITAGUI', 'ITAGÜÍ', 'BELLO', 'LA ESTRELLA', 'COPACABANA', 'GIRARDOTA', 'BARBOSA','RIONEGRO','MARINILLA','El CARMEN DE VIBORAL','LA CEJA','GUARNE','RETIRO']

# Lista de municipios aledaños a Bogotá
municipios_bogota = ['SOACHA', 'CHÍA', 'ZIPAQUIRÁ', 'CAJICÁ', 'TABIO', 'MOSQUERA', 'FUNZA', 'MADRID','COTA','FACATATIVÁ','SANTAFE DE BOGOTA D.C.']

# Función para normalizar y reemplazar los municipios
def reemplazar_municipios(municipio):
    if municipio in municipios_medellin:
        return 'MEDELLIN'
    elif municipio in municipios_bogota:
        return 'BOGOTA'
    return municipio
# Aplicar la función a la columna 'MUNICIPIO'
UEN_FINAL['MUNICIPIO'] = UEN_FINAL['MUNICIPIO'].apply(reemplazar_municipios)



UEN_FINAL.to_excel(r'C:\Users\analistabi.comercial\OneDrive - FEDERAL SAS\2024\SEPTIEMBRE\UEN_FINAL.xlsx')
UEN.to_excel(r'C:\Users\analistabi.comercial\OneDrive - FEDERAL SAS\2024\SEPTIEMBRE\UEN1.xlsx')

#Corregir el conteo de clientes inactivos el kpi mejor dicho
