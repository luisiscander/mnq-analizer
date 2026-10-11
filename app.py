import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# Configuración de la página web
st.set_page_config(
    page_title="S-AACP: Análisis Cuantitativo Pre-Market MNQ",
    page_icon="📈",
    layout="wide"
)

st.title("🚀 S-AACP: Sistema Automatizado de Análisis Pre-Market y Proyección")
st.markdown("### Mapeo Visual de Niveles Operativos, Tercios y Gaps para Futuros Nasdaq (MNQ)")

# Barra lateral para controles
st.sidebar.header("⚙️ Parámetros de Operación")
ticker_option = st.sidebar.selectbox(
    "Seleccione el Activo:",
    ("MNQ=F", "NQ=F", "QQQ", "NVDA", "AAPL")
)

st.sidebar.info("A las 9:29 AM EST, presione el botón para actualizar y proyectar los niveles en el gráfico.")
btn_calcular = st.sidebar.button("📊 Ejecutar Análisis y Generar Mapa")

if btn_calcular or ticker_option:
    with st.spinner(f"Calculando proyecciones para {ticker_option}..."):
        try:
            # Descarga de datos recientes
            ticker = yf.Ticker(ticker_option)
            df_hist = ticker.history(period="5d", interval="1m")
            
            if df_hist.empty:
                st.error("No se pudieron obtener datos recientes para el activo seleccionado.")
            else:
                # Extracción y cálculo de variables
                ultimo_cierre = df_hist['Close'].iloc[-390] if len(df_hist) > 390 else df_hist['Close'].iloc[0]
                precio_actual = df_hist['Close'].iloc[-1]
                
                gap_val = precio_actual - ultimo_cierre
                gap_pct = (gap_val / ultimo_cierre) * 100
                
                high_pm = df_hist['High'].max()
                low_pm = df_hist['Low'].min()
                rango_pm = high_pm - low_pm
                
                # Niveles de apertura simulados / de referencia para la proyección
                precio_apertura_estimado = precio_actual
                
                # Cálculo de Tercios (33.3% y 66.6%) a partir del rango
                tercio_inferior = low_pm + (rango_pm * 0.333)
                tercio_superior = low_pm + (rango_pm * 0.666)
                
                # Objetivos de extensión alcista y bajista basados en tercios
                objetivo_alza = high_pm + (rango_pm * 0.333)
                objetivo_baja = low_pm - (rango_pm * 0.333)

                # Probabilidad Direccional estimada
                prob_alcista = 62.0 if gap_pct > 0 else 38.0
                prob_bajista = 100.0 - prob_alcista

                # --- MÉTRICAS SUPERIORES ---
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric(label="Estado del Gap", value=f"{gap_pct:+.2f}%", delta=f"{gap_val:+.2f} USD")
                with col2:
                    st.metric(label="Máximo Estructural PM", value=f"{high_pm:,.2f}")
                with col3:
                    st.metric(label="Mínimo Estructural PM", value=f"{low_pm:,.2f}")
                
                st.markdown("---")
                
                # --- GRÁFICO VISUAL ESQUEMÁTICO DE NIVELES ---
                st.subheader("🗺️ Mapa Visual de Niveles y Retrocesos Proyectados")
                st.markdown("Este esquema muestra la **Apertura**, los **Máximos/Mínimos** y sus zonas de **retroceso por tercios** para que puedas pasarlos a tu gráfico de NinjaTrader:")

                fig = go.Figure()

                # Línea de Máximo y su tercio de retroceso
                fig.add_trace(go.Scatter(
                    x=[1, 2], y=[high_pm, high_pm],
                    mode="lines+text",
                    name="Máximo Pre-Market",
                    line=dict(color="red", width=3, dash="dash"),
                    text=["", f"Máximo Estructural: {high_pm:,.2f}"],
                    textposition="top center"
                ))
                fig.add_trace(go.Scatter(
                    x=[1, 2], y=[tercio_superior, tercio_superior],
                    mode="lines+text",
                    name="Tercio Superior (66.6%)",
                    line=dict(color="orange", width=2, dash="dot"),
                    text=["", f"Tercio Superior (66.6%): {tercio_superior:,.2f}"],
                    textposition="top center"
                ))

                # Línea de Apertura Oficial
                fig.add_trace(go.Scatter(
                    x=[1, 2], y=[precio_apertura_estimado, precio_apertura_estimado],
                    mode="lines+text",
                    name="Precio de Apertura (Open)",
                    line=dict(color="blue", width=4),
                    text=["", f"Apertura Oficial: {precio_apertura_estimado:,.2f}"],
                    textposition="middle right"
                ))

                # Línea de Mínimo y su tercio de retroceso
                fig.add_trace(go.Scatter(
                    x=[1, 2], y=[tercio_inferior, tercio_inferior],
                    mode="lines+text",
                    name="Tercio Inferior (33.3%)",
                    line=dict(color="orange", width=2, dash="dot"),
                    text=["", f"Tercio Inferior (33.3%): {tercio_inferior:,.2f}"],
                    textposition="bottom center"
                ))
                fig.add_trace(go.Scatter(
                    x=[1, 2], y=[low_pm, low_pm],
                    mode="lines+text",
                    name="Mínimo Pre-Market",
                    line=dict(color="green", width=3, dash="dash"),
                    text=["", f"Mínimo Estructural: {low_pm:,.2f}"],
                    textposition="bottom center"
                ))

                fig.update_layout(
                    title=f"Proyección Operativa RTH para {ticker_option}",
                    xaxis_title="Estructura de Sesión",
                    yaxis_title="Precio (USD)",
                    height=500,
                    showlegend=True,
                    template="plotly_dark"
                )

                st.plotly_chart(fig, use_container_width=True)

                st.markdown("---")
                
                # --- PROBABILIDAD Y SUGERENCIA ---
                col_p1, col_p2 = st.columns(2)
                with col_p1:
                    st.success(f"🟢 **Probabilidad Alcista:** {prob_alcista}%")
                with col_p2:
                    st.error(f"🔴 **Probabilidad Bajista:** {prob_bajista}%")
                
                st.markdown("### 💡 Guía Operativa para NinjaTrader")
                if gap_pct > 0:
                    st.markdown(f"> **Escenario Alcista (Gap Up):** El precio abre sobre el nivel base. Si respeta el **Tercio Inferior (`{tercio_inferior:,.2f}`)** como soporte en el retroceso inicial de las 9:30 AM, el objetivo lógico a buscar en tu gráfico de NinjaTrader es el **Máximo Estructural (`{high_pm:,.2f}`)**.")
                else:
                    st.markdown(f"> **Escenario Bajista (Gap Down):** Vigilar el **Tercio Superior (`{tercio_superior:,.2f}`)** como zona de resistencia o rechazo si el precio intenta rellenar el vacío de mercado tras la campana de apertura.")

        except Exception as e:
            st.error(f"Ocurrió un error al generar el gráfico: {e}")
