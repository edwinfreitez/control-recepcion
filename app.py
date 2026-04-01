import streamlit as st
import pandas as pd
from datetime import datetime
import os

# 1. CONFIGURACIÓN
st.set_page_config(page_title="DUSA - Control de Recepción", page_icon="🧪", layout="wide")

DB_FILE = "historico_recepcion.csv"
COLUMNAS = [
    "Fecha", "Hora", "Tipo de Alcohol", "Tanque", "Producto", "Lote", 
    "Tanque Lavado", "Tanque Vaporizado", "Operador",
    "Volumen Aparente (L)", "Temperatura (°C)", "Grado Aparente (°GL)", 
    "Grado Real (°GL)", "Factor", "Volumen Real (L)", "LAA", "Observaciones"
]
OPCIONES_ALCOHOL = ["", "VLVCW", "VLVFW", "VLCCW", "VLCUQ", "VLVBW", "VLVRW", "VLVHO", "VLVUQ"]

def preparar_db():
    if not os.path.exists(DB_FILE):
        pd.DataFrame(columns=COLUMNAS).to_csv(DB_FILE, index=False)
    else:
        try:
            df_temp = pd.read_csv(DB_FILE)
            if "C4" in df_temp.columns:
                pd.DataFrame(columns=COLUMNAS).to_csv(DB_FILE, index=False)
        except:
            pd.DataFrame(columns=COLUMNAS).to_csv(DB_FILE, index=False)

preparar_db()

# --- LÓGICA DE LIMPIEZA (Session State) ---
def limpiar_campos():
    st.session_state["tipo"] = ""
    st.session_state["tanque"] = ""
    st.session_state["prod"] = ""
    st.session_state["lote"] = ""
    st.session_state["lavado"] = ""
    st.session_state["vapor"] = ""
    st.session_state["operador"] = ""
    st.session_state["v_ap"] = "0"
    st.session_state["temp"] = "0,00"
    st.session_state["g_ap"] = "0,00"
    st.session_state["g_re"] = "0,00"
    st.session_state["fact"] = "0,0000"
    st.session_state["obs"] = ""

# Inicializar llaves si no existen
if "tipo" not in st.session_state:
    limpiar_campos()

st.title("📋 Registro de Recepción de Alcohol")
st.markdown("---")

# 2. INTERFAZ DE ENTRADA
col1, col2 = st.columns(2)

with col1:
    tipo_alcohol = st.selectbox("Tipo de Alcohol", OPCIONES_ALCOHOL, key="tipo")
    tanque = st.text_input("Tanque", key="tanque")
    producto = st.text_input("Producto", key="prod")
    lote = st.text_input("Lote", key="lote")
    tanque_lavado = st.selectbox("Tanque Lavado", ["", "SI", "NO"], key="lavado")
    tanque_vaporizado = st.selectbox("Tanque Vaporizado", ["", "SI", "NO"], key="vapor")
    operador = st.text_input("Operador", key="operador")

with col2:
    v_aparente_raw = st.text_input("Volumen Aparente (L)", key="v_ap")
    temp_raw = st.text_input("Temperatura (°C)", key="temp")
    g_aparente_raw = st.text_input("Grado Aparente (°GL)", key="g_ap")
    g_real_raw = st.text_input("Grado Real (°GL)", key="g_re")
    factor_raw = st.text_input("Factor", key="fact")

    try:
        v_aparente = float(v_aparente_raw.replace(".", "").replace(",", "."))
        temp = float(temp_raw.replace(",", "."))
        g_aparente = float(g_aparente_raw.replace(",", "."))
        g_real = float(g_real_raw.replace(",", "."))
        factor = float(factor_raw.replace(",", "."))
    except:
        v_aparente, temp, g_aparente, g_real, factor = 0.0, 0.0, 0.0, 0.0, 0.0

    # 3. LÓGICA DE FÓRMULAS
    v_real = v_aparente * factor if g_real != 0 else 0.0
    laa = (v_real * g_real) / 100 if v_real != 0 else 0.0

    st.info(f"**Volumen Real (L):** {v_real:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    st.info(f"**LAA:** {laa:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

st.markdown("---")
observaciones = st.text_area("Observaciones", key="obs")

# 4. BOTÓN DE GUARDAR
if st.button("💾 Guardar en Histórico"):
    if tipo_alcohol == "" or operador == "":
        st.error("Error: 'Tipo de Alcohol' y 'Operador' son campos obligatorios.")
    else:
        nuevo_registro = {
            "Fecha": datetime.now().strftime("%d/%m/%Y"),
            "Hora": datetime.now().strftime("%H:%M:%S"),
            "Tipo de Alcohol": tipo_alcohol,
            "Tanque": tanque,
            "Producto": producto,
            "Lote": lote,
            "Tanque Lavado": tanque_lavado,
            "Tanque Vaporizado": tanque_vaporizado,
            "Operador": operador,
            "Volumen Aparente (L)": f"{v_aparente:,.0f}".replace(",", "."),
            "Temperatura (°C)": f"{temp:.2f}".replace(".", ","),
            "Grado Aparente (°GL)": f"{g_aparente:.2f}".replace(".", ","),
            "Grado Real (°GL)": f"{g_real:.2f}".replace(".", ","),
            "Factor": f"{factor:.4f}".replace(".", ","),
            "Volumen Real (L)": f"{v_real:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
            "LAA": f"{laa:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
            "Observaciones": observaciones
        }
        
        df_hist = pd.read_csv(DB_FILE)
        df_nuevo = pd.DataFrame([nuevo_registro])
        pd.concat([df_hist, df_nuevo], ignore_index=True).to_csv(DB_FILE, index=False)
        
        st.success("✅ Registro guardado. Limpiando formulario...")
        limpiar_campos()
        st.rerun() # Esto recarga la página con los campos vacíos

# 5. VISUALIZACIÓN
if st.checkbox("Ver últimos registros"):
    st.dataframe(pd.read_csv(DB_FILE).tail(10))
