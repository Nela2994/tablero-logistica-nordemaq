import streamlit as st
import pandas as pd
import requests
import json

st.set_page_config(page_title="Tablero de Logística Nordemaq", layout="wide")

st.title("🚛 Tablero de Control y Alertas Logísticas")

API_URL = "https://script.google.com/macros/s/AKfycbzX0ZazhJExig84VGrg0VVEDp4KkM4njfy9P9KiSYk8IOg5-HxWRoen1SQN3L1XJsdt1g/exec"

@st.cache_data(ttl=60)
def load_data():
    res = requests.get(API_URL, allow_redirects=True)
    try:
        data_json = res.json()
    except Exception:
        data_json = json.loads(res.text)

    df_raw = pd.DataFrame(data_json)
    
    # Encabezados reales en Fila 2 (índice 1)
    header_row_idx = 1
    raw_headers = df_raw.iloc[header_row_idx].astype(str)
    
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
            
    df = df_raw.iloc[header_row_idx + 1:].copy()
    df.columns = new_cols
    df = df.dropna(how='all', axis=1)
    
    df.reset_index(drop=True, inplace=True)
    df.index = df.index + 1
    
    return df

try:
    df = load_data()

    # Identificar nombres de columnas clave (o asignar por posición de índice si difieren)
    col_cliente = [c for c in df.columns if "Cliente" in c]
    col_cliente = col_cliente[0] if col_cliente else df.columns[3]
    
    # Asignaciones (Columna AY aprox.) y Pre-entrega (Columna AZ aprox.)
    # Se busca por nombre parcial o se toma la última/penúltima columna
    col_asignacion = [c for c in df.columns if "Asignaci" in c or "ASIGNACI" in c]
    col_asignacion = col_asignacion[0] if col_asignacion else df.columns[-2]

    col_preentrega = [c for c in df.columns if "Pre" in c or "PRE" in c or "Entrega" in c]
    col_preentrega = col_preentrega[0] if col_preentrega else df.columns[-1]

    # --- LÓGICA DE ALERTAS ---
    
    # 1. Alerta Clientes Nuevos Sin Asignar
    # Tiene Cliente registrado pero la Asignación está vacía, guion o contiene 'pend'
    cond_cliente_existe = df[col_cliente].astype(str).str.strip().ne("") & df[col_cliente].astype(str).str.strip().ne("-") & df[col_cliente].astype(str).str.strip().ne("nan")
    cond_sin_asignar = df[col_asignacion].astype(str).str.strip().eq("") | df[col_asignacion].astype(str).str.strip().eq("-") | df[col_asignacion].astype(str).str.lower().str.contains("pend|a asign|sin", na=False)
    
    df_sin_asignar = df[cond_cliente_existe & cond_sin_asignar]

    # 2. Alerta Pre-entregas Listas para Logística
    cond_preentrega_lista = df[col_preentrega].astype(str).str.lower().str.contains("finaliz|list|ok|terminad|complet", na=False)
    df_preentrega_lista = df[cond_preentrega_lista]

    # --- TARJETAS SUPERIORES (KPIs) ---
    col1, col2, col3 = st.columns(3)
    col1.metric("Total de Registros Cargados", len(df))
    col2.metric("⚠️ Novedades: Clientes Sin Asignar", len(df_sin_asignar))
    col3.metric("✅ Listos para Salida / Logística", len(df_preentrega_lista))

    st.markdown("---")

    # --- SECCIÓN DE ALERTAS DESTACADAS ---
    if len(df_sin_asignar) > 0:
        st.error(f"🚨 **¡ATENCIÓN! HAY {len(df_sin_asignar)} UNIDADES CON CLIENTE NUEVO PENDIENTES DE ASIGNACIÓN**")
        with st.expander("👉 Haz clic aquí para ver la lista de equipos a coordinar urgente", expanded=True):
            st.dataframe(df_sin_asignar, use_container_width=True)

    if len(df_preentrega_lista) > 0:
        st.success(f"🎉 **¡PRE-ENTREGA FINALIZADA! HAY {len(df_preentrega_lista)} EQUIPOS LISTOS PARA PLANIFICAR LOGÍSTICA**")
        with st.expander("👉 Haz clic aquí para ver los equipos listos para coordinar transporte/flete", expanded=False):
            st.dataframe(df_preentrega_lista, use_container_width=True)

    st.markdown("---")

    # --- FILTROS Y TABLA GENERAL ---
    st.sidebar.header("🔍 Filtros de Gestión")
    modo_vista = st.sidebar.radio("Ver en tabla:", ["Todas las Unidades", "Solo Pendientes de Asignar", "Solo Listos para Salida"])

    busqueda = st.sidebar.text_input("Buscar Chasis, Cliente, Modelo o Ubicación:")

    df_mostrar = df.copy()

    if modo_vista == "Solo Pendientes de Asignar":
        df_mostrar = df_sin_asignar
    elif modo_vista == "Solo Listos para Salida":
        df_mostrar = df_preentrega_lista

    if busqueda:
        df_mostrar = df_mostrar[df_mostrar.astype(str).apply(lambda row: row.str.contains(busqueda, case=False).any(), axis=1)]

    st.subheader(f"📋 Vista General ({modo_vista})")
    st.dataframe(df_mostrar, use_container_width=True)

except Exception as e:
    st.error(f"Error al procesar las alertas logísticas: {e}")
