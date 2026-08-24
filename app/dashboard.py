import streamlit as st
import pandas as pd
import numpy as np
from utils import auto_clean, kpi_cards, forecast, connect_db
import plotly.express as px
from prophet import Prophet

# Configuración inicial del panel
st.set_page_config(page_title="Auto KPI SaaS v2", layout="wide")

st.title("✨ Auto KPI SaaS v2")
st.caption("Panel holográfico tipo Power BI con KPIs, predicciones y análisis interactivo.")

# Subida de archivo
uploaded_file = st.file_uploader("📂 Sube tu archivo Excel/CSV", type=["csv", "xlsx"])

if uploaded_file:
    # Detectar tipo de archivo
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    # Limpieza automática
    df = auto_clean(df)

    # Tarjetas tipo Power BI
    st.subheader("💎 KPIs holográficos")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("🧩 Registros totales", len(df))
    with col2:
        st.metric("💰 Promedio general", round(df.select_dtypes(include=np.number).mean().mean(), 2))
    with col3:
        st.metric("📈 Columnas analizadas", len(df.columns))

    # Gráfico interactivo con hover
    st.subheader("📊 Análisis interactivo")
    try:
        fig = px.line(df, x=df.columns[0], y=df.select_dtypes(include=np.number).columns[0],
                      title="Tendencia KPI", markers=True)
        fig.update_traces(line=dict(width=2), hovertemplate="Fecha: %{x}<br>Valor: %{y}")
        fig.update_layout(template="plotly_dark", plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)
        st.caption("🧠 Al pasar el cursor sobre los puntos, verás el análisis automático de variaciones y tendencias.")
    except Exception as e:
        st.error(f"No se pudo generar el gráfico interactivo: {e}")

    # Predicción 30 días
    st.subheader("🔮 Predicción 30 días")
    try:
        df_forecast = df[[df.columns[0], df.select_dtypes(include=np.number).columns[0]]].rename(
            columns={df.columns[0]: "ds", df.select_dtypes(include=np.number).columns[0]: "y"})
        model = Prophet()
        model.fit(df_forecast)
        future = model.make_future_dataframe(periods=30)
        forecast = model.predict(future)
        fig_forecast = px.line(forecast, x="ds", y="yhat", title="Predicción de tendencia 30 días")
        fig_forecast.update_layout(template="plotly_dark", plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_forecast, use_container_width=True)
    except Exception as e:
        st.error(f"No se pudo generar la predicción: {e}")

else:
    st.info("Sube un archivo para comenzar el análisis.")
