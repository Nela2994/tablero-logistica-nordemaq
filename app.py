import streamlit as st
import pandas as pd

st.set_page_config(page_title="Tablero de Logística Nordemaq", layout="wide")

st.title("🚛 Tablero de Control de Logística y Pre-entrega")

# Leemos la versión HTML publicada que NO requiere autenticación corporativa
PUBHTML_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vR8uCPac3EOcielt-jqFbSPIrFdCCZcLGQ63fiXL2zxJ44sGHJtui42Vy_9qkOt0JbfySlRwlQWxoMg/pubhtml"

@st.cache_data(ttl=60)
def load_data():
    # Lee directamente la tabla HTML de Google Sheets
    tables = pd.read_html(PUBHTML_URL, header=1)
    df = tables[0]
    # Limpiamos columnas vacías o no deseadas
    df = df.dropna(how="all", axis=1)
    return df

try:
    df = load_data()

    # Métricas principales
    col1, col2 = st.columns(2)
    col1.metric("Total de Registros Cargados", len(df))

    # Buscador en la barra lateral
    st.sidebar.header("🔍 Buscador de Unidades")
    busqueda = st.sidebar.text_input("Ingresa Chasis, Cliente, Modelo o Ubicación:")

    if busqueda:
        df = df[df.astype(str).apply(lambda row: row.str.contains(busqueda, case=False).any(), axis=1)]

    st.subheader("📋 Lista de Unidades y Seguimiento Logístico")
    st.dataframe(df, use_container_width=True)

except Exception as e:
    st.error(f"Error al conectar con la planilla: {e}")
