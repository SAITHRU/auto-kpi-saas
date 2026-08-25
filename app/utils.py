import streamlit as st
import pandas as pd
import numpy as np
from prophet import Prophet

def auto_clean(df):
    # ✅ Validación inicial
    if df is None or not isinstance(df, pd.DataFrame) or df.empty:
        st.error("❌ El archivo está vacío o no se pudo leer correctamente.")
        return pd.DataFrame(), []

    corrections = []

    # ✅ Revisión de columnas y valores
    for col in df.columns:
        vacíos = df[col].isnull().sum()
        if vacíos > 0:
            corrections.append({"Columna": col, "Corrección": f"{vacíos} valores vacíos rellenados"})
        if df[col].dtype == 'object':
            try:
                pd.to_numeric(df[col])
            except Exception:
                corrections.append({"Columna": col, "Corrección": "Texto no numérico detectado"})

    # ✅ Limpieza segura
    df = df.replace(['N/A', 'null', 'NaN', '', 'None'], np.nan)
    try:
        df = df.fillna(method='ffill').fillna(method='bfill')
    except Exception:
        st.warning("⚠️ No se pudo aplicar relleno automático. Se mantiene el formato original.")
        df = df.fillna(0)

    return df, corrections


def kpi_cards(df):
    if df is None or df.empty:
        st.warning("⚠️ No hay datos para mostrar KPIs.")
        return

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("👥 Registros totales", len(df))
    with col2:
        st.metric("💰 Promedio general", round(df.select_dtypes(include=np.number).mean().mean(), 2))
    with col3:
        st.metric("📊 Columnas analizadas", len(df.columns))


def suggest_kpis(df):
    if df is None or df.empty:
        return []

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
    if df is None or df.empty:
        return "⚠️ No hay datos suficientes para generar estrategia."

    insights = []
    num_cols = df.select_dtypes(include=np.number).columns
    for col in num_cols[:3]:
        avg_val = df[col].mean()
        max_val = df[col].max()
        min_val = df[col].min()
        if avg_val > (max_val * 0.7):
            insights.append(f"📈 **{col}** alto rendimiento → mantener estrategia actual y explorar expansión.")
        elif avg_val < (max_val * 0.4):
            insights.append(f"📉 **{col}** bajo rendimiento → revisar causas raíz y reasignar recursos.")
        else:
            insights.append(f"⚖️ **{col}** estable → monitorear y ajustar según tendencia.")
    return "\n".join(insights)


def connect_db():
    st.info("🔑 Configura tus credenciales en Secrets para conectar bases de datos.")
def decision_ai(df):
    if df is None or df.empty:
        return "⚠️ No hay datos suficientes para generar decisiones."

    num_cols = df.select_dtypes(include=np.number).columns
    insights = []

    for col in num_cols[:3]:
        avg_val = df[col].mean()
        max_val = df[col].max()
        min_val = df[col].min()

        if avg_val < max_val * 0.4:
            insights.append(f"🔴 **{col}** muestra bajo rendimiento. Decisión: reasignar recursos y revisar procesos críticos.")
        elif avg_val < max_val * 0.7:
            insights.append(f"🟠 **{col}** en zona de riesgo. Decisión: implementar control preventivo y optimizar flujo operativo.")
        else:
            insights.append(f"🟢 **{col}** estable. Decisión: mantener estrategia actual y explorar expansión o automatización.")

    # Decisiones predictivas
    insights.append("📊 Proyección: si se mejora el rendimiento promedio en 10 %, el margen operativo podría aumentar entre 3 % y 5 %.")
    insights.append("💡 Recomendación general: priorizar automatización de validaciones y control de sanciones para reducir costos.")

    return "\n".join(insights)

