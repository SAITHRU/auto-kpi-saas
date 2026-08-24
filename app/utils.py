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
        st.metric("👥 Empleados activos", len(df))
    with col2:
        st.metric("💵 Total salarios", f"${df.select_dtypes(include=np.number).sum().sum():,.0f}")
    with col3:
        st.metric("📊 Columnas analizadas", len(df.columns))

def forecast(df):
    if df.shape[1] >= 2:
        try:
            df_forecast = df[[df.columns[0], df.columns[1]]].rename(columns={df.columns[0]: "ds", df.columns[1]: "y"})
            df_forecast["ds"] = pd.to_datetime(df_forecast["ds"], errors="coerce")
            df_forecast = df_forecast.dropna(subset=["ds"])
            model = Prophet()
            model.fit(df_forecast)
            future = model.make_future_dataframe(periods=30)
            forecast = model.predict(future)
            st.line_chart(forecast[["ds", "yhat"]].set_index("ds"))
        except Exception as e:
            st.error(f"No se pudo generar la predicción: {e}")

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

def connect_db():
    st.info("🔑 Configura tus credenciales en Secrets para conectar bases de datos.")

