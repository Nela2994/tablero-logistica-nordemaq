import streamlit as st
import pandas as pd

# Configuración de la página
st.set_page_config(page_title="Tablero de Logística Nordemaq", layout="wide")

st.title("🚛 Tablero de Control de Logística y Pre-entrega")

# Cargar la base de datos desde Google Sheets (publicada como CSV)
# Reemplaza esta URL con el enlace de exportación CSV de tu Google Sheet
SHEET_URL = "https://docs.google.com/spreadsheets/d/1Q9vXFyG-o04uWiQoxslutAMGzg4wlzfMDrMM6INoQ54/export?format=csv"

@st.cache_data(ttl=60)
def load_data():
    df = pd.read_csv(SHEET_URL)
    return df

try:
    df = load_data()

    # Métricas / Tarjetas rápidas
    col1, col2, col3 = st.columns(3)
    
    total_unidades = len(df)
    col1.metric("Total de Unidades", total_unidades)
    
    # Filtro dinámico en la barra lateral
    st.sidebar.header("Filtros de Búsqueda")
    
    if "UBICACIÓN" in df.columns:
        ubicaciones = ["Todas"] + list(df["UBICACIÓN"].dropna().unique())
        ubicacion_sel = st.sidebar.selectbox("Filtrar por Ubicación", ubicaciones)
        if ubicacion_sel != "Todas":
            df = df[df["UBICACIÓN"] == ubicacion_sel]

    if "MARCA" in df.columns:
        marcas = ["Todas"] + list(df["MARCA"].dropna().unique())
        marca_sel = st.sidebar.selectbox("Filtrar por Marca", marcas)
        if marca_sel != "Todas":
            df = df[df["MARCA"] == marca_sel]

    st.subheader("📋 Lista de Unidades y Estados")
    st.dataframe(df, use_container_width=True)

except Exception as e:
    st.info("Cargando base de datos o configurando conexión...")
    st.write("Asegúrate de que la planilla esté compartida correctamente.")
