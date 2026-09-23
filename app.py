import streamlit as st
import pandas as pd
import requests
import io

st.set_page_config(page_title="Tablero de Logística Nordemaq", layout="wide")

st.title("🚛 Tablero de Control de Logística y Pre-entrega")

# Enlace publicado directamente desde la web
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vR8uCPac3EOcielt-jqFbSPIrFdCCZcLGQ63fiXL2zxJ44sGHJtui42Vy_9qkOt0JbfySlRwlQWxoMg/pub?output=csv"

@st.cache_data(ttl=60)
def load_data():
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(SHEET_URL, headers=headers)
    if response.status_code == 200:
        return pd.read_csv(io.StringIO(response.text))
    else:
        # Intento secundario con enlace alternativo gviz
        alt_url = "https://docs.google.com/spreadsheets/d/1FQ8MwYE6oiRwmL9bsyHRcYYM1hE0VbiRC6QEQHCuOo6o/gviz/tq?tqx=out:csv"
        return pd.read_csv(alt_url)

try:
    df = load_data()

    # Métricas y resumen superior
    col1, col2 = st.columns(2)
    col1.metric("Total de Unidades / Registros", len(df))

    # Buscador en la barra lateral
    st.sidebar.header("🔍 Buscador de Unidades")
    busqueda = st.sidebar.text_input("Ingresa Chasis, Cliente, Modelo o Ubicación:")

    if busqueda:
        df = df[df.astype(str).apply(lambda row: row.str.contains(busqueda, case=False).any(), axis=1)]

    st.subheader("📋 Lista de Unidades y Seguimiento Logístico")
    st.dataframe(df, use_container_width=True)

except Exception as e:
    st.error(f"Error al conectar con la planilla: {e}")
