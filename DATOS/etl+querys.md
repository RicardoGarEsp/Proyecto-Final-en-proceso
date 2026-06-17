## Extraemos la información en la carpeta donde se esté ejecutando el código


```python
#!pip install sqlalchemy psycopg2-binary pandas openpyxl
#!pip install kagglehub
import kagglehub
import shutil
import os

# Descargar dataset
path = kagglehub.dataset_download("jaredrosas/global-superstore-orders-2016-es-esp")

# Carpeta actual
destino = os.getcwd()

# Copiar el contenido del dataset a la carpeta actual
for archivo in os.listdir(path):
    origen = os.path.join(path, archivo)
    destino_archivo = os.path.join(destino, archivo)

    if os.path.isfile(origen):
        shutil.copy2(origen, destino_archivo)
    elif os.path.isdir(origen):
        shutil.copytree(origen, destino_archivo, dirs_exist_ok=True)

print("Dataset guardado en:", destino)
```

    Dataset guardado en: C:\Users\richa\Modulo4
    

## Cargamos el archivo y lo transformamos al modelo estrella


```python
import pandas as pd

# ==========================================
# CARGAR ARCHIVO
# ==========================================

archivo = "Global Superstore Orders 2016_es-ES.xlsx"

pedidos = pd.read_excel(archivo, sheet_name="Pedidos")
personas = pd.read_excel(archivo, sheet_name="Personas")

# ==========================================
# LIMPIEZA DE FECHAS
# ==========================================

pedidos["Fecha de pedido"] = pd.to_datetime(
    pedidos["Fecha de pedido"],
    dayfirst=True
).dt.date

pedidos["Fecha de envío"] = pd.to_datetime(
    pedidos["Fecha de envío"],
    dayfirst=True
).dt.date

# ==========================================
# CREAMOS LAS DIMENSIONES DEL MODELO ESTRELLA
# ==========================================

# ==========================================
# DIM_CLIENTE
# ==========================================

DIM_CLIENTE = pedidos[
    [
        "ID de cliente",
        "Nombre de cliente",
        "Segmento"
    ]
].drop_duplicates()

# ==========================================
# DIM_PRODUCTO
# ==========================================

DIM_PRODUCTO = pedidos[
    [
        "ID de producto",
        "Categoría",
        "Subcategoría",
        "Nombre de producto"
    ]
].drop_duplicates()

# ==========================================
# DIM_GEOGRAFIA
# ==========================================

DIM_GEOGRAFIA = (
    pedidos[
        [
            "Código postal",
            "Ciudad",
            "Estado",
            "País",
            "Región",
            "Mercado"
        ]
    ]
    .drop_duplicates()
    .reset_index(drop=True)
)

DIM_GEOGRAFIA.insert(
    0,
    "id_geografia",
    range(1, len(DIM_GEOGRAFIA) + 1)
)

# ==========================================
# DIM_TIEMPO
# ==========================================

DIM_TIEMPO = (
    pedidos[["Fecha de pedido"]]
    .drop_duplicates()
    .copy()
)

DIM_TIEMPO["Fecha de pedido"] = pd.to_datetime(
    DIM_TIEMPO["Fecha de pedido"]
)

DIM_TIEMPO["dia"] = DIM_TIEMPO["Fecha de pedido"].dt.day
DIM_TIEMPO["mes"] = DIM_TIEMPO["Fecha de pedido"].dt.month
DIM_TIEMPO["trimestre"] = DIM_TIEMPO["Fecha de pedido"].dt.quarter
DIM_TIEMPO["anio"] = DIM_TIEMPO["Fecha de pedido"].dt.year

# Dejar la fecha sin hora para exportar
DIM_TIEMPO["Fecha de pedido"] = DIM_TIEMPO["Fecha de pedido"].dt.date

DIM_TIEMPO = DIM_TIEMPO.reset_index(drop=True)

DIM_TIEMPO.insert(
    0,
    "id_tiempo",
    range(1, len(DIM_TIEMPO) + 1)
)

# ==========================================
# DIM_ENVIO
# ==========================================

DIM_ENVIO = (
    pedidos[
        [
            "Fecha de envío",
            "Modo de envío",
            "Prioridad de pedido"
        ]
    ]
    .drop_duplicates()
    .reset_index(drop=True)
)

DIM_ENVIO.insert(
    0,
    "id_envio",
    range(1, len(DIM_ENVIO) + 1)
)

# ==========================================
# DIM_PERSONA
# ==========================================

DIM_PERSONA = personas.drop_duplicates().reset_index(drop=True)

DIM_PERSONA.insert(
    0,
    "id_persona",
    range(1, len(DIM_PERSONA) + 1)
)

# ==========================================
# AGREGAR FKs A PEDIDOS
# ==========================================

fact = pedidos.copy()

# ----- GEOGRAFIA -----

fact = fact.merge(
    DIM_GEOGRAFIA,
    how="left",
    on=[
        "Código postal",
        "Ciudad",
        "Estado",
        "País",
        "Región",
        "Mercado"
    ]
)

# ----- TIEMPO -----

fact = fact.merge(
    DIM_TIEMPO[
        [
            "id_tiempo",
            "Fecha de pedido"
        ]
    ],
    how="left",
    on="Fecha de pedido"
)

# ----- ENVIO -----

fact = fact.merge(
    DIM_ENVIO,
    how="left",
    on=[
        "Fecha de envío",
        "Modo de envío",
        "Prioridad de pedido"
    ]
)

# ----- PERSONA -----

fact = fact.merge(
    DIM_PERSONA[
        [
            "id_persona",
            "Región"
        ]
    ],
    how="left",
    on="Región"
)

# ==========================================
# FACT_VENTAS
# ==========================================

FACT_VENTAS = fact[
    [
        "ID de fila",
        "ID de pedido",
        "ID de cliente",
        "ID de producto",
        "id_geografia",
        "id_tiempo",
        "id_envio",
        "id_persona",
        "Ventas",
        "Cantidad",
        "Descuento",
        "Beneficio",
        "Costo de envío"
    ]
]

# ==========================================
# EXPORTAR A EXCEL
# ==========================================

with pd.ExcelWriter(
    "Modelo_Estrella_Global_Superstore.xlsx",
    date_format="dd/mm/yyyy",
    datetime_format="dd/mm/yyyy"
) as writer:

    DIM_CLIENTE.to_excel(writer, sheet_name="DIM_CLIENTE", index=False)
    DIM_PRODUCTO.to_excel(writer, sheet_name="DIM_PRODUCTO", index=False)
    DIM_GEOGRAFIA.to_excel(writer, sheet_name="DIM_GEOGRAFIA", index=False)
    DIM_TIEMPO.to_excel(writer, sheet_name="DIM_TIEMPO", index=False)
    DIM_ENVIO.to_excel(writer, sheet_name="DIM_ENVIO", index=False)
    DIM_PERSONA.to_excel(writer, sheet_name="DIM_PERSONA", index=False)
    FACT_VENTAS.to_excel(writer, sheet_name="FACT_VENTAS", index=False)

print("Modelo estrella generado correctamente.")
```

    Modelo estrella generado correctamente.
    

