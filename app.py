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
st.markdown("### Mapeo Avanzado: Estructura Overnight vs. Intención de Última Hora (Pre-Apertura)")

# Barra lateral para controles
st.sidebar.header("⚙️ Parámetros de Operación")
ticker_option = st.sidebar.selectbox(
    "Seleccione el Activo:",
    ("MNQ=F", "NQ=F", "QQQ", "NVDA", "AAPL")
)

st.sidebar.info("A las 9:29 AM EST, presione el botón para actualizar y capturar la intención de última hora antes de la campana.")
btn_calcular = st.sidebar.button("📊 Ejecutar Análisis y Generar Mapa")

if btn_calcular or ticker_option:
    with st.spinner(f"Analizando datos y aislando la intención previa a la apertura para {ticker_option}..."):
        try:
            # Descarga de datos recientes de 1 minuto
            ticker = yf.Ticker(ticker_option)
            df_hist = ticker.history(period="2d", interval="1m")
            
            if df_hist.empty:
                st.error("No se pudieron obtener datos recientes para el activo seleccionado.")
            else:
                # Asegurar índice en formato datetime
                if df_hist.index.tz is not None:
                    df_hist.index = df_hist.index.tz_convert('America/New_York')
                else:
                    df_hist.index = pd.to_datetime(df_hist.index)

                # 1. Extracción de Máximos y Mínimos Generales (Overnight)
                high_pm_general = df_hist['High'].max()
                low_pm_general = df_hist['Low'].min()
                
                # 2. Extracción de Máximos y Mínimos de Última Hora (8:30 AM a 9:29 AM EST)
                hoy = df_hist.index[-1].date()
                mask_ultima_hora = (df_hist.index.date == hoy) & (df_hist.index.time >= time(8, 30)) & (df_hist.index.time <= time(9, 29))
                df_ultima_hora = df_hist[mask_ultima_hora]

                if not df_ultima_hora.empty:
                    high_pm_ult_hora = df_ultima_hora['High'].max()
                    low_pm_ult_hora = df_ultima_hora['Low'].min()
                else:
                    high_pm_ult_hora = high_pm_general
                    low_pm_ult_hora = low_pm_general

                # Precios
                ultimo_cierre = df_hist['Close'].iloc[-390] if len(df_hist) > 390 else df_hist['Close'].iloc[0]
                precio_actual = df_hist['Close'].iloc[-1]
                
                gap_val = precio_actual - ultimo_cierre
                gap_pct = (gap_val / ultimo_cierre) * 100
                
                rango_operativo = high_pm_ult_hora - low_pm_ult_hora if (high_pm_ult_hora > low_pm_ult_hora) else (high_pm_general - low_pm_general)
                
                # Cálculo de Tercios (33.3% y 66.6%)
                tercio_inferior = low_pm_ult_hora + (rango_operativo * 0.333)
                tercio_superior = low_pm_ult_hora + (rango_operativo * 0.666)

                # Probabilidad Direccional
                presion_ultima_hora = precio_actual - low_pm_ult_hora
                factor_presion = presion_ultima_hora / rango_operativo if rango_operativo > 0 else 0.5
                prob_alcista = round(50.0 + (factor_presion * 30.0) + (5.0 if gap_pct > 0 else -5.0), 1)
                prob_alcista = max(min(prob_alcista, 85.0), 15.0)
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
                    st.metric(label="Intención Última Hora (8:30-9:29)", value=f"H: {high_pm_ult_hora:,.2f} / L: {low_pm_ult_hora:,.2f}")

                st.markdown("---")
                
                # --- GRÁFICO VISUAL CON TOOLTIPS ENRIQUECIDOS ---
                st.subheader("🗺️ Mapa Visual de Niveles: Estructura Macro vs. Intención Pre-Apertura")

                fig = go.Figure()

                # 1. Máximo General Overnight
                fig.add_trace(go.Scatter(
                    x=[1, 2], y=[high_pm_general, high_pm_general],
                    mode="lines+text",
                    name="Máximo General Overnight",
                    line=dict(color="red", width=3, dash="dash"),
                    text=["", f"Máximo Estructural (Gral): {high_pm_general:,.2f}"],
                    textposition="top center",
                    hovertemplate=(
                        "<b>Nivel: Máximo Estructural (Gral)</b><br>"
                        f"Precio: {high_pm_general:,.2f} USD<br>"
                        f"Intención (8:30-9:29): {high_pm_ult_hora:,.2f} (H) / {low_pm_ult_hora:,.2f} (L)<br>"
                        "Significado: Resistencia macro institucional absoluta.<extra></extra>"
                    )
                ))

                # 2. Máximo de Última Hora
                fig.add_trace(go.Scatter(
                    x=[1, 2], y=[high_pm_ult_hora, high_pm_ult_hora],
                    mode="lines+text",
                    name="Máx Última Hora (8:30-9:29)",
                    line=dict(color="pink", width=2, dash="dot"),
                    text=["", f"Máx Última Hora: {high_pm_ult_hora:,.2f}"],
                    textposition="top right",
                    hovertemplate=(
                        "<b>Nivel: Máximo Última Hora</b><br>"
                        f"Precio: {high_pm_ult_hora:,.2f} USD<br>"
                        "Significado: Techo de corto plazo previo a la campana.<extra></extra>"
                    )
                ))

                # 3. Apertura / Nivel Actual
                fig.add_trace(go.Scatter(
                    x=[1, 2], y=[precio_actual, precio_actual],
                    mode="lines+text",
                    name="Apertura / Nivel Actual",
                    line=dict(color="blue", width=4),
                    text=["", f"Apertura / Nivel Actual: {precio_actual:,.2f}"],
                    textposition="middle right",
                    hovertemplate=(
                        "<b>Nivel: Apertura / Nivel Actual</b><br>"
                        f"Precio: {precio_actual:,.2f} USD<br>"
                        "Significado: Punto de partida de la sesión regular RTH.<extra></extra>"
                    )
                ))

                # 4. Tercio Superior (66.6%)
                fig.add_trace(go.Scatter(
                    x=[1, 2], y=[tercio_superior, tercio_superior],
                    mode="lines+text",
                    name="Tercio Superior (66.6%)",
                    line=dict(color="orange", width=2, dash="dot"),
                    text=["", f"Tercio Superior (66.6%): {tercio_superior:,.2f}"],
                    textposition="top center",
                    hovertemplate=(
                        "<b>Nivel: Tercio Superior (66.6%)</b><br>"
                        f"Precio: {tercio_superior:,.2f} USD<br>"
                        "Significado: Zona crítica de resistencia o aceleración alcista.<br>"
                        f"Intención (8:30-9:29): {high_pm_ult_hora:,.2f} (H) / {low_pm_ult_hora:,.2f} (L)<br>"
                        "Nota: Vigilar rechazo institucional.<extra></extra>"
                    )
                ))

                # 5. Tercio Inferior (33.3%)
                fig.add_trace(go.Scatter(
                    x=[1, 2], y=[tercio_inferior, tercio_inferior],
                    mode="lines+text",
                    name="Tercio Inferior (33.3%)",
                    line=dict(color="orange", width=2, dash="dot"),
                    text=["", f"Tercio Inferior (33.3%): {tercio_inferior:,.2f}"],
                    textposition="bottom center",
                    hovertemplate=(
                        "<b>Nivel: Tercio Inferior (33.3%)</b><br>"
                        f"Precio: {tercio_inferior:,.2f} USD<br>"
                        "Significado: Zona crítica de soporte o rebote bajista.<br>"
                        f"Intención (8:30-9:29): {high_pm_ult_hora:,.2f} (H) / {low_pm_ult_hora:,.2f} (L)<br>"
                        "Nota: Vigilar defensa de compradores.<extra></extra>"
                    )
                ))

                # 6. Mínimo de Última Hora
                fig.add_trace(go.Scatter(
                    x=[1, 2], y=[low_pm_ult_hora, low_pm_ult_hora],
                    mode="lines+text",
                    name="Mín Última Hora (8:30-9:29)",
                    line=dict(color="lightgreen", width=2, dash="dot"),
                    text=["", f"Mín Última Hora: {low_pm_ult_hora:,.2f}"],
                    textposition="bottom right",
                    hovertemplate=(
                        "<b>Nivel: Mínimo Última Hora</b><br>"
                        f"Precio: {low_pm_ult_hora:,.2f} USD<br>"
                        "Significado: Piso de corto plazo previo a la campana.<extra></extra>"
                    )
                ))

                # 7. Mínimo General Overnight
                fig.add_trace(go.Scatter(
                    x=[1, 2], y=[low_pm_general, low_pm_general],
                    mode="lines+text",
                    name="Mínimo General Overnight",
                    line=dict(color="green", width=3, dash="dash"),
                    text=["", f"Mínimo Estructural (Gral): {low_pm_general:,.2f}"],
                    textposition="bottom center",
                    hovertemplate=(
                        "<b>Nivel: Mínimo Estructural (Gral)</b><br>"
                        f"Precio: {low_pm_general:,.2f} USD<br>"
                        f"Intención (8:30-9:29): {high_pm_ult_hora:,.2f} (H) / {low_pm_ult_hora:,.2f} (L)<br>"
                        "Significado: Soporte macro institucional absoluto.<extra></extra>"
                    )
                ))

                fig.update_layout(
                    title=f"Proyección Cuantitativa RTH con Intención Pre-Apertura para {ticker_option}",
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
                    st.success(f"🟢 **Probabilidad Alcista (Sesgo de Intención):** {prob_alcista}%")
                with col_p2:
                    st.error(f"🔴 **Probabilidad Bajista:** {prob_bajista}%")
                
                st.markdown("### 💡 Guía Operativa Integrando la Intención de Última Hora")
                st.markdown(f"> **Lectura Táctica:** El sistema ha tomado el **Máximo (`{high_pm_general:,.2f}`) y Mínimo (`{low_pm_general:,.2f}`) generales** como vallas institucionales macro, pero calcula los tercios operativos (`{tercio_inferior:,.2f}` y `{tercio_superior:,.2f}`) utilizando la **intención de la última hora previa a la campana**. Pasa el cursor sobre cada línea del gráfico para consultar los detalles de precios, significados y rangos de intención.")

        except Exception as e:
            st.error(f"Ocurrió un error al procesar el motor avanzado: {e}")
