import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from prophet import Prophet
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv
from app.utils import auto_clean, kpi_cards, forecast, connect_db

st.set_page_config(page_title="Auto KPI SaaS v2", layout="wide")

load_dotenv()

st.title("Auto KPI SaaS v2 — Panel Power BI Moderno")

source = st.sidebar.selectbox("Fuente de datos", ["Excel/CSV","PostgreSQL","MySQL","SQL Server","BigQuery"])
mode = st.sidebar.radio("Modo limpieza", ["Automático","Con autorización"])

df = None
date_col = None

if source == "Excel/CSV":
    file = st.file_uploader("Sube archivo Excel/CSV", type=["xlsx","csv"])
    if file:
        try:
            if file.name.endswith(".xlsx"):
                df = pd.read_excel(file)
            else:
                df = pd.read_csv(file)
            df, date_col = auto_clean(df, "auto" if mode=="Automático" else "manual")
        except Exception as e:
            st.error(f"Error leyendo archivo: {e}")
else:
    engine = connect_db(source)
    if engine:
        query = st.text_area("Escribe tu consulta SQL")
        if st.button("Ejecutar consulta"):
            try:
                df = pd.read_sql(query, engine)
                df, date_col = auto_clean(df, "auto" if mode=="Automático" else "manual")
            except Exception as e:
                st.error(f"Error ejecutando consulta: {e}")

if df is not None:
    st.subheader("Vista previa de datos")
    st.dataframe(df.head(20))

    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    if numeric_cols:
        kpi = st.selectbox("Selecciona KPI", numeric_cols)
        kpi_cards(df, kpi)

        if date_col:
            st.subheader("Serie temporal")
            fig = px.line(df, x=date_col, y=kpi, title=f"{kpi} — Serie temporal",
                          template="plotly_dark", markers=True,
                          color_discrete_sequence=["#00f5d4"])
            st.plotly_chart(fig, use_container_width=True)

            st.subheader("Predicción")
            forecast(df, date_col, kpi)

        st.subheader("Mapa de correlación")
        corr = df[numeric_cols].corr()
        fig_corr = px.imshow(corr, text_auto=True, aspect="auto",
                             title="Correlación entre KPIs",
                             template="plotly_dark",
                             color_continuous_scale="Viridis")
        st.plotly_chart(fig_corr, use_container_width=True)

    st.subheader("Resumen ejecutivo")
    st.write(f"- KPI principal: {kpi}")
    st.write("- Tendencia detectada y predicción mostrada arriba.")
    st.write("- Drivers correlacionados resaltados en el mapa de correlación.")
    st.write("- Recomendación: actuar sobre los drivers con mayor correlación positiva.")
