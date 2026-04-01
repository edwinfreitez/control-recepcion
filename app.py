import streamlit as st
import pandas as pd
from datetime import datetime
import os

# Configuración visual
st.set_page_config(page_title="DUSA - Control de Recepción", page_icon="🧪")

# Nombre del archivo de datos
DB_FILE = "historico_recepcion.csv"

# Función para asegurar que el archivo existe
def preparar_db():
    if not os.path.exists(DB_FILE):
        columnas = ["Fecha", "Hora", "C4", "C5", "C6", "C7", "C8", "C9", "C10", 
                    "E4", "E5", "E6", "E7", "E8", "E9_Formula", "E10_Formula", "Observaciones"]
        pd.DataFrame(columns=columnas).to_csv(DB_FILE, index=False)

preparar_db()

st.title("📋 Registro de Recepción de Alcohol")

# Formulario de entrada
with st.form("formulario_datos"):
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Bloque C")
        c4 = st.number_input("C4", value=0.0)
        c5 = st.number_input("C5", value=0.0)
        c6 = st.number_input("C6", value=0.0)
        c7 = st.number_input("C7", value=0.0)
        c8 = st.number_input("C8", value=0.0)
        c9 = st.number_input("C9", value=0.0)
        c10 = st.number_input("C10", value=0.0)

    with col2:
        st.subheader("Bloque E")
        e4 = st.number_input("E4", value=0.0)
        e5 = st.number_input("E5", value=0.0)
        e6 = st.number_input("E6", value=0.0)
        e7 = st.number_input("E7", value=0.0)
        e8 = st.number_input("E8", value=0.0)
        # Aquí puedes definir las fórmulas reales de E9 y E10 si las tienes
        e9 = e4 + e5 
        e10 = e6 * 0.1 
        st.info(f"Cálculo E9: {e9}")
        st.info(f"Cálculo E10: {e10}")

    obs = st.text_input("Observaciones")
    
    boton_guardar = st.form_submit_button("Guardar en Histórico")

if boton_guardar:
    nuevo = {
        "Fecha": datetime.now().strftime("%d/%m/%Y"),
        "Hora": datetime.now().strftime("%H:%M:%S"),
        "C4": c4, "C5": c5, "C6": c6, "C7": c7, "C8": c8, "C9": c9, "C10": c10,
        "E4": e4, "E5": e5, "E6": e6, "E7": e7, "E8": e8,
        "E9_Formula": e9, "E10_Formula": e10, "Observaciones": obs
    }
    df = pd.read_csv(DB_FILE)
    df = pd.concat([df, pd.DataFrame([nuevo])], ignore_index=True)
    df.to_csv(DB_FILE, index=False)
    st.success("¡Datos guardados correctamente!")

# Visualización rápida
if st.checkbox("Mostrar últimos registros"):
    st.table(pd.read_csv(DB_FILE).tail(5))
