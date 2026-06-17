import streamlit as st
import pandas as pd
from pathlib import Path

# =====================================
# CONFIGURACIÓN
# =====================================

st.set_page_config(
    page_title="Dashboard Global Superstore",
    layout="wide"
)

st.title("📊 Dashboard Global Superstore")

# =====================================
# CARGA DE DATOS
# =====================================

BASE_DIR = Path(__file__).parent
archivo = BASE_DIR / "query.xlsx"

rentabilidad = pd.read_excel(archivo, sheet_name="Rentabilidad_Productos")
ventas_margenes = pd.read_excel(archivo, sheet_name="Ventas_vs_Margenes")
impacto_descuentos = pd.read_excel(archivo, sheet_name="Impacto_Descuentos")
desempeno_regiones = pd.read_excel(archivo, sheet_name="Desempeno_Regiones")
costos_logisticos = pd.read_excel(archivo, sheet_name="Costos_Logisticos")

# =====================================
# 1. RENTABILIDAD DE PRODUCTOS
# =====================================

st.header("1. Rentabilidad de productos")

st.dataframe(rentabilidad, use_container_width=True)

st.bar_chart(
    rentabilidad.set_index("producto")["beneficio_total"]
)

st.write("Ranking de productos:")
st.dataframe(rentabilidad[["producto", "ranking"]], use_container_width=True)

# =====================================
# 2. VENTAS VS MÁRGENES
# =====================================

st.header("2. Ventas vs Márgenes por categoría")

st.dataframe(ventas_margenes, use_container_width=True)

st.bar_chart(
    ventas_margenes.set_index("Categoría")[["ventas_totales", "beneficio_total"]]
)

st.line_chart(
    ventas_margenes.set_index("Categoría")["margen"]
)

st.write("Promedio de ventas:")
st.bar_chart(
    ventas_margenes.set_index("Categoría")["promedio_ventas"]
)

# =====================================
# 3. IMPACTO DE DESCUENTOS
# =====================================

st.header("3. Impacto de los descuentos")

st.dataframe(impacto_descuentos, use_container_width=True)

st.bar_chart(
    impacto_descuentos.set_index("pedidos_sin_descuento")[
        ["beneficio_promedio_sin_descuento", "beneficio_promedio_con_descuento"]
    ]
)

# =====================================
# 4. DESEMPEÑO REGIONAL
# =====================================

st.header("4. Desempeño por región")

st.dataframe(desempeno_regiones, use_container_width=True)

st.bar_chart(
    desempeno_regiones.set_index("Región")[["ventas_totales", "beneficio_total"]]
)

st.bar_chart(
    desempeno_regiones.set_index("Región")["mediana_beneficio"]
)

# =====================================
# 5. COSTOS LOGÍSTICOS
# =====================================

st.header("5. Costos logísticos")

st.dataframe(costos_logisticos, use_container_width=True)

# Crear columna de fecha simple
costos_logisticos["periodo"] = (
    costos_logisticos["anio"].astype(str) + "-" +
    costos_logisticos["mes"].astype(str)
)

st.line_chart(
    costos_logisticos.set_index("periodo")["costo_total"]
)

st.line_chart(
    costos_logisticos.set_index("periodo")["variacion_mensual"]
)
