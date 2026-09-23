import streamlit as st
import pandas as pd
import requests
import json

st.set_page_config(page_title="Tablero de Logística Nordemaq", layout="wide")

st.title("🚛 Tablero de Control de Logística y Pre-entrega")

# URL de la API de Apps Script
API_URL = "https://script.google.com/macros/s/AKfycbzX0ZazhJExig84VGrg0VVEDp4KkM4njfy9P9KiSYk8IOg5-HxWRoen1SQN3L1XJsdt1g/exec"

@st.cache_data(ttl=60)
def load_data():
    res = requests.get(API_URL, allow_redirects=True)
    
    try:
        data_json = res.json()
    except Exception:
        data_json = json.loads(res.text)

    # Convertir a DataFrame la matriz de datos completa
    df_raw = pd.DataFrame(data_json)
    
    # En la planilla, la Fila 2 (índice 1) contiene los nombres reales de las columnas
    header_row_idx = 1
    
    # Obtener nombres de columnas desde la Fila 2
    raw_headers = df_raw.iloc[header_row_idx].astype(str)
    
    # Asegurar nombres de columnas únicos para evitar duplicados
    new_cols = []
    counts = {}
    for idx, col in enumerate(raw_headers):
        col_name = col.strip() if col.strip() != "" and col.strip() != "nan" else f"Columna_{idx+1}"
        if col_name in counts:
            counts[col_name] += 1
            new_cols.append(f"{col_name}_{counts[col_name]}")
        else:
            counts[col_name] = 0
            new_cols.append(col_name)
            
    # Los datos de las unidades comienzan después de la Fila 2 (índice 2 en adelante)
    df = df_raw.iloc[header_row_idx + 1:].copy()
    df.columns = new_cols
    
    # Limpiar columnas vacías
    df = df.dropna(how='all', axis=1)
    
    return df

try:
    df = load_data()

    # Métricas principales
    col1, col2 = st.columns(2)
    col1.metric("Total de Unidades / Registros", len(df))

    # Buscador en tiempo real
    st.sidebar.header("🔍 Buscador de Unidades")
    busqueda = st.sidebar.text_input("Ingresa Chasis, Cliente, Modelo o Ubicación:")

    if busqueda:
        df = df[df.astype(str).apply(lambda row: row.str.contains(busqueda, case=False).any(), axis=1)]

    st.subheader("📋 Lista de Unidades y Seguimiento Logístico")
    st.dataframe(df, use_container_width=True)

except Exception as e:
    st.error(f"Error al procesar la información de la planilla: {e}")
