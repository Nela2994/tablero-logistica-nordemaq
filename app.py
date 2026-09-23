import streamlit as st
import pandas as pd
import requests
import json

st.set_page_config(page_title="Tablero de Logística Nordemaq", layout="wide")

st.title("🚛 Tablero de Control y Alertas Logísticas")

API_URL = "https://script.google.com/macros/s/AKfycbzX0ZazhJExig84VGrg0VVEDp4KkM4njfy9P9KiSYk8IOg5-HxWRoen1SQN3L1XJsdt1g/exec"

@st.cache_data(ttl=20)
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

    # Detección de columnas clave
    col_estado = [c for c in df.columns if "Estado" in c or "ESTADO" in c]
    col_estado = col_estado[0] if col_estado else df.columns[4]

    col_cliente = [c for c in df.columns if "Cliente" in c or "CLIENTE" in c]
    col_cliente = col_cliente[0] if col_cliente else df.columns[3]
    
    # Columna AY (Asignación) y AZ (Pre-entrega)
    col_asignacion = [c for c in df.columns if "Asignaci" in c or "ASIGNACI" in c]
    col_asignacion = col_asignacion[0] if col_asignacion else df.columns[-2]

    col_preentrega = [c for c in df.columns if "Pre" in c or "PRE" in c or "Entrega" in c]
    col_preentrega = col_preentrega[0] if col_preentrega else df.columns[-1]

    # --- LÓGICA BASADA EN FECHAS ---
    
    # Excluir operaciones ya finalizadas/cerradas
    cond_no_finalizada = ~df[col_estado].astype(str).str.lower().str.contains("8.7|finaliz|cerrad|complet", na=False)
    
    # Tiene Cliente cargado
    cond_tiene_cliente = df[col_cliente].astype(str).str.strip().ne("") & df[col_cliente].astype(str).str.strip().ne("-") & df[col_cliente].astype(str).str.strip().ne("nan")
    
    # Asignación SIN FECHA (vacía, con guion o sin datos) -> Alerta Roja
    val_asig = df[col_asignacion].astype(str).str.strip().str.lower()
    cond_asig_sin_fecha = val_asig.eq("") | val_asig.eq("-") | val_asig.eq("nan") | val_asig.str.contains("pend|sin", na=False)
    
    df_sin_asignar = df[cond_no_finalizada & cond_tiene_cliente & cond_asig_sin_fecha]

    # Pre-entrega CON FECHA cargada (contiene números o barras '/' '-') -> Alerta Verde
    val_pre = df[col_preentrega].astype(str).str.strip().str.lower()
    cond_pre_con_fecha = val_pre.ne("") & val_pre.ne("-") & val_pre.ne("nan") & ~val_pre.str.contains("pend|no|sin", na=False)
    
    df_preentrega_lista = df[cond_no_finalizada & cond_pre_con_fecha]

    # --- INDICADORES EN PANTALLA ---
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Registro Histórico", len(df))
    col2.metric("⚠️ Sin Asignar (Sin fecha en Col. AY)", len(df_sin_asignar))
    col3.metric("✅ Pre-entrega Lista (Con fecha en Col. AZ)", len(df_preentrega_lista))

    st.markdown("---")

    # --- ALERTAS DEDICADAS ---
    if len(df_sin_asignar) > 0:
        st.error(f"🚨 **¡ATENCIÓN! HAY {len(df_sin_asignar)} UNIDADES CON CLIENTE SIN FECHA DE ASIGNACIÓN**")
        with st.expander("👉 Ver lista de unidades para coordinar asignación de transporte", expanded=True):
            st.dataframe(df_sin_asignar, use_container_width=True)
    else:
        st.info("👍 Todas las unidades activas con cliente ya cuentan con fecha de asignación.")

    if len(df_preentrega_lista) > 0:
        st.success(f"🎉 **¡PRE-ENTREGA FINALIZADA! HAY {len(df_preentrega_lista)} EQUIPOS CON FECHA DE PRE-ENTREGA LISTOS PARA SALIDA**")
        with st.expander("👉 Ver equipos listos para coordinar logística", expanded=True):
            st.dataframe(df_preentrega_lista, use_container_width=True)

    st.markdown("---")

    # --- VISTA DE TABLA CON FILTROS ---
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

    st.subheader(f"📋 Lista de Unidades ({modo_vista})")
    st.dataframe(df_mostrar, use_container_width=True)

except Exception as e:
    st.error(f"Error al procesar las alertas logísticas: {e}")
