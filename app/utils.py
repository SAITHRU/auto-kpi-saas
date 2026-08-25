import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from prophet import Prophet

def auto_clean(df):
    if df is None or df.empty:
        return pd.DataFrame(), []
    corrections = []
    for col in df.columns:
        vacíos = df[col].isnull().sum()
        if vacíos > 0:
            corrections.append({"Columna": col, "Corrección": f"{vacíos} valores vacíos rellenados"})
    df = df.replace(['N/A', 'null', 'NaN', '', 'None'], np.nan)
    df = df.fillna(method='ffill').fillna(method='bfill')
    return df, corrections

def analyze_business(df):
    num_cols = df.select_dtypes(include=np.number).columns
    if len(num_cols) == 0:
        return "⚠️ No se encontraron KPIs numéricos para análisis."
    avg = df[num_cols].mean().mean()
    dispersion = df[num_cols].std().mean()
    if avg < dispersion:
        return "📉 Alta variabilidad y bajo rendimiento → estandarizar procesos críticos y automatizar validaciones."
    elif avg > dispersion * 2:
        return "📈 Estabilidad y eficiencia → escalar el modelo operativo y explorar nuevos mercados."
    else:
        return "⚖️ Rendimiento moderado → optimizar recursos y revisar indicadores de cumplimiento."

def executive_summary(df):
    if df is None or df.empty:
        return "⚠️ No hay datos suficientes para generar un resumen ejecutivo."
    num_cols = df.select_dtypes(include=np.number).columns
    resumen = []
    resumen.append("📑 **Resumen Ejecutivo**")
    resumen.append(f"- Se analizaron {len(df)} registros con {len(df.columns)} variables.")
    if len(num_cols) > 0:
        resumen.append(f"- Rendimiento promedio de KPIs numéricos: {round(df[num_cols].mean().mean(),2)}.")
        resumen.append(f"- Variabilidad promedio: {round(df[num_cols].std().mean(),2)}.")
    resumen.append("💡 Recomendación: priorizar automatización, control de riesgos y expansión en áreas de alto desempeño.")
    return "\n".join(resumen)

def generate_kpi(df, name):
    num_cols = df.select_dtypes(include=np.number).columns
    if len(num_cols) == 0:
        return f"{name} = No se encontraron datos numéricos", go.Figure()
    formula = f"{name} = promedio({num_cols[0]}) / total_registros"
    # Selección automática de gráfico según columnas
    if len(num_cols) >= 2:
        chart = px.scatter(df, x=num_cols[0], y=num_cols[1], title=f"KPI generado: {name}")
    elif len(num_cols) == 1:
        chart = go.Figure(go.Indicator(
            mode="gauge+number",
            value=df[num_cols[0]].mean(),
            title={"text": f"KPI generado: {name}"},
            gauge={"axis": {"range": [None, df[num_cols[0]].max()]},
                   "bar": {"color": "cyan"},
                   "steps": [
                       {"range": [0, df[num_cols[0]].mean()/2], "color": "red"},
                       {"range": [df[num_cols[0]].mean()/2, df[num_cols[0]].mean()], "color": "yellow"},
                       {"range": [df[num_cols[0]].mean(), df[num_cols[0]].max()], "color": "green"}]}))
    else:
        chart = px.histogram(df, title=f"KPI generado: {name}")
    return formula, chart

def predict_future(df):
    num_cols = df.select_dtypes(include=np.number).columns
    if len(num_cols) == 0:
        return go.Figure()
    df_forecast = df[[df.columns[0], num_cols[0]]].rename(
        columns={df.columns[0]: "ds", num_cols[0]: "y"})
    df_forecast["ds"] = pd.to_datetime(df_forecast["ds"], errors="coerce")
    df_forecast = df_forecast.dropna(subset=["ds"])
    model = Prophet()
    model.fit(df_forecast)
    future = model.make_future_dataframe(periods=30)
    forecast = model.predict(future)
    fig = px.line(forecast, x="ds", y="yhat", title="Predicción de tendencia 30 días")
    return fig

def decision_ai(df):
    if df is None or df.empty:
        return "⚠️ No hay datos suficientes para generar decisiones."
    num_cols = df.select_dtypes(include=np.number).columns
    insights = []
    for col in num_cols[:3]:
        avg_val = df[col].mean()
        max_val = df[col].max()
        if avg_val < max_val * 0.4:
            insights.append(f"🔴 **{col}** crítico → reasignar recursos
