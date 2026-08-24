import streamlit as st
import pandas as pd
import numpy as np
from prophet import Prophet

def auto_clean(df):
    if df is None or df.empty:
        st.error("❌ El archivo está vacío o no se pudo leer correctamente.")
        return pd.DataFrame()

    resumen = []
    for col in df.columns:
        vacíos = df[col].isnull().sum()
        if vacíos > 0:
            resumen.append({"Columna": col, "Valores vacíos": vacíos})
        if df[col].dtype == 'object':
            try:
                pd.to_numeric(df[col])
            except Exception:
                resumen.append({"Columna": col, "Valores vacíos": "Texto no numérico"})

    df = df.replace(['N/A', 'null', 'NaN', '', 'None'], np.nan)
    try:
        df = df.fillna(method='ffill').fillna(method='bfill')
    except Exception:
        st.warning("⚠️ No se pudo aplicar relleno automático. Se mantiene el formato original.")
        df = df.fillna(0)

    if resumen:
        st.subheader("🧹 Resumen de limpieza de datos")
        resumen_df = pd.DataFrame(resumen)
        st.dataframe(resumen_df, use_container_width=True)

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
