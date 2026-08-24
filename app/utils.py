import streamlit as st
import pandas as pd
import numpy as np
from prophet import Prophet

def auto_clean(df):
    issues = []
    for col in df.columns:
        if df[col].isnull().sum() > 0:
            issues.append(f"Columna '{col}' tiene {df[col].isnull().sum()} valores vacíos.")
        if df[col].dtype == 'object':
            try:
                pd.to_numeric(df[col])
            except Exception:
                issues.append(f"Columna '{col}' contiene texto no numérico.")

    if issues:
        st.warning("⚠️ Se detectaron posibles problemas en el archivo:")
        for i in issues:
            st.write("-", i)
        st.info("Por favor, completa los datos faltantes para mejorar el cálculo de KPIs.")

    df = df.replace(['N/A', 'null', 'NaN', ''], np.nan)
    df = df.fillna(method='ffill').fillna(method='bfill')
    return df

def kpi_cards(df):
    st.metric("Número de registros", len(df))
    if df.select_dtypes(include=np.number).shape[1] > 0:
        st.metric("Promedio KPI", round(df.select_dtypes(include=np.number).mean().mean(), 2))

def forecast(df):
    if df.shape[1] >= 2:
        try:
            df_forecast = df[[df.columns[0], df.columns[1]]].rename(columns={df.columns[0]: "ds", df.columns[1]: "y"})
            model = Prophet()
            model.fit(df_forecast)
            future = model.make_future_dataframe(periods=30)
            forecast = model.predict(future)
            st.line_chart(forecast[["ds", "yhat"]].set_index("ds"))
        except Exception as e:
            st.error(f"No se pudo generar la predicción: {e}")

def connect_db():
    st.info("🔑 Configura tus credenciales en Secrets para conectar bases de datos.")

