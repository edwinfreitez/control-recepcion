import streamlit as st
import pandas as pd
from datetime import datetime
import os

# 1. CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="Registro de Recepción de Alcoholes", page_icon="🧪", layout="wide")

# --- ESTILO VISUAL (ENCABEZADO ESTÁNDAR DUSA) ---
st.markdown("""
    <style>
    .block-container {padding-top: 3.5rem;}
    .st-emotion-cache-12fmjuu {padding: 1rem 1rem 1rem 1rem;}
    </style>
    """, unsafe_allow_html=True)

# Banner superior con Logo y Título Azul
URL_LOGO = "https://raw.githubusercontent.com/edwinfreitez/calculadora/main/dusa.png"

col_logo, col_tit = st.columns([1, 4])
with col_logo:
    st.image(URL_LOGO, width=150)
with col_tit:
    st.markdown("""
        <div style="background-color: #002060; padding: 15px; border-radius: 10px;">
            <h1 style="color: white; text-align: center; margin: 0; font-family: sans-serif;">
                Registro de Recepción de Alcoholes
            </h1>
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")

# 2. CONFIGURACIÓN DE BASE DE DATOS
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
            if "C4" in df_temp.columns or "C5" in df_temp.columns:
                pd.DataFrame(columns=COLUMNAS).to_csv(DB_FILE, index=False)
        except:
            pd.DataFrame(columns=COLUMNAS).to_csv(DB_FILE, index=False)

preparar_db()

# 3. INTERFAZ DE ENTRADA
col1, col2 = st.columns(2)

with col1:
    tipo_alcohol = st.selectbox("Tipo de Alcohol", OPCIONES_ALCOHOL)
    tanque = st.text_input("Tanque")
    producto = st.text_input("Producto")
    lote = st.text_input("Lote")
    tanque_lavado = st.selectbox("Tanque Lavado", ["", "SI", "NO"])
    tanque_vaporizado = st.selectbox("Tanque Vaporizado", ["", "SI", "NO"])
    operador = st.text_input("Operador")

with col2:
    v_aparente_raw = st.text_input("Volumen Aparente (L)", value="")
    temp_raw = st.text_input("Temperatura (°C)", value="")
    g_aparente_raw = st.text_input("Grado Aparente (°GL)", value="")
    g_real_raw = st.text_input("Grado Real (°GL)", value="")
    factor_raw = st.text_input("Factor", value="")

    try:
        v_aparente = float(v_aparente_raw.replace(".", "").replace(",", ".")) if v_aparente_raw else 0.0
        temp = float(temp_raw.replace(",", ".")) if temp_raw else 0.0
        g_aparente = float(g_aparente_raw.replace(",", ".")) if g_aparente_raw else 0.0
        g_real = float(g_real_raw.replace(",", ".")) if g_real_raw else 0.0
        factor = float(factor_raw.replace(",", ".")) if factor_raw else 0.0
    except:
        v_aparente, temp, g_aparente, g_real, factor = 0.0, 0.0, 0.0, 0.0, 0.0

    v_real = v_aparente * factor if g_real != 0 else 0.0
    laa = (v_real * g_real) / 100 if v_real != 0 else 0.0

    st.info(f"**Volumen Real (L):** {v_real:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    st.info(f"**LAA:** {laa:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

st.markdown("---")
observaciones = st.text_area("Observaciones")

# 4. BOTÓN DE GUARDAR
if st.button("💾 Guardar en Histórico"):
    if tipo_alcohol == "" or operador == "":
        st.error("Error: 'Tipo de Alcohol' y 'Operador' son obligatorios.")
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
        pd.concat([df_hist, pd.DataFrame([nuevo_registro])], ignore_index=True).to_csv(DB_FILE, index=False)
        st.success("✅ Registro guardado exitosamente.")
        st.balloons()

# 5. VISUALIZACIÓN Y DESCARGA
st.markdown("---")
if st.checkbox("Ver últimos registros"):
    df_ver = pd.read_csv(DB_FILE)
    st.dataframe(df_ver.tail(10))
    
    # Exportación optimizada para Excel
    csv_excel = df_ver.to_csv(index=False, sep=';').encode('utf-8-sig')
    st.download_button(
        label="📥 Descargar para Excel (Columnas separadas)",
        data=csv_excel,
        file_name=f'historico_recepcion_{datetime.now().strftime("%Y%m%d")}.csv',
        mime='text/csv',
    )