## TEST DE VALIDACIÓN DEL MODELO ESTRELLA


```python
print("=" * 60)
print("VALIDACIÓN DEL MODELO ESTRELLA")
print("=" * 60)

# 1. Número de registros
print("\n1. Registros")
print(f"Pedidos originales : {len(pedidos)}")
print(f"FACT_VENTAS        : {len(FACT_VENTAS)}")
print("✓ Correcto" if len(pedidos) == len(FACT_VENTAS) else "✗ Error")

# 2. Claves primarias únicas
print("\n2. Claves primarias")

dimensiones = {
    "DIM_GEOGRAFIA": ("id_geografia", DIM_GEOGRAFIA),
    "DIM_TIEMPO": ("id_tiempo", DIM_TIEMPO),
    "DIM_ENVIO": ("id_envio", DIM_ENVIO),
    "DIM_PERSONA": ("id_persona", DIM_PERSONA)
}

for nombre, (pk, df) in dimensiones.items():
    if df[pk].is_unique:
        print(f"✓ {nombre}: {pk} es única")
    else:
        print(f"✗ {nombre}: {pk} tiene duplicados")

# 3. Duplicados en dimensiones
print("\n3. Duplicados en dimensiones")

print(f"DIM_CLIENTE  : {DIM_CLIENTE.duplicated().sum()}")
print(f"DIM_PRODUCTO : {DIM_PRODUCTO.duplicated().sum()}")
print(f"DIM_GEOGRAFIA: {DIM_GEOGRAFIA.duplicated().sum()}")
print(f"DIM_TIEMPO   : {DIM_TIEMPO.duplicated().sum()}")
print(f"DIM_ENVIO    : {DIM_ENVIO.duplicated().sum()}")
print(f"DIM_PERSONA  : {DIM_PERSONA.duplicated().sum()}")

# 4. Llaves foráneas nulas
print("\n4. Llaves foráneas nulas")

fks = [
    "id_geografia",
    "id_tiempo",
    "id_envio",
    "id_persona"
]

print(FACT_VENTAS[fks].isnull().sum())

# 5. Integridad referencial
print("\n5. Integridad referencial")

print(
    "Clientes:",
    FACT_VENTAS["ID de cliente"].isin(DIM_CLIENTE["ID de cliente"]).all()
)

print(
    "Productos:",
    FACT_VENTAS["ID de producto"].isin(DIM_PRODUCTO["ID de producto"]).all()
)

print(
    "Geografía:",
    FACT_VENTAS["id_geografia"].isin(DIM_GEOGRAFIA["id_geografia"]).all()
)

print(
    "Tiempo:",
    FACT_VENTAS["id_tiempo"].isin(DIM_TIEMPO["id_tiempo"]).all()
)

print(
    "Envío:",
    FACT_VENTAS["id_envio"].isin(DIM_ENVIO["id_envio"]).all()
)

print(
    "Persona:",
    FACT_VENTAS["id_persona"].isin(DIM_PERSONA["id_persona"]).all()
)

# 6. Totales de medidas
print("\n6. Validación de medidas")

medidas = [
    "Ventas",
    "Cantidad",
    "Descuento",
    "Beneficio",
    "Costo de envío"
]

for medida in medidas:
    original = pedidos[medida].sum()
    fact = FACT_VENTAS[medida].sum()

    if original == fact:
        print(f"✓ {medida}: OK ({original})")
    else:
        print(f"✗ {medida}: Original={original} Fact={fact}")

print("\n" + "=" * 60)
print("VALIDACIÓN FINALIZADA")
print("=" * 60)
```

    ============================================================
    VALIDACIÓN DEL MODELO ESTRELLA
    ============================================================
    
    1. Registros
    Pedidos originales : 51290
    FACT_VENTAS        : 51290
    ✓ Correcto
    
    2. Claves primarias
    ✓ DIM_GEOGRAFIA: id_geografia es única
    ✓ DIM_TIEMPO: id_tiempo es única
    ✓ DIM_ENVIO: id_envio es única
    ✓ DIM_PERSONA: id_persona es única
    
    3. Duplicados en dimensiones
    DIM_CLIENTE  : 0
    DIM_PRODUCTO : 0
    DIM_GEOGRAFIA: 0
    DIM_TIEMPO   : 0
    DIM_ENVIO    : 0
    DIM_PERSONA  : 0
    
    4. Llaves foráneas nulas
    id_geografia      0
    id_tiempo         0
    id_envio          0
    id_persona      384
    dtype: int64
    
    5. Integridad referencial
    Clientes: True
    Productos: True
    Geografía: True
    Tiempo: True
    Envío: True
    Persona: False
    
    6. Validación de medidas
    ✓ Ventas: OK (12642501.90988)
    ✓ Cantidad: OK (178312)
    ✓ Descuento: OK (7329.727999999999)
    ✓ Beneficio: OK (1467457.2912799998)
    ✓ Costo de envío: OK (1358085.7033999995)
    
    ============================================================
    VALIDACIÓN FINALIZADA
    ============================================================
    


