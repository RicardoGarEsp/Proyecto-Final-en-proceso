import pandas as pd

# ==========================================
# CARGAR ARCHIVO
# ==========================================

archivo = "Global Superstore Orders 2016_es-ES.xlsx"

pedidos = pd.read_excel(archivo, sheet_name="Pedidos")
personas = pd.read_excel(archivo, sheet_name="Personas")


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
    DIM_TIEMPO["Fecha de pedido"],
    dayfirst=True
)

DIM_TIEMPO["dia"] = DIM_TIEMPO["Fecha de pedido"].dt.day
DIM_TIEMPO["mes"] = DIM_TIEMPO["Fecha de pedido"].dt.month
DIM_TIEMPO["trimestre"] = DIM_TIEMPO["Fecha de pedido"].dt.quarter
DIM_TIEMPO["anio"] = DIM_TIEMPO["Fecha de pedido"].dt.year

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

with pd.ExcelWriter("Modelo_Estrella_Global_Superstore.xlsx") as writer:
    DIM_CLIENTE.to_excel(writer, sheet_name="DIM_CLIENTE", index=False)
    DIM_PRODUCTO.to_excel(writer, sheet_name="DIM_PRODUCTO", index=False)
    DIM_GEOGRAFIA.to_excel(writer, sheet_name="DIM_GEOGRAFIA", index=False)
    DIM_TIEMPO.to_excel(writer, sheet_name="DIM_TIEMPO", index=False)
    DIM_ENVIO.to_excel(writer, sheet_name="DIM_ENVIO", index=False)
    DIM_PERSONA.to_excel(writer, sheet_name="DIM_PERSONA", index=False)
    FACT_VENTAS.to_excel(writer, sheet_name="FACT_VENTAS", index=False)

print("Modelo estrella generado correctamente.")
