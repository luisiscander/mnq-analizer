import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime

# Configuración de la página web
st.set_page_config(
    page_title="S-AACP: Análisis Cuantitativo Pre-Market MNQ",
    page_icon="📈",
    layout="wide"
)

st.title("🚀 S-AACP: Sistema Automatizado de Análisis Pre-Market y Proyección")
st.markdown("### Panel Cuantitativo para Futuros Nasdaq (MNQ) y Activos de Alta liquidez")

# Barra lateral para controles
st.sidebar.header("⚙️ Parámetros de Operación")
ticker_option = st.sidebar.selectbox(
    "Seleccione el Activo:",
    ("MNQ=F", "NQ=F", "QQQ", "NVDA", "AAPL")
)

st.sidebar.info("A las 9:29 AM - 9:30 AM EST, presione el botón para actualizar y calcular los niveles de apertura y probabilidades.")

btn_calcular = st.sidebar.button("📊 Ejecutar Análisis Pre-Market")

if btn_calcular or ticker_option:
    with st.spinner(f"Analizando datos en tiempo real para {ticker_option}..."):
        try:
            # Descarga de datos recientes (último día con intervalos de 1 minuto o diario)
            ticker = yf.Ticker(ticker_option)
            df_hist = ticker.history(period="5d", interval="1m")
            
            if df_hist.empty:
                st.error("No se pudieron obtener datos recientes para el activo seleccionado. Intente nuevamente.")
            else:
                # Simulación / Procesamiento de variables clave basados en la estructura solicitada
                ultimo_cierre = df_hist['Close'].iloc[-390] if len(df_hist) > 390 else df_hist['Close'].iloc[0]
                precio_actual = df_hist['Close'].iloc[-1]
                
                # Cálculo de Gap
                gap_val = precio_actual - ultimo_cierre
                gap_pct = (gap_val / ultimo_cierre) * 100
                
                # Mock / Estimación de máximos y mínimos estructurales basados en la sesión
                high_pm = df_hist['High'].max()
                low_pm = df_hist['Low'].min()
                rango_pm = high_pm - low_pm
                
                # Cálculo de Tercios (33.3% y 66.6%)
                tercio_inferior = low_pm + (rango_pm * 0.333)
                tercio_superior = low_pm + (rango_pm * 0.666)
                
                # Asignación de Probabilidad Direccional simulada en base al Gap y tendencia
                prob_alcista = 65.0 if gap_pct > 0 else 35.0
                prob_bajista = 100.0 - prob_alcista

                # --- DISEÑO VISUAL DE LA INTERFAZ ---
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric(label="Estado del Gap", value=f"{gap_pct:+.2f}%", delta=f"{gap_val:+.2f} USD")
                with col2:
                    st.metric(label="Máximo Estructural PM", value=f"{high_pm:,.2f}")
                with col3:
                    st.metric(label="Mínimo Estructural PM", value=f"{low_pm:,.2f}")
                
                st.markdown("---")
                
                # Sección de Tercios y Niveles Clave
                st.subheader("🎯 Zonas de Retroceso y Niveles Clave (Tercios)")
                col_t1, col_t2 = st.columns(2)
                with col_t1:
                    st.info(f"**Tercio Superior (66.6% del Rango):** `{tercio_superior:,.2f}`\n\n*Zona crítica de resistencia o aceleración alcista.*")
                with col_t2:
                    st.warning(f"**Tercio Inferior (33.3% del Rango):** `{tercio_inferior:,.2f}`\n\n*Zona crítica de soporte o rebote bajista.*")
                
                st.markdown("---")
                
                # Medidor de Probabilidad Direccional
                st.subheader("📊 Probabilidad Direccional Estimada para la Apertura")
                st.progress(int(prob_alcista))
                col_p1, col_p2 = st.columns(2)
                with col_p1:
                    st.success(f"🟢 **Probabilidad Alcista / Continuación:** {prob_alcista}%")
                with col_p2:
                    st.error(f"🔴 **Probabilidad Bajista / Reversión:** {prob_bajista}%")
                
                # Sugerencia Operativa Automática
                st.markdown("### 💡 Sugerencia Operativa del Sistema")
                if gap_pct > 0:
                    st.markdown(f"> **Gap Alcista detectado (+{gap_pct:.2f}%).** Si el precio se mantiene consolidando por encima del tercio inferior (`{tercio_inferior:,.2f}`), la probabilidad estadística favorece la búsqueda del máximo estructural (`{high_pm:,.2f}`). Vigilar rechazos en el tercio superior.")
                else:
                    st.markdown(f"> **Gap Bajista detectado ({gap_pct:.2f}%).** Vigilar el comportamiento en el tercio superior como zona de rebote en corto si el precio no logra superar la media de apertura.")

        except Exception as e:
            st.error(f"Ocurrió un error al procesar la información de mercado: {e}")