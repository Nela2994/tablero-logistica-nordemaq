import streamlit as st
import pandas as pd
import requests
import io

st.set_page_config(page_title="Tablero de Logística Nordemaq", layout="wide")

st.title("🚛 Tablero de Control de Logística y Pre-entrega")

# URL de la Web App desplegada en Google Apps Script
API_URL = "https://script.google.com/macros/s/AKfycbzX0ZazhJExig84VGrg0VVEDp4KkM4njfy9P9KiSYk8IOg5-HxWRoen1SQN3L1XJsdt1g/exec"

@st.cache_data(ttl=60)
def load_data():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
    res = requests.get(API_URL, headers=headers, allow_redirects=True)
    
    # Intentar interpretar la respuesta como JSON
    try:
        raw_data = res.json()
        headers_row = raw_data[0]
        rows = raw_data[1:]
        return pd.DataFrame(rows, columns=headers_row)
    except Exception:
        # Manejo de líneas con cantidad variable de columnas o comas internas
        return pd.read_csv(
            io.StringIO(res.text),
            on_bad_lines='skip',
            engine='python'
        )

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
    st.error(f"Error al procesar la información: {e}")