```python
regiones_faltantes = set(pedidos["Región"]) - set(personas["Región"])

print(regiones_faltantes)
```

    {'Canadá'}
    

# Conexión con AWS


```python
from sqlalchemy import create_engine, text

# =====================================
# CONFIGURACIÓN AURORA
# =====================================

AURORA_HOST = "aurora-mod4.cluster-cr9wjf4zhb8s.us-east-1.rds.amazonaws.com"
AURORA_PASSWORD = "ModuloDiplomado4"
AURORA_DATABASE = "ecomerce"

# =====================================
# CREAR ENGINE
# =====================================

engine = create_engine(
    f"postgresql+psycopg2://postgres:{AURORA_PASSWORD}@{AURORA_HOST}:5432/{AURORA_DATABASE}"
)

# =====================================
# PRUEBA DE CONEXIÓN
# =====================================

try:
    with engine.connect() as conn:
        version = conn.execute(
            text("SELECT version();")
        ).scalar()

    print("✅ Conexión exitosa")
    print(version)

except Exception as e:
    print("❌ Error de conexión")
    print(e)
```

    ✅ Conexión exitosa
    PostgreSQL 17.7 on x86_64-pc-linux-gnu, compiled by x86_64-pc-linux-gnu-gcc (GCC) 10.5.0, 64-bit
    


```python
SCHEMA = "ecomerce_dwh"

with engine.begin() as conn:
    conn.execute(
        text(f"CREATE SCHEMA IF NOT EXISTS {SCHEMA}")
    )

print(f"✅ Schema {SCHEMA} creado correctamente")
```

    ✅ Schema ecomerce_dwh creado correctamente
    


```python
from sqlalchemy import text

# ==========================================
# DICCIONARIO DE TABLAS
# ==========================================

tables = {
    "dim_cliente": DIM_CLIENTE,
    "dim_producto": DIM_PRODUCTO,
    "dim_geografia": DIM_GEOGRAFIA,
    "dim_tiempo": DIM_TIEMPO,
    "dim_envio": DIM_ENVIO,
    "dim_persona": DIM_PERSONA,
    "fact_ventas": FACT_VENTAS
}

# ==========================================
# CARGAR TABLAS A POSTGRESQL
# ==========================================

def load_data(tables: dict, engine, schema: str = "ecomerce_dwh"):

    tablas_en_orden = [
        "dim_cliente",
        "dim_producto",
        "dim_geografia",
        "dim_tiempo",
        "dim_envio",
        "dim_persona",
        "fact_ventas"
    ]

    for nombre in tablas_en_orden:

        tables[nombre].to_sql(
            name=nombre,
            con=engine,
            schema=schema,
            if_exists="replace",
            index=False,
            chunksize=1000,
            method="multi"
        )

        print(f"✅ {nombre:15s} {len(tables[nombre]):>8,} filas cargadas")

    print("\n✅ Carga completa en PostgreSQL.")

# ==========================================
# EJECUTAR CARGA
# ==========================================

load_data(tables, engine, schema=SCHEMA)

# ==========================================
# VALIDAR CANTIDAD DE REGISTROS
# ==========================================

print("\n========== VALIDACIÓN ==========\n")

with engine.connect() as conn:

    for tabla in tables.keys():

        filas = conn.execute(
            text(f"SELECT COUNT(*) FROM {SCHEMA}.{tabla};")
        ).scalar()

        print(f"{tabla:15s}: {filas:,} filas")

print("\n✅ Validación finalizada.")
```

    ✅ dim_cliente       17,415 filas cargadas
    ✅ dim_producto       3,788 filas cargadas
    ✅ dim_geografia      3,856 filas cargadas
    ✅ dim_tiempo         1,430 filas cargadas
    ✅ dim_envio          9,471 filas cargadas
    ✅ dim_persona           24 filas cargadas
    ✅ fact_ventas       51,290 filas cargadas
    
    ✅ Carga completa en PostgreSQL.
    
    ========== VALIDACIÓN ==========
    
    dim_cliente    : 17,415 filas
    dim_producto   : 3,788 filas
    dim_geografia  : 3,856 filas
    dim_tiempo     : 1,430 filas
    dim_envio      : 9,471 filas
    dim_persona    : 24 filas
    fact_ventas    : 51,290 filas
    
    ✅ Validación finalizada.
    

## Consultas SQL

### 1. CTE + Ranking simple, ¿Qué productos generan la mayor rentabilidad?


