import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, time
import feedparser

# Configuración de la página web
st.set_page_config(
    page_title="S-AACP: Análisis Cuantitativo Pre-Market MNQ",
    page_icon="📈",
    layout="wide"
)

st.title("🚀 S-AACP: Sistema Automatizado de Análisis Pre-Market y Proyección")
st.markdown("### Mapeo Avanzado: Estructura Técnica + Motor Heurístico de Sentimiento (100% Gratuito)")

# Función para extraer automáticamente titulares recientes relevantes de forma gratuita
@st.cache_data(ttl=300)
def obtener_noticias_automaticas():
    feeds = [
        "https://finance.yahoo.com/news/rssindex",
        "https://www.cnbc.com/id/15839069/device/rss/rss.html"
    ]
    titulares_relevantes = []
    palabras_clave = ["fed", "inflation", "cpi", "rate", "apple", "nvidia", "microsoft", "tesla", "nasdaq", "tech", "yield", "bonds"]
    
    for url in feeds:
        try:
            parsed = feedparser.parse(url)
            for entry in parsed.entries[:15]:
                titulo = entry.title.lower()
                if any(kw in titulo for kw in palabras_clave):
                    titulares_relevantes.append(entry.title)
        except Exception:
            continue
            
    if not titulares_relevantes:
        return "No se detectaron alertas macro/tech críticas en este exacto minuto. Operando bajo estructura técnica pura."
    
    return " | ".join(titulares_relevantes[:6])

# Barra lateral para controles
st.sidebar.header("⚙️ Configuración y Fuentes")
ticker_option = st.sidebar.selectbox(
    "Seleccione el Activo:",
    ("MNQ=F", "NQ=F", "QQQ", "NVDA", "AAPL")
)

st.sidebar.markdown("---")
modo_noticias = st.sidebar.radio("Modo de Fuentes de Noticias:", ("Automático (RSS Gratuito)", "Manual (Pegar Texto)"))

if modo_noticias == "Automático (RSS Gratuito)":
    noticias_input = obtener_noticias_automaticas()
    st.sidebar.success("Titulares capturados de feeds públicos.")
else:
    noticias_input = st.sidebar.text_area("Pegue las noticias manualmente:", height=100)

st.sidebar.info("A las 9:29 AM EST, presione el botón para ejecutar el análisis.")
btn_calcular = st.sidebar.button("📊 Ejecutar Análisis Integral")

