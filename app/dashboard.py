import sys, os
sys.path.append(os.path.dirname(__file__))

import streamlit as st
import pandas as pd
import numpy as np
from utils import auto_clean, connect_db, generate_kpi, analyze_business, predict_future
import plotly.express as px
from prophet import Prophet

st.set_page_config(page_title="Auto KPI SaaS v5", layout="wide")

st.title("🧠 Consultor Digital Autónomo")
st.caption("Sistema experto que analiza, predice y recomienda estrategias empresariales sin intervención humana.")

uploaded_file = st.file_uploader("📂 Sube tu archivo Excel/CSV", type=["csv", "xlsx"])

if uploaded_file:
    df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith(".csv") else pd.read_excel(uploaded_file)
    df, corrections = auto_clean(df)

    if corrections:
        with st.expander("🧹 Limpieza automática"):
            st.dataframe(pd.DataFrame(corrections), use_container_width=True)

    st.subheader("📈 Análisis ejecutivo")
    st.markdown(analyze_business(df))

    st.subheader("🎯 KPIs estratégicos")
    kpi_list = ["Rentabilidad", "Eficiencia operativa", "Cumplimiento legal"]
    for kpi in kpi_list:
        st.metric(kpi, round(df.select_dtypes(include=np.number).mean().mean(), 2))

    st.subheader("⚙️ Generador de KPIs personalizados")
    new_kpi = st.text_input("Escribe el KPI que deseas crear (ejemplo: 'Satisfacción del cliente')")
    if new_kpi:
        formula, chart = generate_kpi(df, new_kpi)
        st.success(f"KPI '{new_kpi}' generado con fórmula: {formula}")
        st.plotly_chart(chart, use_container_width=True)

    st.subheader("🔮 Predicción y simulación")
    try:
        fig_forecast = predict_future(df)
        st.plotly_chart(fig_forecast, use_container_width=True)
    except Exception as e:
        st.error(f"No se pudo generar la predicción: {e}")

else:
    st.info("Sube un archivo para comenzar el análisis.")
