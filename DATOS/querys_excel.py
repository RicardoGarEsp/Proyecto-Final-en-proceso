#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Dashboard Global Superstore",
    layout="wide"
)

st.title("📊 Dashboard Global Superstore")

# Leer archivo
archivo = "querys.xlsx"

top_clientes = pd.read_excel(archivo, sheet_name="Top_Clientes")
promedio = pd.read_excel(archivo, sheet_name="Promedio_Movil")
descuentos = pd.read_excel(archivo, sheet_name="Descuentos")
mediana = pd.read_excel(archivo, sheet_name="Mediana_Ventas")
costos = pd.read_excel(archivo, sheet_name="Ventas_Mensuales")

st.header("Top Clientes")
st.dataframe(top_clientes)

st.header("Promedio móvil")
st.line_chart(
    promedio.set_index("fecha")["ventas_dia"]
)

st.header("Descuentos")
st.dataframe(descuentos)

st.header("Mediana por categoría")
st.bar_chart(
    mediana.set_index("Categoría")["mediana_ventas"]
)

st.header("Costos logísticos")
st.line_chart(
    costos.set_index("mes")["costo_total"]
)