```python
query1 = """
WITH rentabilidad_producto AS (

    SELECT
        dp."Nombre de producto" AS producto,
        SUM(fv."Beneficio") AS beneficio_total

    FROM ecomerce_dwh.fact_ventas fv
    JOIN ecomerce_dwh.dim_producto dp
        ON fv."ID de producto" = dp."ID de producto"

    GROUP BY dp."Nombre de producto"

)

SELECT
    producto,
    beneficio_total,
    RANK() OVER(ORDER BY beneficio_total DESC) AS ranking

FROM rentabilidad_producto

ORDER BY ranking
LIMIT 10;
"""

df = pd.read_sql(query1, engine)
df
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>producto</th>
      <th>beneficio_total</th>
      <th>ranking</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>Canon imageCLASS 2200 Advanced Copier</td>
      <td>25199.9280</td>
      <td>1</td>
    </tr>
    <tr>
      <th>1</th>
      <td>Cisco Smart Phone, Full Size</td>
      <td>17238.5206</td>
      <td>2</td>
    </tr>
    <tr>
      <th>2</th>
      <td>Motorola Smart Phone, Full Size</td>
      <td>17027.1130</td>
      <td>3</td>
    </tr>
    <tr>
      <th>3</th>
      <td>Hoover Stove, Red</td>
      <td>11807.9690</td>
      <td>4</td>
    </tr>
    <tr>
      <th>4</th>
      <td>Sauder Classic Bookcase, Traditional</td>
      <td>10672.0730</td>
      <td>5</td>
    </tr>
    <tr>
      <th>5</th>
      <td>Harbour Creations Executive Leather Armchair, ...</td>
      <td>10427.3260</td>
      <td>6</td>
    </tr>
    <tr>
      <th>6</th>
      <td>Nokia Smart Phone, Full Size</td>
      <td>9938.1955</td>
      <td>7</td>
    </tr>
    <tr>
      <th>7</th>
      <td>Cisco Smart Phone, with Caller ID</td>
      <td>9786.6408</td>
      <td>8</td>
    </tr>
    <tr>
      <th>8</th>
      <td>Nokia Smart Phone, with Caller ID</td>
      <td>9465.3257</td>
      <td>9</td>
    </tr>
    <tr>
      <th>9</th>
      <td>Belkin Router, USB</td>
      <td>8955.0180</td>
      <td>10</td>
    </tr>
  </tbody>
</table>
</div>



### 2. Window Function, ¿Qué categorías tienen mayores ventas pero menores márgenes?


```python
query2 = """
SELECT

    dp."Categoría",

    SUM(fv."Ventas") AS ventas_totales,

    SUM(fv."Beneficio") AS beneficio_total,

    ROUND(
        (
            SUM(fv."Beneficio") /
            NULLIF(SUM(fv."Ventas"),0)
        )::numeric,
        4
    ) AS margen,

    AVG(SUM(fv."Ventas")) OVER() AS promedio_ventas

FROM ecomerce_dwh.fact_ventas fv

JOIN ecomerce_dwh.dim_producto dp
ON fv."ID de producto" = dp."ID de producto"

GROUP BY dp."Categoría"

ORDER BY ventas_totales DESC;
"""

df = pd.read_sql(query2, engine)
df
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>Categoría</th>
      <th>ventas_totales</th>
      <th>beneficio_total</th>
      <th>margen</th>
      <th>promedio_ventas</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>Tecnología</td>
      <td>4.744557e+06</td>
      <td>663778.73318</td>
      <td>0.1399</td>
      <td>4.214167e+06</td>
    </tr>
    <tr>
      <th>1</th>
      <td>Mobiliario</td>
      <td>4.110452e+06</td>
      <td>285082.73020</td>
      <td>0.0694</td>
      <td>4.214167e+06</td>
    </tr>
    <tr>
      <th>2</th>
      <td>Material de oficina</td>
      <td>3.787493e+06</td>
      <td>518595.82790</td>
      <td>0.1369</td>
      <td>4.214167e+06</td>
    </tr>
  </tbody>
</table>
</div>



### 3. COUNT FILTER, ¿Cómo impactan los descuentos en el beneficio final?


```python
query3 = """
SELECT

    COUNT(*) FILTER (
        WHERE "Descuento" = 0
    ) AS pedidos_sin_descuento,

    COUNT(*) FILTER (
        WHERE "Descuento" > 0
    ) AS pedidos_con_descuento,

    AVG("Beneficio") FILTER (
        WHERE "Descuento" = 0
    ) AS beneficio_promedio_sin_descuento,

    AVG("Beneficio") FILTER (
        WHERE "Descuento" > 0
    ) AS beneficio_promedio_con_descuento

FROM ecomerce_dwh.fact_ventas;
"""

df = pd.read_sql(query3, engine)
df
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>pedidos_sin_descuento</th>
      <th>pedidos_con_descuento</th>
      <th>beneficio_promedio_sin_descuento</th>
      <th>beneficio_promedio_con_descuento</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>29009</td>
      <td>22281</td>
      <td>61.039514</td>
      <td>-13.609711</td>
    </tr>
  </tbody>
</table>
</div>



### 4. PERCENTILE_CONT, ¿Qué regiones presentan mejor desempeño comercial?


```python
query4 = """
SELECT

    dg."Región",

    SUM(fv."Ventas") AS ventas_totales,

    SUM(fv."Beneficio") AS beneficio_total,

    PERCENTILE_CONT(0.5)
    WITHIN GROUP (
        ORDER BY fv."Beneficio"
    ) AS mediana_beneficio

FROM ecomerce_dwh.fact_ventas fv

JOIN ecomerce_dwh.dim_geografia dg
ON fv.id_geografia = dg.id_geografia

GROUP BY dg."Región"

ORDER BY beneficio_total DESC;
"""

