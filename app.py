import streamlit as st
import pandas as pd
from datetime import datetime
import os

# 1. CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="DUSA - Control de Recepción", page_icon="🧪", layout="wide")

# Nombre del archivo de base de datos
DB_FILE = "historico_recepcion.csv"

# Definición de las columnas finales (Nombres reales)
COLUMNAS = [
    "Fecha", "Hora", "Tipo de Alcohol", "Tanque", "Producto", "Lote", 
    "Tanque Lavado", "Tanque Vaporizado", "Operador",
    "Volumen Aparente (L)", "Temperatura (°C)", "Grado Aparente (°GL)", 
    "Grado Real (°GL)", "Factor", "Volumen Real (L)", "LAA", "Observaciones"
]

def preparar_db():
    # Si el archivo no existe, lo creamos con los nuevos encabezados
    if not os.path.exists(DB_FILE):
        pd.DataFrame(columns=COLUMNAS).to_csv(DB_FILE, index=False)
    else:
        # Si existe pero tiene las columnas viejas (C4, E5, etc.), lo reseteamos
        df_temp = pd.read_csv(DB_FILE)
        if "C4" in df_temp.columns:
            pd.DataFrame(columns=COLUMNAS).to_csv(DB_FILE, index=False)

preparar_db()

st.title("📋 Registro de Recepción de Alcohol")
st.markdown("---")

# 2. INTERFAZ DE ENTRADA (Sin etiquetas de celdas Excel)
col1, col2 = st.columns(2)

with col1:
    tipo_alcohol = st.text_input("Tipo de Alcohol")
    tanque = st.text_input("Tanque")
    producto = st.text_input("Producto")
    lote = st.text_input("Lote")
    tanque_lavado = st.selectbox("Tanque Lavado", ["", "SI", "NO"])
    tanque_vaporizado = st.selectbox("Tanque Vaporizado", ["", "SI", "NO"])
    operador = st.text_input("Operador")

with col2:
    # Entradas de texto para evitar botones +/- y controlar el formato
    v_aparente_raw = st.text_input("Volumen Aparente (L)", value="0")
    temp_raw = st.text_input("Temperatura (°C)", value="0,00")
    g_aparente_raw = st.text_input("Grado Aparente (°GL)", value="0,00")
    g_real_raw = st.text_input("Grado Real (°GL)", value="0,00")
    factor_raw = st.text_input("Factor", value="0,0000")

    # Conversión para cálculos (Manejo de coma decimal y punto de miles)
    try:
        v_aparente = float(v_aparente_raw.replace(".", "").replace(",", "."))
        temp = float(temp_raw.replace(",", "."))
        g_aparente = float(g_aparente_raw.replace(",", "."))
        g_real = float(g_real_raw.replace(",", "."))
        factor = float(factor_raw.replace(",", "."))
    except:
        v_aparente, temp, g_aparente, g_real, factor = 0.0, 0.0, 0.0, 0.0, 0.0

    # 3. LÓGICA DE FÓRMULAS (E9 y E10)
    v_real = v_aparente * factor if g_real != 0 else 0.0
    laa = (v_real * g_real) / 100 if v_real != 0 else 0.0

    # Mostrar cálculos en pantalla con formato venezolano
    st.info(f"**Volumen Real (L):** {v_real:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    st.info(f"**LAA:** {laa:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

st.markdown("---")
observaciones = st.text_area("Observaciones")

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
        
        # Guardar datos
        df_hist = pd.read_csv(DB_FILE)
        df_nuevo = pd.DataFrame([nuevo_registro])
        df_final = pd.concat([df_hist, df_nuevo], ignore_index=True)
        df_final.to_csv(DB_FILE, index=False)
        
        st.success("✅ Registro guardado exitosamente.")
        st.balloons()

# 5. VISUALIZACIÓN DE LA TABLA
if st.checkbox("Ver últimos registros"):
    st.dataframe(pd.read_csv(DB_FILE).tail(10))