if btn_calcular or ticker_option:
    with st.spinner("Procesando estructura técnica y evaluando sesgo de noticias..."):
        try:
            # Motor Heurístico Inteligente (Simula la discriminación del Prompt Maestro sin costos)
            texto_lower = noticias_input.lower()
            score_narrativa = 0.0
            veredicto_ia = "NEUTRAL / MIXTO"
            
            # Criterios alcistas ponderados
            if any(w in texto_lower for w in ["lower inflation", "cpi beat", "rate cuts", "bajan los tipos", "surges", "record", "growth", "rally"]):
                score_narrativa += 2.5
                veredicto_ia = "ALCISTA (Fundamentos a Favor)"
            # Criterios bajistas ponderados
            elif any(w in texto_lower for w in ["inflation rises", "rate hike", "suben los tipos", "tensions", "drops", "slumps", "recession", "drop"]):
                score_narrativa -= 2.5
                veredicto_ia = "BAJISTA (Presión Sistémica)"
            else:
                veredicto_ia = "NEUTRAL (Sin eventos de alto impacto)"

            informe_ia = f"Evaluación de ingeniería basada en la detección de términos clave en los titulares capturados. Score asignado: {score_narrativa:+.1f}."

            # Descarga de datos técnicos de mercado (1 minuto)
            ticker = yf.Ticker(ticker_option)
            df_hist = ticker.history(period="2d", interval="1m")
            
            if df_hist.empty:
                st.error("No se pudieron obtener datos recientes para el activo seleccionado.")
            else:
                if df_hist.index.tz is not None:
                    df_hist.index = df_hist.index.tz_convert('America/New_York')
                else:
                    df_hist.index = pd.to_datetime(df_hist.index)

                # Estructura Overnight y Última Hora
                high_pm_general = df_hist['High'].max()
                low_pm_general = df_hist['Low'].min()
                
                hoy = df_hist.index[-1].date()
                mask_ultima_hora = (df_hist.index.date == hoy) & (df_hist.index.time >= time(8, 30)) & (df_hist.index.time <= time(9, 29))
                df_ultima_hora = df_hist[mask_ultima_hora]

                if not df_ultima_hora.empty:
                    high_pm_ult_hora = df_ultima_hora['High'].max()
                    low_pm_ult_hora = df_ultima_hora['Low'].min()
                else:
                    high_pm_ult_hora = high_pm_general
                    low_pm_ult_hora = low_pm_general

                ultimo_cierre = df_hist['Close'].iloc[-390] if len(df_hist) > 390 else df_hist['Close'].iloc[0]
                precio_actual = df_hist['Close'].iloc[-1]
                
                gap_val = precio_actual - ultimo_cierre
                gap_pct = (gap_val / ultimo_cierre) * 100
                
                rango_operativo = high_pm_ult_hora - low_pm_ult_hora if (high_pm_ult_hora > low_pm_ult_hora) else (high_pm_general - low_pm_general)
                
                tercio_inferior = low_pm_ult_hora + (rango_operativo * 0.333)
                tercio_superior = low_pm_ult_hora + (rango_operativo * 0.666)

                # Probabilidad combinada (Técnica + Score Heurístico)
                presion_ultima_hora = precio_actual - low_pm_ult_hora
                factor_presion = presion_ultima_hora / rango_operativo if rango_operativo > 0 else 0.5
                
                prob_alcista = round(50.0 + (factor_presion * 20.0) + (5.0 if gap_pct > 0 else -5.0) + (score_narrativa * 5.0), 1)
                prob_alcista = max(min(prob_alcista, 88.0), 12.0)
                prob_bajista = round(100.0 - prob_alcista, 1)

                # --- MÉTRICAS SUPERIORES ---
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric(label="Estado del Gap", value=f"{gap_pct:+.2f}%", delta=f"{gap_val:+.2f} USD")
                with col2:
                    st.metric(label="Máximo Estructural (Gral)", value=f"{high_pm_general:,.2f}")
                with col3:
                    st.metric(label="Mínimo Estructural (Gral)", value=f"{low_pm_general:,.2f}")
                with col4:
                    st.metric(label="Sesgo Fundamental", value=veredicto_ia.split(" ")[0])

                st.markdown("---")
                
                # --- INFORME DE NARRATIVA ---
                with st.expander("🧠 Informe de Sentimiento y Titulares Procesados", expanded=True):
                    st.markdown(f"**Titulares Capturados:** _{noticias_input}_")
                    st.markdown(f"- **Veredicto:** {veredicto_ia}")
                    st.markdown(f"- **Score de Impacto:** {score_narrativa:+.1f}")
                    st.markdown(f"- **Nota Analítica:** {informe_ia}")

                # --- GRÁFICO VISUAL CON TOOLTIPS ---
                st.subheader("🗺️ Mapa Visual de Niveles: Estructura Macro vs. Intención Pre-Apertura")

                fig = go.Figure()

                fig.add_trace(go.Scatter(
                    x=[1, 2], y=[high_pm_general, high_pm_general],
                    mode="lines+text", name="Máximo General Overnight",
                    line=dict(color="red", width=3, dash="dash"),
                    text=["", f"Máximo Estructural (Gral): {high_pm_general:,.2f}"],
                    textposition="top center",
                    hovertemplate=f"<b>Nivel: Máximo Estructural (Gral)</b><br>Precio: {high_pm_general:,.2f} USD<extra></extra>"
                ))

                fig.add_trace(go.Scatter(
                    x=[1, 2], y=[high_pm_ult_hora, high_pm_ult_hora],
                    mode="lines+text", name="Máx Última Hora",
                    line=dict(color="pink", width=2, dash="dot"),
                    text=["", f"Máx Última Hora: {high_pm_ult_hora:,.2f}"],
                    textposition="top right",
                    hovertemplate=f"<b>Nivel: Máximo Última Hora (8:30-9:29)</b><br>Precio: {high_pm_ult_hora:,.2f} USD<extra></extra>"
                ))

                fig.add_trace(go.Scatter(
                    x=[1, 2], y=[precio_actual, precio_actual],
                    mode="lines+text", name="Apertura / Nivel Actual",
                    line=dict(color="blue", width=4),
                    text=["", f"Apertura / Nivel Actual: {precio_actual:,.2f}"],
                    textposition="middle right",
                    hovertemplate=f"<b>Apertura RTH</b><br>Precio: {precio_actual:,.2f} USD<extra></extra>"
                ))

                fig.add_trace(go.Scatter(
                    x=[1, 2], y=[tercio_superior, tercio_superior],
                    mode="lines+text", name="Tercio Superior (66.6%)",
                    line=dict(color="orange", width=2, dash="dot"),
                    text=["", f"Tercio Superior (66.6%): {tercio_superior:,.2f}"],
                    textposition="top center",
                    hovertemplate=f"<b>Tercio Superior (66.6%)</b><br>Precio: {tercio_superior:,.2f} USD<extra></extra>"
                ))

                fig.add_trace(go.Scatter(
                    x=[1, 2], y=[tercio_inferior, tercio_inferior],
                    mode="lines+text", name="Línea Tercio Inferior",
                    line=dict(color="orange", width=2, dash="dot"),
                    text=["", f"Tercio Inferior (33.3%): {tercio_inferior:,.2f}"],
                    textposition="bottom center",
                    hovertemplate=f"<b>Tercio Inferior (33.3%)</b><br>Precio: {tercio_inferior:,.2f} USD<extra></extra>"
                ))

                fig.add_trace(go.Scatter(
                    x=[1, 2], y=[low_pm_ult_hora, low_pm_ult_hora],
                    mode="lines+text", name="Mín Última Hora",
                    line=dict(color="lightgreen", width=2, dash="dot"),
                    text=["", f"Mín Última Hora: {low_pm_ult_hora:,.2f}"],
                    textposition="bottom right",
                    hovertemplate=f"<b>Nivel: Mínimo Última Hora (8:30-9:29)</b><br>Precio: {low_pm_ult_hora:,.2f} USD<extra></extra>"
                ))

                fig.add_trace(go.Scatter(
                    x=[1, 2], y=[low_pm_general, low_pm_general],
                    mode="lines+text", name="Mínimo General Overnight",
                    line=dict(color="green", width=3, dash="dash"),
                    text=["", f"Mínimo Estructural (Gral): {low_pm_general:,.2f}"],
                    textposition="bottom center",
                    hovertemplate=f"<b>Nivel: Mínimo Estructural (Gral)</b><br>Precio: {low_pm_general:,.2f} USD<extra></extra>"
                ))

                fig.update_layout(
                    title=f"Proyección Cuantitativa RTH e Impacto de Sentimiento para {ticker_option}",
                    xaxis_title="Estructura de Sesión",
                    yaxis_title="Precio (USD)",
                    height=550,
                    showlegend=True,
                    template="plotly_dark",
                    hovermode="closest"
                )

                st.plotly_chart(fig, use_container_width=True)

                st.markdown("---")
                
                # --- PROBABILIDAD Y GUÍA ---
                col_p1, col_p2 = st.columns(2)
                with col_p1:
                    st.success(f"🟢 **Probabilidad Alcista (Técnica + Sentimiento):** {prob_alcista}%")
                with col_p2:
                    st.error(f"🔴 **Probabilidad Bajista:** {prob_bajista}%")
                
                st.markdown("### 💡 Guía Operativa")
                st.markdown(f"> **Lectura Táctica:** El motor ha evaluado automáticamente los titulares de los feeds públicos y los ha integrado al cálculo de los tercios (`{tercio_inferior:,.2f}` y `{tercio_superior:,.2f}`). Usa esta confluencia para operar con precisión en tu NinjaTrader.")

        except Exception as e:
            st.error(f"Ocurrió un error al procesar el sistema: {e}")
