import streamlit as st
import pandas as pd

st.set_page_config(page_title="Tablero de Logística Nordemaq", layout="wide")

st.title("🚛 Tablero de Control de Logística y Pre-entrega")

# ID exacto de tu planilla publicado vía Google Visualization API
SHEET_ID = "1FQ8MWyE6oiRwmL9bsyHRcYYM1hE0VbiRC6QEQHCuOo6"
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv"

@st.cache_data(ttl=60)
def load_data():
    return pd.read_csv(SHEET_URL)

try:
    df = load_data()

    # Métricas superiores
    col1, col2 = st.columns(2)
    col1.metric("Total de Registros Cargados", len(df))

    # Buscador en tiempo real
    st.sidebar.header("🔍 Buscador de Unidades")
    busqueda = st.sidebar.text_input("Ingresa Chasis, Cliente, Modelo o Ubicación:")

    if busqueda:
        df = df[df.astype(str).apply(lambda row: row.str.contains(busqueda, case=False).any(), axis=1)]

    st.subheader("📋 Lista de Unidades y Seguimiento Logístico")
    st.dataframe(df, use_container_width=True)

except Exception as e:
    st.error(f"Error de conexión: {e}")
