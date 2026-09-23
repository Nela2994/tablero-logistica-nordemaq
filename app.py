import streamlit as st
import pandas as pd

st.set_page_config(page_title="Tablero de Logística Nordemaq", layout="wide")

st.title("🚛 Tablero de Control de Logística y Pre-entrega")

# ID de la planilla
SHEET_ID = "1FQ8MWyE6oiRwmL9bsyHRcYYM1hE0VbiRC6QEQHCuOo6"
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv"

@st.cache_data(ttl=60)
def load_data():
    return pd.read_csv(SHEET_URL)

try:
    df = load_data()

    # Métricas principales
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Registros", len(df))
    
    # Menú lateral de filtros
    st.sidebar.header("🔍 Filtros de Búsqueda")
    
    # Buscador general por texto (Chasis, Cliente, Modelo)
    busqueda = st.sidebar.text_input("Buscar por Chasis, Cliente o Modelo:")
    if busqueda:
        df = df[df.astype(str).apply(lambda row: row.str.contains(busqueda, case=False).any(), axis=1)]

    st.subheader("📋 Unidades y Seguimiento Logístico")
    st.dataframe(df, use_container_width=True)

except Exception as e:
    st.error(f"Error al conectar con la planilla: {e}")
    st.info("Asegúrate de publicar la planilla en la web (Archivo > Compartir > Publicar en la web).")
