import sys, os
sys.path.append(os.path.dirname(__file__))

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# Importar funciones desde utils.py
from utils import (
    auto_clean,
    connect_db,
    generate_kpi,
    analyze_business,
    predict_future,
    decision_ai,
    executive_summary
)

# Configuración inicial
st.set_page_config(page_title="Panel estratégico de decisiones", layout="wide")

st.title("🧠 Consultor Digital Autónomo")
st.caption("Sistema experto que analiza, predice y recomienda estrategias empresariales sin intervención humana.")

# Subida de archivo
uploaded_file = st.file_uploader("📂 Sube tu archivo Excel/CSV", type=["csv", "xlsx"])

if uploaded_file:
    # Lectura de archivo
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    # Limpieza automática
    df, corrections = auto_clean(df)
    if corrections:
        with st.expander("🧹 Limpieza automática"):
            st.dataframe(pd.DataFrame(corrections), use_container_width=True)

    # Análisis ejecutivo
    st.subheader("📈 Análisis ejecutivo")
    st.markdown(analyze_business(df))

    # Resumen ejecutivo
    st.subheader("📑 Resumen ejecutivo")
    st.markdown(executive_summary(df))

    # KPIs estratégicos y personalizados
    st.subheader("🎯 KPIs estratégicos y personalizados")
    new_kpi = st.text_input("Escribe el KPI que deseas crear (ejemplo: 'Satisfacción del cliente')")
    if new_kpi:
        formula, chart = generate_kpi(df, new_kpi)
        st.success(f"KPI '{new_kpi}' generado con fórmula: {formula}")
        st.plotly_chart(chart, use_container_width=True)

    # Predicción y simulación
    st.subheader("🔮 Predicción y simulación")
    try:
        fig_forecast = predict_future(df)
        st.plotly_chart(fig_forecast, use_container_width=True)
    except Exception as e:
        st.error(f"No se pudo generar la predicción: {e}")

    # Decisiones sugeridas
    st.subheader("🧭 Decisiones sugeridas por IA")
    decisions = decision_ai(df)
    st.markdown(decisions)

else:
    st.info("Sube un archivo para comenzar el análisis.")