df = pd.read_sql(query4, engine)
df
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>Región</th>
      <th>ventas_totales</th>
      <th>beneficio_total</th>
      <th>mediana_beneficio</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>Europa Occidental</td>
      <td>1.731930e+06</td>
      <td>218433.50850</td>
      <td>15.3990</td>
    </tr>
    <tr>
      <th>1</th>
      <td>Asia Oriental</td>
      <td>8.550594e+05</td>
      <td>167101.85100</td>
      <td>23.7000</td>
    </tr>
    <tr>
      <th>2</th>
      <td>Asia Meridional</td>
      <td>8.665727e+05</td>
      <td>159336.42700</td>
      <td>19.3800</td>
    </tr>
    <tr>
      <th>3</th>
      <td>Centroamérica</td>
      <td>1.223101e+06</td>
      <td>158981.64816</td>
      <td>9.2800</td>
    </tr>
    <tr>
      <th>4</th>
      <td>Oceanía</td>
      <td>1.100185e+06</td>
      <td>120089.11200</td>
      <td>8.7660</td>
    </tr>
    <tr>
      <th>5</th>
      <td>Oeste de EE. UU.</td>
      <td>7.254578e+05</td>
      <td>108418.44890</td>
      <td>11.1664</td>
    </tr>
    <tr>
      <th>6</th>
      <td>Este de EE. UU.</td>
      <td>6.787812e+05</td>
      <td>91522.78000</td>
      <td>8.1717</td>
    </tr>
    <tr>
      <th>7</th>
      <td>Europa Septentrional</td>
      <td>6.367792e+05</td>
      <td>83923.91700</td>
      <td>11.0835</td>
    </tr>
    <tr>
      <th>8</th>
      <td>Europa Oriental</td>
      <td>3.100334e+05</td>
      <td>77084.88000</td>
      <td>14.3100</td>
    </tr>
    <tr>
      <th>9</th>
      <td>Europa Meridional</td>
      <td>6.085940e+05</td>
      <td>70109.41800</td>
      <td>13.6500</td>
    </tr>
    <tr>
      <th>10</th>
      <td>África Septentrional</td>
      <td>2.332166e+05</td>
      <td>57836.25000</td>
      <td>13.2900</td>
    </tr>
    <tr>
      <th>11</th>
      <td>Sur de EE. UU.</td>
      <td>3.917219e+05</td>
      <td>46749.43030</td>
      <td>9.0720</td>
    </tr>
    <tr>
      <th>12</th>
      <td>Centro de EE. UU.</td>
      <td>5.012399e+05</td>
      <td>39706.36250</td>
      <td>5.1840</td>
    </tr>
    <tr>
      <th>13</th>
      <td>África Central</td>
      <td>1.436300e+05</td>
      <td>35383.71000</td>
      <td>13.9200</td>
    </tr>
    <tr>
      <th>14</th>
      <td>Caribe</td>
      <td>3.242809e+05</td>
      <td>34571.32104</td>
      <td>7.1640</td>
    </tr>
    <tr>
      <th>15</th>
      <td>Sudamérica</td>
      <td>6.172237e+05</td>
      <td>28090.51788</td>
      <td>5.9200</td>
    </tr>
    <tr>
      <th>16</th>
      <td>África Meridional</td>
      <td>1.051918e+05</td>
      <td>24158.55000</td>
      <td>14.4750</td>
    </tr>
    <tr>
      <th>17</th>
      <td>África Oriental</td>
      <td>1.278560e+05</td>
      <td>21900.90900</td>
      <td>8.7150</td>
    </tr>
    <tr>
      <th>18</th>
      <td>Asia Sudoriental</td>
      <td>8.844232e+05</td>
      <td>17852.32900</td>
      <td>-1.3533</td>
    </tr>
    <tr>
      <th>19</th>
      <td>Canadá</td>
      <td>6.692817e+04</td>
      <td>17817.39000</td>
      <td>12.3450</td>
    </tr>
    <tr>
      <th>20</th>
      <td>Asia Central</td>
      <td>1.931146e+04</td>
      <td>-7282.01100</td>
      <td>-7.6140</td>
    </tr>
    <tr>
      <th>21</th>
      <td>África Occidental</td>
      <td>1.738788e+05</td>
      <td>-50407.78800</td>
      <td>-8.6115</td>
    </tr>
    <tr>
      <th>22</th>
      <td>Asia Occidental</td>
      <td>3.171070e+05</td>
      <td>-53921.67000</td>
      <td>-5.2620</td>
    </tr>
  </tbody>
