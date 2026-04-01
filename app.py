import streamlit as st
import pandas as pd
from datetime import datetime
import os

# 1. CONFIGURACIÓN DE LA PÁGINA
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
            # Si detecta encabezados viejos de Excel (C4, etc), limpia el archivo
            if "C4" in df_temp.columns:
                pd.DataFrame(columns=COLUMNAS).to_csv(DB_FILE, index=False)
        except:
            pd.DataFrame(columns=COLUMNAS).to_csv(DB_FILE, index=False)

preparar_db()

st.title("📋 Registro de Recepción de Alcohol")
st.markdown("---")

# 2. FORMULARIO DE ENTRADA
# 'clear_on_submit=True' hace que al darle a Guardar, todos los campos vuelvan a blanco/cero
with st.form("formulario_dusa", clear_on_submit=True):
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
        v_aparente_raw = st.text_input("Volumen Aparente (L)", value="0")
        temp_raw = st.text_input("Temperatura (°C)", value="0,00")
        g_aparente_raw = st.text_input("Grado Aparente (°GL)", value="0,00")
        g_real_raw = st.text_input("Grado Real (°GL)", value="0,00")
        factor_raw = st.text_input("Factor", value="0,0000")

        # Nota: Los cálculos se realizan al momento de procesar el envío (submit)
        st.write("---")
        st.caption("Los cálculos de Volumen Real y LAA se procesarán al guardar.")

    observaciones = st.text_area("Observaciones")
    
    # El botón de Guardar ahora es el 'submit' del formulario
    boton_guardar = st.form_submit_button("💾 Guardar en Histórico")

# 3. LÓGICA DE PROCESAMIENTO
if boton_guardar:
    if tipo_alcohol == "" or operador == "":
        st.error("Error: 'Tipo de Alcohol' y 'Operador' son obligatorios.")
    else:
        try:
            # Conversión de los textos a números para cálculos
            v_ap = float(v_aparente_raw.replace(".", "").replace(",", "."))
            temp = float(temp_raw.replace(",", "."))
            g_ap = float(g_aparente_raw.replace(",", "."))
            g_re = float(g_real_raw.replace(",", "."))
            fact = float(factor_raw.replace(",", "."))
            
            # Fórmulas (E9 y E10 de tu Excel)
            v_real_calc = v_ap * fact if g_re != 0 else 0.0
            laa_calc = (v_real_calc * g_re) / 100 if v_real_calc != 0 else 0.0

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
                "Volumen Aparente (L)": f"{v_ap:,.0f}".replace(",", "."),
                "Temperatura (°C)": f"{temp:.2f}".replace(".", ","),
                "Grado Aparente (°GL)": f"{g_ap:.2f}".replace(".", ","),
                "Grado Real (°GL)": f"{g_re:.2f}".replace(".", ","),
                "Factor": f"{fact:.4f}".replace(".", ","),
                "Volumen Real (L)": f"{v_real_calc:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
                "LAA": f"{laa_calc:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
                "Observaciones": observaciones
            }
            
            # Guardar en el CSV
            df_hist = pd.read_csv(DB_FILE)
            pd.concat([df_hist, pd.DataFrame([nuevo_registro])], ignore_index=True).to_csv(DB_FILE, index=False)
            
            st.success("✅ Registro guardado exitosamente. Formulario listo para nueva entrada.")
            st.balloons()
            
        except ValueError:
            st.error("Error en el formato de los números. Verifique puntos y comas.")

# 4. VISUALIZACIÓN DEL HISTÓRICO
st.markdown("---")
if st.checkbox("Ver últimos registros"):
    st.dataframe(pd.read_csv(DB_FILE).tail(10))
