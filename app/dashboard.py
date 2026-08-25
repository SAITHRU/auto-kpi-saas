import sys, os
sys.path.append(os.path.dirname(__file__))

import streamlit as st
import pandas as pd
import numpy as np
from utils import auto_clean, kpi_cards, connect_db, suggest_kpis, strategy_ai
import plotly.express as px
import plotly.graph_objects as go
from prophet import Prophet

st.set_page_config(page_title="Auto KPI SaaS v4", layout="wide")

st.title("🚀 Auto KPI SaaS v4")
st.caption("Panel holográfico interactivo con análisis experto, alertas y visuales dinámicos.")

uploaded_file = st.file_uploader("📂 Sube tu archivo Excel/CSV", type=["csv", "xlsx"])

if uploaded_file:
    df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith(".csv") else pd.read_excel(uploaded_file)
    df, corrections = auto_clean(df)

    if corrections:
        with st.expander("🧹 Correcciones realizadas"):
            st.dataframe(pd.DataFrame(corrections), use_container_width=True)

    st.subheader("💎 KPIs holográficos")
    kpi_cards(df)

    st.subheader("📊 Visualización avanzada")
    num_cols = df.select_dtypes(include=np.number).columns
    cat_cols = df.select_dtypes(exclude=np.number).columns

    if len(num_cols) > 0:
        for col in num_cols[:3]:
            st.markdown(f"### 🔹 {col}")
            tipo = st.selectbox(f"Tipo de gráfico para {col}", ["Barras", "Torta", "Embudo", "Medidor"], key=col)

            if tipo == "Barras" and len(cat_cols) > 0:
                cat = cat_cols[0]
                resumen = df.groupby(cat)[col].mean().reset_index()
                fig = px.bar(resumen, x=cat, y=col, color=cat, text_auto=True,
                             title=f"Promedio de {col} por {cat}")
            elif tipo == "Torta" and len(cat_cols) > 0:
                cat = cat_cols[0]
                resumen = df.groupby(cat)[col].mean().reset_index()
                fig = px.pie(resumen, names=cat, values=col, title=f"Distribución de {col}")
            elif tipo == "Embudo" and len(cat_cols) > 0:
                cat = cat_cols[0]
                resumen = df.groupby(cat)[col].mean().reset_index()
                fig = px.funnel(resumen, x=cat, y=col, title=f"Embudo de {col}")
            else:
                valor = df[col].mean()
                fig = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=valor,
                    title={"text": f"Nivel promedio de {col}"},
                    gauge={"axis": {"range": [None, df[col].max()]},
                           "bar": {"color": "cyan"},
                           "steps": [
                               {"range": [0, df[col].mean()/2], "color": "red"},
                               {"range": [df[col].mean()/2, df[col].mean()], "color": "yellow"},
                               {"range": [df[col].mean(), df[col].max()], "color": "green"}]}))
            st.plotly_chart(fig, use_container_width=True)

    st.subheader("🚨 Alertas automáticas")
    for col in num_cols[:3]:
        avg = df[col].mean()
        maxv = df[col].max()
        if avg < maxv * 0.3:
            st.error(f"⚠️ Alerta crítica: el KPI **{col}** está por debajo del 30 % del máximo.")
        elif avg < maxv * 0.6:
            st.warning(f"🟡 Atención: el KPI **{col}** muestra tendencia descendente.")
        else:
            st.success(f"🟢 OK: el KPI **{col}** mantiene buen desempeño.")

    st.subheader("🔮 Predicción 30 días")
    try:
        df_forecast = df[[df.columns[0], num_cols[0]]].rename(columns={df.columns[0]: "ds", num_cols[0]: "y"})
        df_forecast["ds"] = pd.to_datetime(df_forecast["ds"], errors="coerce")
        df_forecast = df_forecast.dropna(subset=["ds"])
        model = Prophet()
        model.fit(df_forecast)
        future = model.make_future_dataframe(periods=30)
        forecast = model.predict(future)
        fig_forecast = px.line(forecast, x="ds", y="yhat", title="Predicción de tendencia 30 días")
        st.plotly_chart(fig_forecast, use_container_width=True)
    except Exception as e:
        st.error(f"No se pudo generar la predicción: {e}")

    st.subheader("🧠 Estrategia sugerida por IA")
    st.markdown(strategy_ai(df))

else:
    st.info("Sube un archivo para comenzar el análisis.")

    st.subheader("🧭 Decisiones sugeridas por IA")
    from utils import decision_ai
    decisions = decision_ai(df)
    st.markdown(decisions)
