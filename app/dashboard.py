import streamlit as st
import pandas as pd
import numpy as np
from utils import auto_clean, kpi_cards, forecast, connect_db, suggest_kpis
import plotly.express as px
from prophet import Prophet

st.set_page_config(page_title="Auto KPI SaaS v3", layout="wide")

st.title("🚀 Auto KPI SaaS v3")
st.caption("Panel holográfico tipo Power BI con análisis estratégico, comparativas y predicciones inteligentes.")

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

    # KPIs principales
    st.subheader("💎 KPIs holográficos")
    kpi_cards(df)

    # Sugerencias IA
    st.subheader("🤖 Sugerencias automáticas de KPIs")
    suggested = suggest_kpis(df)
    st.dataframe(pd.DataFrame(suggested), use_container_width=True)

    # Layout lateral tipo Power BI
    st.subheader("📊 Análisis estratégico")
    num_cols = df.select_dtypes(include=np.number).columns
    cat_cols = df.select_dtypes(exclude=np.number).columns

    if len(num_cols) > 0:
        for col in num_cols[:3]:  # máximo 3 KPIs para claridad
            st.markdown(f"### 🔹 {col}")
            left, right = st.columns([2, 1])

            with left:
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
                else:
                    st.warning("No se detectaron columnas categóricas para segmentar este KPI.")

            with right:
                max_val = df[col].max()
                min_val = df[col].min()
                avg_val = df[col].mean()
                st.metric("📈 Máximo", round(max_val, 2))
                st.metric("📉 Mínimo", round(min_val, 2))
                st.metric("⚖️ Promedio", round(avg_val, 2))
                st.info(f"💡 La IA sugiere revisar el KPI **{col}**: su variación indica oportunidad de mejora.")

    # Comparativa general
    st.subheader("📊 Comparativa entre KPIs")
    if len(num_cols) > 1:
        comp_df = df[num_cols]
        fig_comp = px.scatter_matrix(comp_df, dimensions=num_cols[:4], title="Comparativa entre KPIs")
        fig_comp.update_layout(template="plotly_dark",
                               plot_bgcolor="rgba(0,0,0,0)",
                               paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_comp, use_container_width=True)

    # Predicción 30 días
    st.subheader("🔮 Predicción 30 días")
    try:
        df_forecast = df[[df.columns[0], df.select_dtypes(include=np.number).columns[0]]].rename(
            columns={df.columns[0]: "ds", df.select_dtypes(include=np.number).columns[0]: "y"})
        df_forecast["ds"] = pd.to_datetime(df_forecast["ds"], errors="coerce")
        df_forecast = df_forecast.dropna(subset=["ds"])
        model
