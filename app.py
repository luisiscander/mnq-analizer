import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, time

# Configuración de la página web
st.set_page_config(
    page_title="S-AACP: Análisis Cuantitativo Pre-Market MNQ",
    page_icon="📈",
    layout="wide"
)

st.title("🚀 S-AACP: Sistema Automatizado de Análisis Pre-Market y Proyección")
st.markdown("### Mapeo Avanzado: Estructura Técnica + Análisis de Sentimiento y Narrativa Nasdaq")

# Barra lateral para controles y entrada de noticias macro
st.sidebar.header("⚙️ Parámetros de Operación")
ticker_option = st.sidebar.selectbox(
    "Seleccione el Activo:",
    ("MNQ=F", "NQ=F", "QQQ", "NVDA", "AAPL")
)

st.sidebar.markdown("---")
st.sidebar.subheader("📰 Sentimiento Pre-Market (8:30 - 9:29 AM)")
noticias_input = st.sidebar.text_area(
    "Pegue aquí las noticias, datos macro (IPC, Empleo) o comunicados de la FED:",
    placeholder="Ej: IPC de EE.UU. sale por debajo de lo esperado; los rendimientos de los bonos bajan y las tecnológicas repuntan en el pre-market...",
    height=150
)

st.sidebar.info("A las 9:29 AM EST, presione el botón para ejecutar el motor completo.")
btn_calcular = st.sidebar.button("📊 Ejecutar Análisis Integral y Generar Mapa")

