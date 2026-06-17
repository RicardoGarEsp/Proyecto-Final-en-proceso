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

st.header("1. Productos con mayor rentabilidad")

st.dataframe(rentabilidad, use_container_width=True)

st.bar_chart(
    rentabilidad.set_index("Categoría")["beneficio_total"]
)

# =====================================
# 2. VENTAS VS MÁRGENES
# =====================================

st.header("2. Ventas vs márgenes por categoría")

st.dataframe(ventas_margenes, use_container_width=True)

st.bar_chart(
    ventas_margenes.set_index("Categoría")[["ventas_totales", "beneficio_total"]]
)

# =====================================
# 3. IMPACTO DESCUENTOS
# =====================================

st.header("3. Impacto de los descuentos")

st.dataframe(impacto_descuentos, use_container_width=True)

st.bar_chart(
    impacto_descuentos.set_index("Categoría")
)

# =====================================
# 4. DESEMPEÑO REGIONAL
# =====================================

st.header("4. Desempeño comercial por región")

st.dataframe(desempeno_regiones, use_container_width=True)

st.bar_chart(
    desempeno_regiones.set_index("Región")[["ventas_totales", "beneficio_total"]]
)

# =====================================
# 5. COSTOS LOGÍSTICOS
# =====================================

st.header("5. Costos logísticos por mes")

st.dataframe(costos_logisticos, use_container_width=True)

st.line_chart(
    costos_logisticos.set_index("mes")["costo_total"]
)
