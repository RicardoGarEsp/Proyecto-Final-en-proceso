import streamlit as st
import pandas as pd
import altair as alt
from pathlib import Path

# =====================================
# CONFIGURACIÓN
# =====================================
st.set_page_config(page_title="Dashboard Global Superstore", layout="wide")

st.title("📊 Dashboard Global Superstore")

st.markdown("""
Dashboard analítico para evaluar ventas, rentabilidad, desempeño regional y eficiencia logística.
Se enfoca en identificar patrones, riesgos y oportunidades de optimización del negocio.
""")

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
# KPIs GENERALES
# =====================================
st.subheader("📌 Indicadores clave del negocio")

col1, col2, col3 = st.columns(3)

total_ventas = ventas_margenes["ventas_totales"].sum()
total_beneficio = ventas_margenes["beneficio_total"].sum()
margen_global = total_beneficio / total_ventas

col1.metric("💰 Ventas totales", f"{total_ventas:,.0f}")
col2.metric("📈 Beneficio total", f"{total_beneficio:,.0f}")
col3.metric("📊 Margen global", f"{margen_global:.2%}")

st.info("""
El negocio muestra un margen global estable. Sin embargo, la rentabilidad depende fuertemente de ciertas categorías y regiones, lo que implica riesgo de concentración.
""")

st.divider()

# =====================================
# 1. RENTABILIDAD
# =====================================
st.subheader("1. 🏆 Productos más rentables")

st.info("""
Los productos más rentables son principalmente de alto valor unitario (tecnología y equipos corporativos), lo que indica un modelo de negocio B2B y de ticket alto.
""")

top_prod = rentabilidad.sort_values("beneficio_total", ascending=True)

chart_prod = alt.Chart(top_prod).mark_bar().encode(
    x=alt.X("beneficio_total:Q", title="Beneficio total"),
    y=alt.Y("producto:N", sort="-x", title="Producto"),
    tooltip=["producto", "beneficio_total"]
).properties(height=400)

st.altair_chart(chart_prod, use_container_width=True)

# =====================================
# 2. VENTAS VS MÁRGENES
# =====================================
st.subheader("2. 📦 Ventas vs Márgenes por categoría")

st.info("""
Tecnología lidera en ventas y beneficio, mientras que mobiliario presenta una eficiencia significativamente menor, sugiriendo problemas de costos o descuentos.
""")

base = ventas_margenes.melt(
    id_vars="Categoría",
    value_vars=["ventas_totales", "beneficio_total"],
    var_name="Indicador",
    value_name="Valor"
)

chart_cat = alt.Chart(base).mark_bar().encode(
    x=alt.X("Categoría:N"),
    xOffset="Indicador:N",
    y="Valor:Q",
    color="Indicador:N",
    tooltip=["Categoría", "Indicador", "Valor"]
).properties(height=400)

st.altair_chart(chart_cat, use_container_width=True)

chart_margin = alt.Chart(ventas_margenes).mark_line(point=True).encode(
    x="Categoría:N",
    y="margen:Q",
    tooltip=["Categoría", "margen"]
).properties(height=300)

st.altair_chart(chart_margin, use_container_width=True)

# =====================================
# 3. DESEMPEÑO REGIONAL
# =====================================
st.subheader("3. 🌎 Desempeño por región")

st.info("""
Europa Occidental y Asia Oriental concentran la mayor rentabilidad. En contraste, varias regiones muestran baja eficiencia o incluso pérdidas, lo que indica expansión no optimizada.
""")

chart_region = alt.Chart(desempeno_regiones).mark_bar().encode(
    x="Región:N",
    y="ventas_totales:Q",
    color="beneficio_total:Q",
    tooltip=["Región", "ventas_totales", "beneficio_total"]
).properties(height=400)

st.altair_chart(chart_region, use_container_width=True)

# =====================================
# 4. COSTOS LOGÍSTICOS (MEJORADO)
# =====================================
st.subheader("4. 🚚 Evolución de costos logísticos")

st.info("""
Se observa un crecimiento sostenido de los costos logísticos, especialmente en clase estándar. El sistema presenta alta volatilidad mensual, lo que sugiere ineficiencia en planificación de capacidad.
""")

# Orden temporal correcto
costos_logisticos["periodo"] = (
    costos_logisticos["anio"].astype(str) + "-" +
    costos_logisticos["mes"].astype(str)
)

# mejor orden
costos_logisticos = costos_logisticos.sort_values(["anio", "mes"])

# GRÁFICO MEJORADO: separado por modo de envío
chart_costos = alt.Chart(costos_logisticos).mark_line(point=True).encode(
    x=alt.X("periodo:N", title="Periodo"),
    y=alt.Y("costo_total:Q", title="Costo total"),
    color=alt.Color("modo_envio:N", title="Tipo de envío"),
    tooltip=["anio", "mes", "modo_envio", "costo_total", "variacion_mensual"]
).properties(height=450)

st.altair_chart(chart_costos, use_container_width=True)

st.info("""
Interpretación:
- Clase estándar domina el costo total
- Urgente genera picos de alta volatilidad
- Segunda clase actúa como equilibrio operativo
- El sistema muestra crecimiento estructural de costos con variabilidad significativa
""")
