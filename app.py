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

# Opciones para la lista de tipos de alcohol
OPCIONES_ALCOHOL = ["", "VLVCW", "VLVFW", "VLCCW", "VLCUQ", "VLVBW", "VLVRW", "VLVHO", "VLVUQ"]

def preparar_db():
    if not os.path.exists(DB_FILE):
        # Guardamos con punto y coma para compatibilidad directa con Excel
        pd.DataFrame(columns=COLUMNAS).to_csv(DB_FILE, index=False, sep=';')
    else:
        try:
            # Intentamos leer con punto y coma
            df_temp = pd.read_csv(DB_FILE, sep=';')
            if "C4" in df_temp.columns or "C5" in df_temp.columns:
                pd.DataFrame(columns=COLUMNAS).to_csv(DB_FILE, index=False, sep=';')
        except:
            pd.DataFrame(columns=COLUMNAS).to_csv(DB_FILE, index=False, sep=';')

preparar_db()

st.title("📋 Registro de Recepción de Alcohol")
st.markdown("---")

# 2. INTERFAZ DE ENTRADA
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
    # Se eliminaron los valores por defecto "0" y "0,00"
    v_aparente_raw = st.text_input("Volumen Aparente (L)", value="")
    temp_raw = st.text_input("Temperatura (°C)", value="")
    g_aparente_raw = st.text_input("Grado Aparente (°GL)", value="")
    g_real_raw = st.text_input("Grado Real (°GL)", value="")
    factor_raw = st.text_input("Factor", value="")

    # Conversión para cálculos (Manejo de coma decimal y punto de miles)
    try:
        v_aparente = float(v_aparente_raw.replace(".", "").replace(",", ".")) if v_aparente_raw else 0.0
        temp = float(temp_raw.replace(",", ".")) if temp_raw else 0.0
        g_aparente = float(g_aparente_raw.replace(",", ".")) if g_aparente_raw else 0.0
        g_real = float(g_real_raw.replace(",", ".")) if g_real_raw else 0.0
        factor = float(factor_raw.replace(",", ".")) if factor_raw else 0.0
    except:
        v_aparente, temp, g_aparente, g_real, factor = 0.0, 0.0, 0.0, 0.0, 0.0

    # 3. LÓGICA DE FÓRMULAS
    v_real = v_aparente * factor if g_real != 0 else 0.0
    laa = (v_real * g_real) / 100 if v_real != 0 else 0.0

    # Mostrar cálculos en pantalla
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
        
        # Guardar usando punto y coma como separador
        df_hist = pd.read_csv(DB_FILE, sep=';')
        df_nuevo = pd.DataFrame([nuevo_registro])
        df_final = pd.concat([df_hist, df_nuevo], ignore_index=True)
        df_final.to_csv(DB_FILE, index=False, sep=';')
        
        st.success("✅ Registro guardado exitosamente.")
        st.balloons()

# 5. VISUALIZACIÓN DE LA TABLA
if st.checkbox("Ver últimos registros"):
    st.dataframe(pd.read_csv(DB_FILE, sep=';').tail(10))