if btn_calcular or ticker_option:
    with st.spinner(f"Proyectando niveles técnicos y evaluando narrativa fundamental para {ticker_option}..."):
        try:
            # 1. Análisis básico de Sentimiento mediante palabras clave (Ingeniería de Narrativa)
            texto_lower = noticias_input.lower()
            score_narrativa = 0.0
            
            # Factores alcistas comunes en Nasdaq
            if any(w in texto_lower for w in ["menor inflación", "cpi bajo", "bajan los tipos", "recorte de tasas", "superan expectativas", "guía al alza", "liquidez"]):
                score_narrativa += 2.5
            # Factores bajistas comunes en Nasdaq
            if any(w in texto_lower for w in ["inflación alta", "suben los tipos", "temores de recesión", "guerra", "tensiones", "multa", "caída de ventas"]):
                score_narrativa -= 2.5

            if len(noticias_input.strip()) > 10:
                sentimiento_ia = "ALCISTA (Fundamentos a Favor)" if score_narrativa > 0 else ("BAJISTA (Presión Sistémica)" if score_narrativa < 0 else "NEUTRAL / MIXTO (Esperando Dirección)")
            else:
                sentimiento_ia = "NEUTRAL (Sin datos de noticias ingresados)"

            # 2. Descarga de datos de mercado (1 minuto)
            ticker = yf.Ticker(ticker_option)
            df_hist = ticker.history(period="2d", interval="1m")
            
            if df_hist.empty:
                st.error("No se pudieron obtener datos recientes para el activo seleccionado.")
            else:
                if df_hist.index.tz is not None:
                    df_hist.index = df_hist.index.tz_convert('America/New_York')
                else:
                    df_hist.index = pd.to_datetime(df_hist.index)

                # Máximos y Mínimos Generales (Overnight)
                high_pm_general = df_hist['High'].max()
                low_pm_general = df_hist['Low'].min()
                
                # Máximos y Mínimos de Última Hora (8:30 AM a 9:29 AM EST)
                hoy = df_hist.index[-1].date()
                mask_ultima_hora = (df_hist.index.date == hoy) & (df_hist.index.time >= time(8, 30)) & (df_hist.index.time <= time(9, 29))
                df_ultima_hora = df_hist[mask_ultima_hora]

                if not df_ultima_hora.empty:
                    high_pm_ult_hora = df_ultima_hora['High'].max()
                    low_pm_ult_hora = df_ultima_hora['Low'].min()
                else:
                    high_pm_ult_hora = high_pm_general
                    low_pm_ult_hora = low_pm_general

                # Precios y Gaps
                ultimo_cierre = df_hist['Close'].iloc[-390] if len(df_hist) > 390 else df_hist['Close'].iloc[0]
                precio_actual = df_hist['Close'].iloc[-1]
                
                gap_val = precio_actual - ultimo_cierre
                gap_pct = (gap_val / ultimo_cierre) * 100
                
                rango_operativo = high_pm_ult_hora - low_pm_ult_hora if (high_pm_ult_hora > low_pm_ult_hora) else (high_pm_general - low_pm_general)
                
                # Tercios (33.3% y 66.6%)
                tercio_inferior = low_pm_ult_hora + (rango_operativo * 0.333)
                tercio_superior = low_pm_ult_hora + (rango_operativo * 0.666)

                # Probabilidad Direccional ajustada por Técnica + Sentimiento de Noticias
                presion_ultima_hora = precio_actual - low_pm_ult_hora
                factor_presion = presion_ultima_hora / rango_operativo if rango_operativo > 0 else 0.5
                
                # Combinamos presión técnica + sesgo de noticias
                prob_alcista = round(50.0 + (factor_presion * 25.0) + (5.0 if gap_pct > 0 else -5.0) + (score_narrativa * 4.0), 1)
                prob_alcista = max(min(prob_alcista, 88.0), 12.0)
                prob_bajista = round(100.0 - prob_alcista, 1)

                # --- PANEL DE MÉTRICAS SUPERIORES ---
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric(label="Estado del Gap", value=f"{gap_pct:+.2f}%", delta=f"{gap_val:+.2f} USD")
                with col2:
                    st.metric(label="Máximo Estructural (Gral)", value=f"{high_pm_general:,.2f}")
                with col3:
                    st.metric(label="Mínimo Estructural (Gral)", value=f"{low_pm_general:,.2f}")
                with col4:
                    st.metric(label="Sentimiento Macro / Noticias", value=sentimiento_ia.split(" ")[0])

                st.markdown("---")
                
                # --- BLOQUE DE ANÁLISIS DE NARRATIVA ---
                with st.expander("🧠 Informe de Ingeniería Inversa de Narrativa (Mundo 1 & Mundo 2)", expanded=True):
                    st.markdown(f"**Noticias Analizadas:** _{noticias_input if noticias_input else 'Ninguna noticia ingresada. Operando puramente bajo estructura técnica.'}_")
                    st.markdown(f"- **Sesgo Fundamental Derivado:** {sentimiento_ia}")
                    st.markdown(f"- **Score de Impacto Narrativo:** {score_narrativa:+.1f} / 5.0")
                    st.markdown("- **Recomendación de Ingeniería:** El motor ha ponderado este factor frente a la acción del precio en la última hora (8:30 - 9:29 AM).")

                # --- GRÁFICO VISUAL CON TOOLTIPS ---
                st.subheader("🗺️ Mapa Visual de Niveles: Estructura Macro vs. Intención Pre-Apertura")

                fig = go.Figure()

                fig.add_trace(go.Scatter(
                    x=[1, 2], y=[high_pm_general, high_pm_general],
                    mode="lines+text", name="Máximo General Overnight",
                    line=dict(color="red", width=3, dash="dash"),
                    text=["", f"Máximo Estructural (Gral): {high_pm_general:,.2f}"],
                    textposition="top center",
                    hovertemplate=f"<b>Nivel: Máximo Estructural (Gral)</b><br>Precio: {high_pm_general:,.2f} USD<br>Resistencia Macro Absoluta<extra></extra>"
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
                    hovertemplate=f"<b>Tercio Superior (66.6%)</b><br>Precio: {tercio_superior:,.2f} USD<br>Zona de Resistencia / Aceleración<extra></extra>"
                ))

                fig.add_trace(go.Scatter(
                    x=[1, 2], y=[tercio_inferior, tercio_inferior],
                    mode="lines+text", name="Tercio Inferior (33.3%)",
                    line=dict(color="orange", width=2, dash="dot"),
                    text=["", f"Tercio Inferior (33.3%): {tercio_inferior:,.2f}"],
                    textposition="bottom center",
                    hovertemplate=f"<b>Tercio Inferior (33.3%)</b><br>Precio: {tercio_inferior:,.2f} USD<br>Zona de Soporte / Rebote Clave<extra></extra>"
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
                    text=["", f"Máximo Estructural (Gral): {low_pm_general:,.2f}"],
                    textposition="bottom center",
                    hovertemplate=f"<b>Nivel: Mínimo Estructural (Gral)</b><br>Precio: {low_pm_general:,.2f} USD<br>Soporte Macro Absoluto<extra></extra>"
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
                
                # --- PROBABILIDAD Y GUÍA OPERATIVA ---
                col_p1, col_p2 = st.columns(2)
                with col_p1:
                    st.success(f"🟢 **Probabilidad Alcista (Técnica + Sentimiento):** {prob_alcista}%")
                with col_p2:
                    st.error(f"🔴 **Probabilidad Bajista:** {prob_bajista}%")
                
                st.markdown("### 💡 Guía Operativa con Confluencia Fundamental")
                st.markdown(f"> **Lectura Estratégica:** El sistema ha integrado el análisis de noticias macro/tecnológicas con los niveles de los tercios (`{tercio_inferior:,.2f}` y `{tercio_superior:,.2f}`). Si el sentimiento detectado respalda la dirección del precio en la apertura de las 9:30 AM, busca la extensión hacia el máximo general (`{high_pm_general:,.2f}`) o mínimo general (`{low_pm_general:,.2f}`) en tu NinjaTrader.")

        except Exception as e:
            st.error(f"Ocurrió un error al procesar el sistema integral: {e}")
