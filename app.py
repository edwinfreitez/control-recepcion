import streamlit as st
import pandas as pd
from datetime import datetime
import os

# 1. CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="Registro de Recepción de Alcoholes", page_icon="🧪", layout="wide")

# --- FUNCIONES DE APOYO (ESTÁNDAR VENEZUELA) ---
def formatear_venezuela(valor, decimales=2):
    try:
        val = float(valor) if valor else 0.0
        texto = "{:,.{}f}".format(val, decimales)
        return texto.translate(str.maketrans(",.", ".,"))
    except:
        return "0,00"

# --- ENCABEZADO (ESTILO EXACTO A TU CALCULADORA) ---
st.image("https://dusa.com.ve/wp-content/uploads/2020/10/Logo-Original.png", width=180)
st.markdown('<h2 style="font-size: 24px; margin-bottom: 0px; margin-top: -20px;">📋 Registro de Recepción de Alcoholes</h2>', unsafe_allow_html=True)
st.markdown("""**Destilerías Unidas, S.A.** *© Edwin Freitez*""")
st.markdown("---")

# 2. CONFIGURACIÓN DE BASE DE DATOS
DB_FILE = "historico_recepcion.csv"
COLUMNAS = [
    "Fecha", "Hora", "Tipo de Alcohol", "Tanque", "Producto", "Lote", 
    "¿Tanque Lavado?", "¿Tanque Vaporizado?", "Operador",
    "Volumen Aparente (L)", "Temperatura (°C)", "Grado Aparente (°GL)", 
    "Grado Real (°GL)", "Factor de corrección", "Volumen Real (L)", "LAA", "Observaciones"
]
OPCIONES_ALCOHOL = ["", "VLVCW", "VLVFW", "VLCCW", "VLCUQ", "VLVBW", "VLVRW", "VLVHO", "VLVUQ"]

def preparar_db():
    if not os.path.exists(DB_FILE):
        pd.DataFrame(columns=COLUMNAS).to_csv(DB_FILE, index=False)
    else:
        try:
            df_temp = pd.read_csv(DB_FILE)
            # Limpieza automática si detecta nombres de celdas viejas (C4, E5, etc.)
            if "C4" in df_temp.columns:
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
    tanque_lavado = st.selectbox("¿Tanque Lavado?", ["", "SI", "NO"])
    tanque_vaporizado = st.selectbox("¿Tanque Vaporizado?", ["", "SI", "NO"])
    operador = st.text_input("Operador")

with col2:
    # Celdas vacías por defecto
    v_aparente_raw = st.text_input("Volumen Aparente (L)", value="")
    temp_raw = st.text_input("Temperatura (°C)", value="")
    g_aparente_raw = st.text_input("Grado Aparente (°GL)", value="")
    g_real_raw = st.text_input("Grado Real (°GL)", value="")
    factor_raw = st.text_input("Factor de corrección", value="")

    try:
        # Conversión que acepta el formato de entrada venezolano
        v_aparente = float(v_aparente_raw.replace(".", "").replace(",", ".")) if v_aparente_raw else 0.0
        temp = float(temp_raw.replace(",", ".")) if temp_raw else 0.0
        g_aparente = float(g_aparente_raw.replace(",", ".")) if g_aparente_raw else 0.0
        g_real = float(g_real_raw.replace(",", ".")) if g_real_raw else 0.0
        factor = float(factor_raw.replace(",", ".")) if factor_raw else 0.0
    except:
        v_aparente, temp, g_aparente, g_real, factor = 0.0, 0.0, 0.0, 0.0, 0.0

    v_real = v_aparente * factor if g_real != 0 else 0.0
    laa = (v_real * g_real) / 100 if v_real != 0 else 0.0

    # Métricas con el formato visual de DUSA
    st.info(f"**Volumen Real (L):** {formatear_venezuela(v_real)}")
    st.info(f"**LAA:** {formatear_venezuela(laa)}")

st.markdown("---")
observaciones = st.text_area("Observaciones")

# 4. BOTÓN DE GUARDAR
if st.button("💾 Guardar", use_container_width=True):
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
            "Volumen Aparente (L)": formatear_venezuela(v_aparente, 0),
            "Temperatura (°C)": formatear_venezuela(temp, 2),
            "Grado Aparente (°GL)": formatear_venezuela(g_aparente, 2),
            "Grado Real (°GL)": formatear_venezuela(g_real, 2),
            "Factor": formatear_venezuela(factor, 4),
            "Volumen Real (L)": formatear_venezuela(v_real, 2),
            "LAA": formatear_venezuela(laa, 2),
            "Observaciones": observaciones
        }
        
        df_hist = pd.read_csv(DB_FILE)
        pd.concat([df_hist, pd.DataFrame([nuevo_registro])], ignore_index=True).to_csv(DB_FILE, index=False)
        st.success("✅ Registro guardado exitosamente.")
        st.balloons()

# 5. HISTÓRICO Y EXPORTACIÓN
st.markdown("---")
if st.checkbox("Ver últimos registros"):
    df_ver = pd.read_csv(DB_FILE)
    st.dataframe(df_ver.tail(10), use_container_width=True)
    
    # Exportación con ';' para que Excel separe columnas automáticamente
    csv_excel = df_ver.to_csv(index=False, sep=';').encode('utf-8-sig')
    st.download_button(
        label="📥 Descargar Excel",
        data=csv_excel,
        file_name=f'historico_recepcion_{datetime.now().strftime("%Y%m%d")}.csv',
        mime='text/csv',
    )
