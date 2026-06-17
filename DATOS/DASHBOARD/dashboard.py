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
# 1. RENTABILIDAD
# =====================================

st.header("1. Productos con mayor rentabilidad")

st.bar_chart(
    rentabilidad.set_index("producto")["beneficio_total"]
)

# =====================================
# 2. VENTAS VS MÁRGENES
# =====================================

st.header("2. Ventas vs márgenes por categoría")

st.bar_chart(
    ventas_margenes.set_index("Categoría")[["ventas_totales", "beneficio_total"]]
)

st.line_chart(
    ventas_margenes.set_index("Categoría")["margen"]
)

# =====================================
# 3. DESEMPEÑO REGIONAL
# =====================================

st.header("3. Desempeño por región")

st.bar_chart(
    desempeno_regiones.set_index("Región")[["ventas_totales", "beneficio_total"]]
)

# =====================================
# 4. COSTOS LOGÍSTICOS
# =====================================

st.header("4. Costos logísticos")

costos_logisticos["periodo"] = (
    costos_logisticos["anio"].astype(str) + "-" +
    costos_logisticos["mes"].astype(str)
)

st.line_chart(
    costos_logisticos.set_index("periodo")["costo_total"]
)
