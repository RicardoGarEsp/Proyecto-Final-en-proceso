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
archivo = BASE_DIR / "querys.xlsx"

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

with st.expander("📋 Ver tabla"):
    st.dataframe(rentabilidad, use_container_width=True)

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

with st.expander("📋 Ver tabla"):
    st.dataframe(ventas_margenes, use_container_width=True)

# =====================================
# 3. IMPACTO DESCUENTOS
# =====================================

st.header("3. Impacto de los descuentos")

st.bar_chart(
    impacto_descuentos.set_index("pedidos_sin_descuento")[
        ["beneficio_promedio_sin_descuento", "beneficio_promedio_con_descuento"]
    ]
)

with st.expander("📋 Ver tabla"):
    st.dataframe(impacto_descuentos, use_container_width=True)

# =====================================
# 4. DESEMPEÑO REGIONAL
# =====================================

st.header("4. Desempeño por región")

st.bar_chart(
    desempeno_regiones.set_index("Región")[["ventas_totales", "beneficio_total"]]
)

with st.expander("📋 Ver tabla"):
    st.dataframe(desempeno_regiones, use_container_width=True)

# =====================================
# 5. COSTOS LOGÍSTICOS
# =====================================

st.header("5. Costos logísticos")

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

with st.expander("📋 Ver tabla"):
    st.dataframe(costos_logisticos, use_container_width=True)
