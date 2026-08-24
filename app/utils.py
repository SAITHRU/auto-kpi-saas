import streamlit as st
import pandas as pd
import numpy as np
from prophet import Prophet

def auto_clean(df):
    corrections = []
    if df is None or df.empty:
        st.error("❌ El archivo está vacío o no se pudo leer correctamente.")
        return pd.DataFrame(), corrections

    for col in df.columns:
        vacíos = df[col].isnull().sum()
        if vacíos > 0:
            corrections.append({"Columna": col, "Corrección": f"{vacíos} valores vacíos rellenados"})
        if df[col].dtype == 'object':
            try:
                pd.to_numeric(df[col])
            except Exception:
                corrections.append({"Columna": col, "Corrección": "Texto no numérico detectado"})

    df = df.replace(['N/A', 'null', 'NaN', '', 'None'], np.nan)
    try:
        df = df.fillna(method='ffill').fillna(method='bfill')
    except Exception:
        st.warning("⚠️ No se pudo aplicar relleno automático. Se mantiene el formato original.")
        df = df.fillna(0)

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
    suggestions = []
    num_cols = df.select_dtypes(include=np.number).columns
    for col in num_cols:
        mean_val = df[col].mean()
        suggestions.append({
            "KPI sugerido": col,
            "Promedio": round(mean_val, 2),
            "Impacto estimado": "Moderado" if mean_val < df[col].max() / 2 else "Alto"
        })
    return suggestions

def strategy_ai(df):
    insights = []
    num_cols = df.select_dtypes(include=np.number).columns
    for col in num_cols[:3]:
        avg_val = df[col].mean()
        max_val = df[col].max()
        min_val = df[col].min()
        if avg_val > (max_val * 0.7):
            insights.append(f"📈 El KPI **{col}** está en niveles altos. Estrategia: mantener inversión y reforzar áreas exitosas.")
        elif avg_val < (min_val * 1.3):
            insights.append(f"📉 El KPI **{col}** está en niveles bajos. Estrategia: revisar procesos y asignar recursos adicionales.")
        else:
            insights.append(f"⚖️ El KPI **{col}** está estable. Estrategia: monitorear y ajustar según tendencias futuras.")
    return "\n".join(insights)

def connect_db():
    st.info("🔑 Configura tus credenciales en Secrets para conectar bases de datos.")

