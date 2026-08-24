import pandas as pd
import numpy as np
from sqlalchemy import create_engine
import os
import streamlit as st
import plotly.express as px

def connect_db(db_type):
    uri = os.getenv(db_type.upper().replace(" ","")+"_URI")
    if not uri:
        st.error(f"No hay URI configurada para {db_type}")
        return None
    try:
        engine = create_engine(uri)
        return engine
    except Exception as e:
        st.error(f"Error conectando a {db_type}: {e}")
        return None

def auto_clean(df, mode="auto"):
    df2 = df.copy()
    df2.columns = [str(c).strip() for c in df2.columns]
    date_col = None
    for col in df2.columns:
        try:
            parsed = pd.to_datetime(df2[col], errors="coerce")
            if parsed.notna().sum() / len(parsed) > 0.35:
                date_col = col
                df2[col] = parsed
                break
        except:
            continue
    for c in df2.columns:
        df2[c] = pd.to_numeric(df2[c], errors="ignore")
    if mode == "auto":
        df2 = df2.dropna(how="all")
    return df2, date_col

def kpi_cards(df, kpi):
    series = pd.to_numeric(df[kpi], errors="coerce").dropna()
    if series.empty:
        st.warning("No hay datos válidos para KPI seleccionado")
        return
    latest = series.iloc[-1]
    avg30 = series.tail(30).mean()
    change = (latest - avg30) / (avg30 + 1e-9)
    c1, c2, c3 = st.columns(3)
    c1.metric("Valor actual", f"{latest:,.0f}")
    c2.metric("Promedio (últ. 30)", f"{avg30:,.0f}")
    c3.metric("Cambio vs promedio", f"{change*100:+.1f}%")

def forecast(df, date_col, kpi):
    try:
        model_df = df[[date_col, kpi]].dropna().rename(columns={date_col:"ds", kpi:"y"})
        from prophet import Prophet
        m = Prophet()
        m.fit(model_df)
        future = m.make_future_dataframe(periods=30)
        forecast = m.predict(future)
        fig = px.line(forecast, x="ds", y="yhat", title=f"Predicción 30 días — {kpi}", markers=True,
                      template="plotly_dark", color_discrete_sequence=["#ff006e"])
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error(f"No se pudo generar predicción: {e}")
