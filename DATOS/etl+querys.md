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

### 1. CTE + Ranking simple


```python
query = """
WITH ventas_cliente AS (

    SELECT
        dc."Nombre de cliente" AS cliente,
        SUM(fv."Ventas") AS total_ventas

    FROM ecomerce_dwh.fact_ventas fv
    JOIN ecomerce_dwh.dim_cliente dc
        ON fv."ID de cliente" = dc."ID de cliente"

    GROUP BY dc."Nombre de cliente"

)

SELECT
    cliente,
    total_ventas,
    RANK() OVER (ORDER BY total_ventas DESC) AS ranking

FROM ventas_cliente
ORDER BY ranking
LIMIT 10;
"""

df = pd.read_sql(query, engine)

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
      <th>cliente</th>
      <th>total_ventas</th>
      <th>ranking</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>Tom Ashbrook</td>
      <td>40488.07080</td>
      <td>1</td>
    </tr>
    <tr>
      <th>1</th>
      <td>Tamara Chand</td>
      <td>37457.33300</td>
      <td>2</td>
    </tr>
    <tr>
      <th>2</th>
      <td>Greg Tran</td>
      <td>35550.95428</td>
      <td>3</td>
    </tr>
    <tr>
      <th>3</th>
      <td>Christopher Conant</td>
      <td>35187.07640</td>
      <td>4</td>
    </tr>
    <tr>
      <th>4</th>
      <td>Sean Miller</td>
      <td>35170.93296</td>
      <td>5</td>
    </tr>
    <tr>
      <th>5</th>
      <td>Bart Watters</td>
      <td>32310.44650</td>
      <td>6</td>
    </tr>
    <tr>
      <th>6</th>
      <td>Natalie Fritzler</td>
      <td>31781.25850</td>
      <td>7</td>
    </tr>
    <tr>
      <th>7</th>
      <td>Fred Hopkins</td>
      <td>30400.67452</td>
      <td>8</td>
    </tr>
    <tr>
      <th>8</th>
      <td>Jane Waco</td>
      <td>30288.45030</td>
      <td>9</td>
    </tr>
    <tr>
      <th>9</th>
      <td>Hunter Lopez</td>
      <td>30243.56658</td>
      <td>10</td>
    </tr>
  </tbody>
</table>
</div>



### 2. Window Function — Promedio móvil de ventas (7 días)


```python
query = """
WITH ventas_dia AS (

    SELECT
        dt."Fecha de pedido" AS fecha,
        SUM(fv."Ventas") AS ventas_dia

    FROM ecomerce_dwh.fact_ventas fv
    JOIN ecomerce_dwh.dim_tiempo dt
        ON fv.id_tiempo = dt.id_tiempo

    GROUP BY dt."Fecha de pedido"

)

SELECT
    fecha,
    ventas_dia,

    AVG(ventas_dia) OVER (
        ORDER BY fecha
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ) AS promedio_movil_7_dias

FROM ventas_dia
ORDER BY fecha;
"""

df = pd.read_sql(query, engine)
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
      <th>fecha</th>
      <th>ventas_dia</th>
      <th>promedio_movil_7_dias</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>2012-01-01</td>
      <td>808.56300</td>
      <td>808.563000</td>
    </tr>
    <tr>
      <th>1</th>
      <td>2012-01-02</td>
      <td>314.22000</td>
      <td>561.391500</td>
    </tr>
    <tr>
      <th>2</th>
      <td>2012-01-03</td>
      <td>4503.53720</td>
      <td>1875.440067</td>
    </tr>
    <tr>
      <th>3</th>
      <td>2012-01-04</td>
      <td>2808.87024</td>
      <td>2108.797610</td>
    </tr>
    <tr>
      <th>4</th>
      <td>2012-01-05</td>
      <td>3662.31000</td>
      <td>2419.500088</td>
    </tr>
    <tr>
      <th>...</th>
      <td>...</td>
      <td>...</td>
      <td>...</td>
    </tr>
    <tr>
      <th>1425</th>
      <td>2015-12-27</td>
      <td>13421.26376</td>
      <td>17431.658106</td>
    </tr>
    <tr>
      <th>1426</th>
      <td>2015-12-28</td>
      <td>1647.17400</td>
      <td>17610.469249</td>
    </tr>
    <tr>
      <th>1427</th>
      <td>2015-12-29</td>
      <td>25109.28878</td>
      <td>19718.102646</td>
    </tr>
    <tr>
      <th>1428</th>
      <td>2015-12-30</td>
      <td>16831.61480</td>
      <td>18108.899403</td>
    </tr>
    <tr>
      <th>1429</th>
      <td>2015-12-31</td>
      <td>13257.95430</td>
      <td>17077.190774</td>
    </tr>
  </tbody>
