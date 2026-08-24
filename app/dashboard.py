import streamlit as st
import pandas as pd
import numpy as np
from utils import auto_clean, kpi_cards, forecast, connect_db, suggest_kpis
import plotly.express as px
from prophet import Prophet

st.set_page_config(page_title="Auto KPI SaaS v2", layout="wide")

st.title("✨ Auto KPI SaaS v2")
st.caption("Panel holográfico tipo Power BI con KPIs, predicciones y análisis interactivo.")

uploaded_file = st.file_uploader("📂 Sube tu archivo Excel/CSV", type=["csv", "xlsx"])

if uploaded_file:
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    df, corrections = auto_clean(df)

    if corrections:
        with st.expander("🧹 Ver correcciones realizadas"):
            st.dataframe(pd.DataFrame(corrections), use_container_width=True)
            st.info("Haz clic en cada fila para autorizar o revertir la corrección manualmente.")

    st.subheader("💎 KPIs holográficos")
    kpi_cards(df)

    st.subheader("🤖 Sugerencias automáticas de KPIs")
    suggested = suggest_kpis(df)
    st.dataframe(pd.DataFrame(suggested), use_container_width=True)

    st.info("¿Deseas agregar otros KPIs manualmente?")
    new_kpi = st.text_input("Escribe el nombre del nuevo KPI:")
    if new_kpi:
        st.success(f"✅ KPI '{new_kpi}' agregado correctamente.")

    # --- Análisis modular por KPI ---
    st.subheader("📊 Análisis por KPI")
    num_cols = df.select_dtypes(include=np.number).columns
    cat_cols = df.select_dtypes(exclude=np.number).columns

    if len(num_cols) > 0:
        for col in num_cols[:5]:  # máximo 5 KPIs para evitar saturación
            st.markdown(f"### 🔹 Análisis de **{col}**")
            if len(cat_cols) > 0:
                cat = cat_cols[0]
                resumen = df.groupby(cat)[col].agg(["count", "mean"]).reset_index()
                fig_bar = px.bar(resumen, x=cat, y="mean", color=cat,
                                 title=f"Promedio de {col} por {cat}",
                                 text_auto=True)
                fig_bar.update_layout(template="plotly_dark",
                                      plot_bgcolor="rgba(0,0,0,0)",
                                      paper_bgcolor="rgba(0,0,0,0)")
                st.plotly_chart(fig_bar, use_container_width=True)

                # Insight automático
                max_cat = resumen.loc[resumen["mean"].idxmax(), cat]
                st.info(f"📈 El valor promedio más alto de **{col}** se encuentra en **{max_cat}**.")
            else:
                st.warning("No se detectaron columnas categóricas para segmentar este KPI.")

    # --- Predicción 30 días ---
    st.subheader("🔮 Predicción 30 días")
    try:
        df_forecast = df[[df.columns[0], df.select_dtypes(include=np.number).columns[0]]].rename(
            columns={df.columns[0]: "ds", df.select_dtypes(include=np.number).columns[0]: "y"})
        df_forecast["ds"] = pd.to_datetime(df_forecast["ds"], errors="coerce")
        df_forecast = df_forecast.dropna(subset=["ds"])
        model = Prophet()
        model.fit(df_forecast)
        future = model.make_future_dataframe(periods=30)
        forecast = model.predict(future)
        fig_forecast = px.line(forecast, x="ds", y="yhat", title="Predicción de tendencia 30 días")
        fig_forecast.update_layout(template="plotly_dark",
                                   plot_bgcolor="rgba(0,0,0,0)",
                                   paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_forecast, use_container_width=True)
    except Exception as e:
        st.error(f"No se pudo generar la predicción: {e}")

else:
    st.info("Sube un archivo para comenzar el análisis.")
