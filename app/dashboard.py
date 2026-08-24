import streamlit as st
import pandas as pd
import numpy as np
from utils import auto_clean, kpi_cards, forecast, connect_db, suggest_kpis
import plotly.express as px
from prophet import Prophet

# Configuración inicial
st.set_page_config(page_title="Auto KPI SaaS v2", layout="wide")

st.title("✨ Auto KPI SaaS v2")
st.caption("Panel holográfico tipo Power BI con KPIs, predicciones y análisis interactivo.")

# Subida de archivo
uploaded_file = st.file_uploader("📂 Sube tu archivo Excel/CSV", type=["csv", "xlsx"])

if uploaded_file:
    # Leer archivo
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    # Limpieza automática con revisión
    df, corrections = auto_clean(df)

    # Mostrar resumen de limpieza
    if corrections:
        with st.expander("🧹 Ver correcciones realizadas"):
            st.dataframe(pd.DataFrame(corrections), use_container_width=True)
            st.info("Haz clic en cada fila para autorizar o revertir la corrección manualmente.")

    # KPIs principales
    st.subheader("💎 KPIs holográficos")
    kpi_cards(df)

    # Sugerencias de KPIs por IA
    st.subheader("🤖 Sugerencias automáticas de KPIs")
    suggested = suggest_kpis(df)
    st.write("La IA sugiere analizar los siguientes indicadores:")
    st.dataframe(pd.DataFrame(suggested), use_container_width=True)

    # Permitir agregar KPIs personalizados
    st.info("¿Deseas agregar otros KPIs manualmente?")
    new_kpi = st.text_input("Escribe el nombre del nuevo KPI:")
    if new_kpi:
        st.success(f"✅ KPI '{new_kpi}' agregado correctamente.")

    # Análisis por categorías
    st.subheader("📊 Análisis por categorías")
    num_cols = df.select_dtypes(include=np.number).columns
    cat_cols = df.select_dtypes(exclude=np.number).columns

    if len(cat_cols) > 0 and len(num_cols) > 0:
        cat = cat_cols[0]
        num = num_cols[0]
        resumen = df.groupby(cat)[num].agg(["count", "mean"]).reset_index()
        fig_bar = px.bar(resumen, x=cat, y="mean", color=cat,
                         title=f"Promedio de {num} por {cat}", text_auto=True)
        fig_bar.update_layout(template="plotly_dark",
                              plot_bgcolor="rgba(0,0,0,0)",
                              paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.info("No se detectaron columnas categóricas para análisis segmentado.")

    # Predicción 30 días
    st.subheader("🔮 Predicción 30 días")
    try:
        df_forecast = df[[df.columns[0], df.select_dtypes(include=np.number).columns[0]]].rename(
            columns={df.columns[0]: "ds", df.select_dtypes(include=np.number).columns[0]: "y"})
        df_forecast["ds"] = pd.to_datetime(df_forecast["ds"], errors="coerce")
        df_forecast = df_forecast.dropna(subset=["ds"])
        model = Prophet()
        model.fit(df_forecast)
        future = model.make_future_dataframe(periods=30)
        forecast = model.predict(future)
        fig_forecast = px.line(forecast, x="ds", y="yhat", title="Predicción de tendencia 30 días")
        fig_forecast.update_layout(template="plotly_dark",
                                   plot_bgcolor="rgba(0,0,0,0)",
                                   paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_forecast, use_container_width=True)
    except Exception as e:
        st.error(f"No se pudo generar la predicción: {e}")

else:
    st.info("Sube un archivo para comenzar el análisis.")

