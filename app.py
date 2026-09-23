import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="Tablero de Logística Nordemaq", layout="wide")

st.title("🚛 Tablero de Control de Logística y Pre-entrega")

# URL de la API de Apps Script de tu jefe
API_URL = "https://script.google.com/macros/s/AKfycbzX0ZazhJExig84VGrg0VVEDp4KkM4njfy9P9KiSYk8IOg5-HxWRoen1SQN3L1XJsdt1g/exec"

@st.cache_data(ttl=60)
def load_data():
    # allow_redirects=True le permite a Python seguir la redirección de Google Apps Script
    res = requests.get(API_URL, allow_redirects=True)
    raw_data = res.json()
    
    # Encabezados en la primera fila y datos en las siguientes
    headers = raw_data[0]
    rows = raw_data[1:]
    
    df = pd.DataFrame(rows, columns=headers)
    return df

try:
    df = load_data()

    # Indicadores superiores
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
    st.error(f"Error al procesar la información: {e}")
