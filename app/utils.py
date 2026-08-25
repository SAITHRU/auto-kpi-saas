import streamlit as st
import pandas as pd
import numpy as np

def auto_clean(df):
    corrections = []
    for col in df.columns:
        vacíos = df[col].isnull().sum()
        if vacíos > 0:
            corrections.append({"Columna": col, "Corrección": f"{vacíos} valores vacíos rellenados"})
    df = df.fillna(method='ffill').fillna(method='bfill')
    return df, corrections

def kpi_cards(df):
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("👥 Registros totales", len(df))
    with col2:
        st.metric("💰 Promedio general", round(df.select_dtypes(include=np.number).mean().mean(), 2))
    with col3:
        st.metric("📊 Columnas analizadas", len(df.columns))

def suggest_kpis(df):
    num_cols = df.select_dtypes(include=np.number).columns
    return [{"KPI sugerido": col, "Promedio": round(df[col].mean(), 2)} for col in num_cols]

def strategy_ai(df):
    insights = []
    num_cols = df.select_dtypes(include=np.number).columns
    for col in num_cols[:3]:
        avg, maxv, minv = df[col].mean(), df[col].max(), df[col].min()
        if avg > maxv * 0.7:
            insights.append(f"📈 **{col}** alto rendimiento → mantener estrategia actual y explorar expansión.")
        elif avg < maxv * 0.4:
            insights.append(f"📉 **{col}** bajo rendimiento → revisar causas raíz y reasignar recursos.")
        else:
            insights.append(f"⚖️ **{col}** estable → monitorear y ajustar según tendencia.")
    return "\n".join(insights)

def connect_db():
    st.info("🔑 Configura tus credenciales en Secrets para conectar bases de datos.")
