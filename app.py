import streamlit as st
import pandas as pd

st.set_page_config(page_title="Tablero de Logística Nordemaq", layout="wide")

st.title("🚛 Tablero de Control de Logística y Pre-entrega")

# Enlace directo de exportación con la URL exacta del documento y la pestaña gid=0
SHEET_URL = "https://docs.google.com/spreadsheets/d/1FQ8MWyE6oiRwmL9bsyHRcYYM1hE0VbiRC6QEQHCuOo6o/export?format=csv&gid=0"

@st.cache_data(ttl=60)
def load_data():
    return pd.read_csv(SHEET_URL)

try:
    df = load_data()

    # Tarjetas de métricas
    col1, col2 = st.columns(2)
    col1.metric("Total de Unidades / Registros", len(df))

    # Filtro dinámico en la barra lateral
    st.sidebar.header("🔍 Buscador de Unidades")
    busqueda = st.sidebar.text_input("Ingresa Chasis, Cliente, Modelo o Ubicación:")

    if busqueda:
        df = df[df.astype(str).apply(lambda row: row.str.contains(busqueda, case=False).any(), axis=1)]

    st.subheader("📋 Lista de Unidades y Seguimiento Logístico")
    st.dataframe(df, use_container_width=True)

except Exception as e:
    st.error(f"Error al conectar con la planilla: {e}")