</table>
<p>1430 rows × 3 columns</p>
</div>



### 3. COUNT FILTER — Pedidos con y sin descuento por categoría


```python
query = """
SELECT

    dp."Categoría",

    COUNT(*) AS total_pedidos,

    COUNT(*) FILTER (
        WHERE fv."Descuento" > 0
    ) AS pedidos_con_descuento,

    COUNT(*) FILTER (
        WHERE fv."Descuento" = 0
    ) AS pedidos_sin_descuento

FROM ecomerce_dwh.fact_ventas fv

JOIN ecomerce_dwh.dim_producto dp
    ON fv."ID de producto" = dp."ID de producto"

GROUP BY dp."Categoría"

ORDER BY total_pedidos DESC;
"""

df = pd.read_sql(query, engine)
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
      <th>total_pedidos</th>
      <th>pedidos_con_descuento</th>
      <th>pedidos_sin_descuento</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>Material de oficina</td>
      <td>31289</td>
      <td>12073</td>
      <td>19216</td>
    </tr>
    <tr>
      <th>1</th>
      <td>Tecnología</td>
      <td>10141</td>
      <td>4837</td>
      <td>5304</td>
    </tr>
    <tr>
      <th>2</th>
      <td>Mobiliario</td>
      <td>9860</td>
      <td>5371</td>
      <td>4489</td>
    </tr>
  </tbody>
</table>
</div>



### 4. PERCENTILE_CONT — Mediana de ventas por categoría


```python
query = """
SELECT

    dp."Categoría",

    PERCENTILE_CONT(0.5)
    WITHIN GROUP (
        ORDER BY fv."Ventas"
    ) AS mediana_ventas

FROM ecomerce_dwh.fact_ventas fv

JOIN ecomerce_dwh.dim_producto dp
    ON fv."ID de producto" = dp."ID de producto"

GROUP BY dp."Categoría"

ORDER BY mediana_ventas DESC;
"""

df = pd.read_sql(query, engine)
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
      <th>mediana_ventas</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>Tecnología</td>
      <td>260.3400</td>
    </tr>
    <tr>
      <th>1</th>
      <td>Mobiliario</td>
      <td>220.5903</td>
    </tr>
    <tr>
      <th>2</th>
      <td>Material de oficina</td>
      <td>46.3440</td>
    </tr>
  </tbody>
</table>
</div>



### 5. CTE + LAG() — Comparación de ventas mensuales