</table>
</div>



### 5. CTE + LAG(), ¿Qué modos de envío generan mayores costos logísticos?


```python
query5 = """
WITH costos_envio AS (

    SELECT

        dt.anio,
        dt.mes,
        de."Modo de envío" AS modo_envio,

        SUM(fv."Costo de envío") AS costo_total

    FROM ecomerce_dwh.fact_ventas fv

    JOIN ecomerce_dwh.dim_envio de
        ON fv.id_envio = de.id_envio

    JOIN ecomerce_dwh.dim_tiempo dt
        ON fv.id_tiempo = dt.id_tiempo

    GROUP BY
        dt.anio,
        dt.mes,
        de."Modo de envío"

)

SELECT

    anio,
    mes,
    modo_envio,
    costo_total,

    LAG(costo_total) OVER (
        PARTITION BY modo_envio
        ORDER BY anio, mes
    ) AS costo_mes_anterior,

    costo_total -
    LAG(costo_total) OVER (
        PARTITION BY modo_envio
        ORDER BY anio, mes
    ) AS variacion_mensual

FROM costos_envio

ORDER BY
    modo_envio,
    anio,
    mes;
"""

df = pd.read_sql(query5, engine)
df
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>anio</th>
      <th>mes</th>
      <th>modo_envio</th>
      <th>costo_total</th>
      <th>costo_mes_anterior</th>
      <th>variacion_mensual</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>2012</td>
      <td>1</td>
      <td>Clase estándar</td>
      <td>5309.8480</td>
      <td>NaN</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>1</th>
      <td>2012</td>
      <td>2</td>
      <td>Clase estándar</td>
      <td>4921.2950</td>
      <td>5309.8480</td>
      <td>-388.5530</td>
    </tr>
    <tr>
      <th>2</th>
      <td>2012</td>
      <td>3</td>
      <td>Clase estándar</td>
      <td>5945.5055</td>
      <td>4921.2950</td>
      <td>1024.2105</td>
    </tr>
    <tr>
      <th>3</th>
      <td>2012</td>
      <td>4</td>
      <td>Clase estándar</td>
      <td>5504.4980</td>
      <td>5945.5055</td>
      <td>-441.0075</td>
    </tr>
    <tr>
      <th>4</th>
      <td>2012</td>
      <td>5</td>
      <td>Clase estándar</td>
      <td>7926.0150</td>
      <td>5504.4980</td>
      <td>2421.5170</td>
    </tr>
    <tr>
      <th>...</th>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
    </tr>
    <tr>
      <th>187</th>
      <td>2015</td>
      <td>8</td>
      <td>Urgente</td>
      <td>9474.2140</td>
      <td>6334.5320</td>
      <td>3139.6820</td>
    </tr>
    <tr>
      <th>188</th>
      <td>2015</td>
      <td>9</td>
      <td>Urgente</td>
      <td>13263.0330</td>
      <td>9474.2140</td>
      <td>3788.8190</td>
    </tr>
    <tr>
      <th>189</th>
      <td>2015</td>
      <td>10</td>
      <td>Urgente</td>
      <td>10959.7640</td>
      <td>13263.0330</td>
      <td>-2303.2690</td>
    </tr>
    <tr>
      <th>190</th>
      <td>2015</td>
      <td>11</td>
      <td>Urgente</td>
      <td>12692.3570</td>
      <td>10959.7640</td>
      <td>1732.5930</td>
    </tr>
    <tr>
      <th>191</th>
      <td>2015</td>
      <td>12</td>
      <td>Urgente</td>
      <td>13453.6110</td>
      <td>12692.3570</td>
      <td>761.2540</td>
    </tr>
  </tbody>
</table>
<p>192 rows × 6 columns</p>
</div>


