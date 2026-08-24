
import streamlit as st
import pandas as pd
from utils import auto_clean, kpi_cards, forecast, connect_db
import plotly.express as px

# Configuración inicial del panel
st.set_page_config(page_title="Auto KPI SaaS v2", layout="wide")

# Título principal
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

    # Limpieza automática sin borrar datos importantes
    df = auto_clean(df)

    # KPIs principales
    st.subheader("📊 KPIs principales")
    kpi_cards(df)

    # Gráfico interactivo con hover
    st.subheader("📈 Análisis interactivo")
    fig = px.line(df, x=df.columns[0], y=df.columns[1], title="Tendencia KPI")
    fig.update_traces(mode="lines+markers", hovertemplate="Fecha: %{x}<br>Valor: %{y}")
    st.plotly_chart(fig, use_container_width=True)

    # Predicciones automáticas
    st.subheader("🔮 Predicción 30 días")
    forecast(df)

else:
    st.info("Sube un archivo para comenzar el análisis.")