```python
query = """
WITH ventas_mes AS (

    SELECT

        dt.anio,
        dt.mes,

        SUM(fv."Ventas") AS ventas

    FROM ecomerce_dwh.fact_ventas fv

    JOIN ecomerce_dwh.dim_tiempo dt
        ON fv.id_tiempo = dt.id_tiempo

    GROUP BY
        dt.anio,
        dt.mes

)

SELECT

    anio,
    mes,
    ventas,

    LAG(ventas) OVER (
        ORDER BY anio, mes
    ) AS ventas_mes_anterior,

    ventas -
    LAG(ventas) OVER (
        ORDER BY anio, mes
    ) AS diferencia

FROM ventas_mes

ORDER BY anio, mes;
"""

df = pd.read_sql(query, engine)
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
      <th>ventas</th>
      <th>ventas_mes_anterior</th>
      <th>diferencia</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>2012</td>
      <td>1</td>
      <td>98898.48886</td>
      <td>NaN</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>1</th>
      <td>2012</td>
      <td>2</td>
      <td>103717.92328</td>
      <td>98898.48886</td>
      <td>4819.43442</td>
    </tr>
    <tr>
      <th>2</th>
      <td>2012</td>
      <td>3</td>
      <td>135746.40206</td>
      <td>103717.92328</td>
      <td>32028.47878</td>
    </tr>
    <tr>
      <th>3</th>
      <td>2012</td>
      <td>4</td>
      <td>114332.96318</td>
      <td>135746.40206</td>
      <td>-21413.43888</td>
    </tr>
    <tr>
      <th>4</th>
      <td>2012</td>
      <td>5</td>
      <td>158228.32880</td>
      <td>114332.96318</td>
      <td>43895.36562</td>
    </tr>
    <tr>
      <th>5</th>
      <td>2012</td>
      <td>6</td>
      <td>207571.54352</td>
      <td>158228.32880</td>
      <td>49343.21472</td>
    </tr>
    <tr>
      <th>6</th>
      <td>2012</td>
      <td>7</td>
      <td>118434.88462</td>
      <td>207571.54352</td>
      <td>-89136.65890</td>
    </tr>
    <tr>
      <th>7</th>
      <td>2012</td>
      <td>8</td>
      <td>208063.28372</td>
      <td>118434.88462</td>
      <td>89628.39910</td>
    </tr>
    <tr>
      <th>8</th>
      <td>2012</td>
      <td>9</td>
      <td>284587.74846</td>
      <td>208063.28372</td>
      <td>76524.46474</td>
    </tr>
    <tr>
      <th>9</th>
      <td>2012</td>
      <td>10</td>
      <td>216114.56748</td>
      <td>284587.74846</td>
      <td>-68473.18098</td>
    </tr>
    <tr>
      <th>10</th>
      <td>2012</td>
      <td>11</td>
      <td>293947.35216</td>
      <td>216114.56748</td>
      <td>77832.78468</td>
    </tr>
    <tr>
      <th>11</th>
      <td>2012</td>
      <td>12</td>
      <td>319807.40940</td>
      <td>293947.35216</td>
      <td>25860.05724</td>
    </tr>
    <tr>
      <th>12</th>
      <td>2013</td>
      <td>1</td>
      <td>137435.97514</td>
      <td>319807.40940</td>
      <td>-182371.43426</td>
    </tr>
    <tr>
      <th>13</th>
      <td>2013</td>
      <td>2</td>
      <td>98854.96208</td>
      <td>137435.97514</td>
      <td>-38581.01306</td>
    </tr>
    <tr>
      <th>14</th>
      <td>2013</td>
      <td>3</td>
      <td>163076.77116</td>
      <td>98854.96208</td>
      <td>64221.80908</td>
    </tr>
    <tr>
      <th>15</th>
      <td>2013</td>
      <td>4</td>
      <td>161052.26952</td>
      <td>163076.77116</td>
      <td>-2024.50164</td>
    </tr>
    <tr>
      <th>16</th>
      <td>2013</td>
      <td>5</td>
      <td>208364.89124</td>
      <td>161052.26952</td>
      <td>47312.62172</td>
    </tr>
    <tr>
      <th>17</th>
      <td>2013</td>
      <td>6</td>
      <td>256175.69842</td>
      <td>208364.89124</td>
      <td>47810.80718</td>
    </tr>
    <tr>
      <th>18</th>
      <td>2013</td>
      <td>7</td>
      <td>145236.78512</td>
      <td>256175.69842</td>
      <td>-110938.91330</td>
    </tr>
    <tr>
      <th>19</th>
      <td>2013</td>
      <td>8</td>
      <td>303142.94238</td>
      <td>145236.78512</td>
      <td>157906.15726</td>
    </tr>
    <tr>
      <th>20</th>
      <td>2013</td>
      <td>9</td>
      <td>289389.16564</td>
      <td>303142.94238</td>
      <td>-13753.77674</td>
    </tr>
    <tr>
      <th>21</th>
      <td>2013</td>
      <td>10</td>
      <td>252939.85020</td>
      <td>289389.16564</td>
      <td>-36449.31544</td>
    </tr>
    <tr>
      <th>22</th>
      <td>2013</td>
      <td>11</td>
      <td>323512.41690</td>
      <td>252939.85020</td>
      <td>70572.56670</td>
    </tr>
    <tr>
      <th>23</th>
      <td>2013</td>
      <td>12</td>
      <td>338256.96660</td>
      <td>323512.41690</td>
      <td>14744.54970</td>
    </tr>
    <tr>
      <th>24</th>
      <td>2014</td>
      <td>1</td>
      <td>199185.90738</td>
      <td>338256.96660</td>
      <td>-139071.05922</td>
    </tr>
    <tr>
      <th>25</th>
      <td>2014</td>
      <td>2</td>
      <td>167239.65040</td>
      <td>199185.90738</td>
      <td>-31946.25698</td>
    </tr>
    <tr>
      <th>26</th>
      <td>2014</td>
      <td>3</td>
      <td>198594.03012</td>
      <td>167239.65040</td>
      <td>31354.37972</td>
    </tr>
    <tr>
      <th>27</th>
      <td>2014</td>
      <td>4</td>
      <td>177821.31684</td>
      <td>198594.03012</td>
      <td>-20772.71328</td>
    </tr>
    <tr>
      <th>28</th>
      <td>2014</td>
      <td>5</td>
      <td>260498.56470</td>
      <td>177821.31684</td>
      <td>82677.24786</td>
    </tr>
    <tr>
      <th>29</th>
      <td>2014</td>
      <td>6</td>
      <td>396519.61190</td>
      <td>260498.56470</td>
      <td>136021.04720</td>
    </tr>
    <tr>
      <th>30</th>
      <td>2014</td>
      <td>7</td>
      <td>229928.95200</td>
      <td>396519.61190</td>
      <td>-166590.65990</td>
    </tr>
    <tr>
      <th>31</th>
      <td>2014</td>
      <td>8</td>
      <td>326488.78936</td>
      <td>229928.95200</td>
      <td>96559.83736</td>
    </tr>
    <tr>
      <th>32</th>
      <td>2014</td>
      <td>9</td>
      <td>376619.24568</td>
      <td>326488.78936</td>
      <td>50130.45632</td>
    </tr>
    <tr>
      <th>33</th>
      <td>2014</td>
      <td>10</td>
      <td>293406.64288</td>
      <td>376619.24568</td>
      <td>-83212.60280</td>
    </tr>
    <tr>
      <th>34</th>
      <td>2014</td>
      <td>11</td>
      <td>373989.36010</td>
      <td>293406.64288</td>
      <td>80582.71722</td>
    </tr>
    <tr>
      <th>35</th>
      <td>2014</td>
      <td>12</td>
      <td>405454.37802</td>
      <td>373989.36010</td>
      <td>31465.01792</td>
    </tr>
    <tr>
      <th>36</th>
      <td>2015</td>
      <td>1</td>
      <td>241268.55566</td>
      <td>405454.37802</td>
      <td>-164185.82236</td>
    </tr>
    <tr>
      <th>37</th>
      <td>2015</td>
      <td>2</td>
      <td>184837.35556</td>
      <td>241268.55566</td>
      <td>-56431.20010</td>
    </tr>
    <tr>
      <th>38</th>
      <td>2015</td>
      <td>3</td>
      <td>263100.77262</td>
      <td>184837.35556</td>
      <td>78263.41706</td>
    </tr>
    <tr>
      <th>39</th>
      <td>2015</td>
      <td>4</td>
      <td>242771.86130</td>
      <td>263100.77262</td>
      <td>-20328.91132</td>
    </tr>
    <tr>
      <th>40</th>
      <td>2015</td>
      <td>5</td>
      <td>288401.04614</td>
      <td>242771.86130</td>
      <td>45629.18484</td>
    </tr>
    <tr>
      <th>41</th>
      <td>2015</td>
      <td>6</td>
      <td>401814.06310</td>
      <td>288401.04614</td>
      <td>113413.01696</td>
    </tr>
    <tr>
      <th>42</th>
      <td>2015</td>
      <td>7</td>
      <td>258705.68048</td>
      <td>401814.06310</td>
      <td>-143108.38262</td>
    </tr>
    <tr>
      <th>43</th>
      <td>2015</td>
      <td>8</td>
      <td>456619.94236</td>
      <td>258705.68048</td>
      <td>197914.26188</td>
    </tr>
    <tr>
      <th>44</th>
      <td>2015</td>
      <td>9</td>
      <td>481157.24370</td>
      <td>456619.94236</td>
      <td>24537.30134</td>
    </tr>
    <tr>
      <th>45</th>
      <td>2015</td>
      <td>10</td>
      <td>422766.62916</td>
      <td>481157.24370</td>
      <td>-58390.61454</td>
    </tr>
    <tr>
      <th>46</th>
      <td>2015</td>
      <td>11</td>
      <td>555279.02700</td>
      <td>422766.62916</td>
      <td>132512.39784</td>
    </tr>
    <tr>
      <th>47</th>
      <td>2015</td>
      <td>12</td>
      <td>503143.69348</td>
      <td>555279.02700</td>
      <td>-52135.33352</td>
    </tr>
  </tbody>
</table>
</div>




```python

```
