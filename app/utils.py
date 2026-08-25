import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from prophet import Prophet

def auto_clean(df):
    if df is None or df.empty:
        st.error("❌ El archivo está vacío o no se pudo leer correctamente.")
        return pd.DataFrame(), []
    corrections = []
    for col in df.columns:
        vacíos = df[col].isnull().sum()
        if vacíos > 0:
            corrections.append({"Columna": col, "Corrección": f"{vacíos} valores vacíos rellenados"})
    df = df.fillna(method='ffill').fillna(method='bfill')
    return df, corrections

def analyze_business(df):
    num_cols = df.select_dtypes(include=np.number).columns
    avg = df[num_cols].mean().mean()
    dispersion = df[num_cols].std().mean()
    if avg < dispersion:
        return "📉 La operación muestra alta variabilidad y bajo rendimiento. Recomendación: estandarizar procesos críticos y automatizar validaciones."
    elif avg > dispersion * 2:
        return "📈 El negocio mantiene estabilidad y eficiencia. Recomendación: escalar el modelo operativo y explorar nuevos mercados."
    else:
        return "⚖️ Rendimiento moderado. Recomendación: optimizar recursos y revisar indicadores de cumplimiento."

def generate_kpi(df, name):
    num_cols = df.select_dtypes(include=np.number).columns
    formula = f"{name} = promedio({num_cols[0]}) / total_registros"
    chart = px.line(df, y=num_cols[0], title=f"KPI generado: {name}")
    return formula, chart

def predict_future(df):
    df_forecast = df[[df.columns[0], df.select_dtypes(include=np.number).columns[0]]].rename(
        columns={df.columns[0]: "ds", df.select_dtypes(include=np.number).columns[0]: "y"})
    df_forecast["ds"] = pd.to_datetime(df_forecast["ds"], errors="coerce")
    df_forecast = df_forecast.dropna(subset=["ds"])
    model = Prophet()
    model.fit(df_forecast)
    future = model.make_future_dataframe(periods=30)
    forecast = model.predict(future)
    fig = px.line(forecast, x="ds", y="yhat", title="Predicción de tendencia 30 días")
    return fig

def connect_db():
    st.info("🔑 Configura tus credenciales en Secrets para conectar bases de datos.")

