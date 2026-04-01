import streamlit as st
import pandas as pd
from datetime import datetime
import os

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="DUSA - Control de Recepción", page_icon="🧪", layout="wide")

# Nombre del archivo de base de datos
DB_FILE = "historico_recepcion.csv"

def preparar_db():
    if not os.path.exists(DB_FILE):
        columnas = [
            "Fecha", "Hora", "Tipo de Alcohol", "Tanque", "Producto", "Lote", 
            "Tanque Lavado", "Tanque Vaporizado", "Operador",
            "Volumen Aparente (L)", "Temperatura (°C)", "Grado Aparente (°GL)", 
            "Grado Real (°GL)", "Factor", "Volumen Real (L)", "LAA", "Observaciones"
        ]
        pd.DataFrame(columns=columnas).to_csv(DB_FILE, index=False)

preparar_db()

st.title("📋 Registro de Recepción de Alcohol")
st.markdown("---")

# 2. INTERFAZ DE ENTRADA DE DATOS
col1, col2 = st.columns(2)

with col1:
    tipo_alcohol = st.text_input("Tipo de Alcohol (C4)")
    tanque = st.text_input("Tanque (C5)")
    producto = st.text_input("Producto (C6)")
    lote = st.text_input("Lote (C7)")
    tanque_lavado = st.selectbox("Tanque Lavado (C8)", ["", "SI", "NO"])
    tanque_vaporizado = st.selectbox("Tanque Vaporizado (C9)", ["", "SI", "NO"])
    operador = st.text_input("Operador (C10)")

with col2:
    # Uso de text_input para evitar los botones +/- y manejar formatos personalizados
    v_aparente_raw = st.text_input("Volumen Aparente (L) (E4)", value="0")
    temp_raw = st.text_input("Temperatura (°C) (E5)", value="0.00")
    g_aparente_raw = st.text_input("Grado Aparente (°GL) (E6)", value="0.00")
    g_real_raw = st.text_input("Grado Real (°GL) (E7)", value="0.00")
    factor_raw = st.text_input("Factor (E8)", value="0.0000")

    # Conversión segura para cálculos
    try:
        v_aparente = float(v_aparente_raw.replace(".", "").replace(",", "."))
        temp = float(temp_raw.replace(",", "."))
        g_aparente = float(g_aparente_raw.replace(",", "."))
        g_real = float(g_real_raw.replace(",", "."))
        factor = float(factor_raw.replace(",", "."))
    except:
        v_aparente, temp, g_aparente, g_real, factor = 0.0, 0.0, 0.0, 0.0, 0.0

    # 3. LÓGICA DE FÓRMULAS (Equivalente a tus fórmulas de Excel E9 y E10)
    # E9: SI(E7="";"";E4*E8)
    v_real = v_aparente * factor if g_real != 0 else 0.0
    
    # E10: SI(E9="";"";E9*E7/100)
    laa = (v_real * g_real) / 100 if v_real != 0 else 0.0

    # Mostrar resultados de fórmulas (Solo lectura)
    st.info(f"**Volumen Real (L) (E9):** {v_real:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    st.info(f"**LAA (E10):** {laa:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

st.markdown("---")
observaciones = st.text_area("Observaciones", help="Equivalente a B12 en Excel")

# 4. BOTÓN DE GUARDAR Y LIMPIEZA
if st.button("💾 Guardar en Histórico"):
    if tipo_alcohol == "" or operador == "":
        st.error("Por favor, complete los campos obligatorios (Tipo de Alcohol y Operador).")
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
            "Temperatura (°C)": f"{temp:.2f}",
            "Grado Aparente (°GL)": f"{g_aparente:.2f}",
            "Grado Real (°GL)": f"{g_real:.2f}",
            "Factor": f"{factor:.4f}",
            "Volumen Real (L)": f"{v_real:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
            "LAA": f"{laa:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
            "Observaciones": observaciones
        }
        
        # Guardar en CSV
        df_hist = pd.read_csv(DB_FILE)
        df_nuevo = pd.DataFrame([nuevo_registro])
        pd.concat([df_hist, df_nuevo], ignore_index=True).to_csv(DB_FILE, index=False)
        
        st.success("✅ Registro guardado exitosamente.")
        # Nota: Streamlit limpia los campos de entrada al recargar automáticamente tras un submit en ciertos contextos, 
        # pero aquí los valores de las fórmulas se mantienen por la lógica del script.
        st.balloons()

# 5. VISUALIZACIÓN DEL HISTÓRICO
if st.checkbox("Ver últimos 10 registros"):
    st.dataframe(pd.read_csv(DB_FILE).tail(10))
