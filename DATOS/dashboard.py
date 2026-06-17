#!/usr/bin/env python
# coding: utf-8

# In[5]:


import streamlit as st
import pandas as pd

# =====================================
# CONFIGURACIÓN DE LA PÁGINA
# =====================================

st.set_page_config(
    page_title="Dashboard Global Superstore",
    layout="wide"
)

st.title("📊 Dashboard Global Superstore")

# =====================================
# LEER ARCHIVO EXCEL
# =====================================

archivo = "querys.xlsx"

rentabilidad = pd.read_excel(
    archivo,
    sheet_name="Rentabilidad_Productos"
)

ventas_margenes = pd.read_excel(
    archivo,
    sheet_name="Ventas_vs_Margenes"
)

impacto_descuentos = pd.read_excel(
    archivo,
    sheet_name="Impacto_Descuentos"
)

desempeno_regiones = pd.read_excel(
    archivo,
    sheet_name="Desempeno_Regiones"
)

costos_logisticos = pd.read_excel(
    archivo,
    sheet_name="Costos_Logisticos"
)

# =====================================
# DASHBOARD
# =====================================

st.header("1. Productos con mayor rentabilidad")
st.dataframe(rentabilidad, use_container_width=True)

st.header("2. Categorías con mayores ventas y márgenes")
st.dataframe(ventas_margenes, use_container_width=True)

st.header("3. Impacto de los descuentos en el beneficio")
st.dataframe(impacto_descuentos, use_container_width=True)

st.header("4. Desempeño comercial por región")
st.dataframe(desempeno_regiones, use_container_width=True)

st.header("5. Costos logísticos por modo de envío")
st.dataframe(costos_logisticos, use_container_width=True)


# In[ ]:




