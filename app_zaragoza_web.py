import streamlit as st
import mysql.connector
import pandas as pd
from datetime import datetime
import random

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="VAZ-Control V3.2 - Cotizador Visual", layout="wide")

# --- FUNCIONES DE BASE DE DATOS ---
def conectar_db():
    try:
        return mysql.connector.connect(
            host=st.secrets["mysql"]["host"],
            user=st.secrets["mysql"]["user"],
            password=st.secrets["mysql"]["password"],
            database=st.secrets["mysql"]["database"],
            port=st.secrets["mysql"]["port"]
        )
    except Exception as e:
        st.error(f"Error de conexión: {e}")
        return None

def obtener_precios_db():
    conn = conectar_db()
    if conn:
        df = pd.read_sql("SELECT id_config, concepto, costo_base_m2 FROM configuracion_precios", conn)
        conn.close()
        return df
    return pd.DataFrame()

# --- INTERFAZ DEL ASESOR ---
if 'rol' not in st.session_state or st.session_state.rol != 'asesor':
    st.warning("Acceso restringido. Por favor, inicia sesión como Asesor.")
else:
    st.header(f"📋 Nuevo Presupuesto Visual | Asesor: {st.session_state.nombre}")

    # Estructura de dos columnas (Formulario y Gráfico)
    col_form, col_visual = st.columns([1, 1.2])

    with col_form:
        with st.form("form_visual"):
            st.subheader("1. Datos y Materiales")
            cliente = st.text_input("Nombre del Cliente")
            
            df_precios = obtener_precios_db()
            opciones_serie = df_precios['concepto'].tolist() if not df_precios.empty else ["Serie 20"]
            serie = st.selectbox("Serie", opciones_serie)
            
            modelo = st.selectbox("Modelo", ["Fijo", "Corrediza", "Batiente", "Mosquitero Fijo"])
            
            # --- NUEVO: Margen por color ---
            margen_colores = {"Blanco": 1.0, "Negro": 1.05, "Natural": 1.0, "Bronce": 1.08, "Madera": 1.15}
            color = st.selectbox("Color del Aluminio", list(margen_colores.keys()))
            
            st.divider()
            st.subheader("2. Medidas y Cristal")
            c1, c2 = st.columns(2)
            # Medidas que disparan el cambio en el gráfico
            ancho = c1.number_input("Ancho (mm)", min_value=1, value=1200, step=1)
            alto = c2.number_input("Alto (mm)", min_value=1, value=1500, step=1)
            
            espesor = st.selectbox("Cristal", ["6mm", "9mm", "10mm Templado", "DuoVent"])

            st.divider()
            
            # --- CÁLCULO DE INGENIERÍA CON MÁRGENES ---
            costo_base = float(df_precios[df_precios['concepto'] == serie]['costo_base_m2'].values[0])
            area_m2 = (ancho * alto) / 1000000
            
            total_calc = (area_m2 * costo_base) # Costo Material Base
            total_calc = total_calc * 1.50      # +50% Mano de obra
            total_calc = total_calc * margen_colores[color] # +Margen por color especializado
            
            st.write(f"## Total: ${total_calc:,.2f} MXN")
            st.caption(f"Incluye mano de obra y margen por color {color} (+{int((margen_colores[color]-1)*100)}%).")

            guardar = st.form_submit_button("🚀 Guardar Presupuesto")

    # --- NUEVO: COLUMNA VISUAL (CANVAS TÉCNICO) ---
    with col_visual:
        st.subheader("📐 Validación Técnica (Vista Previa)")
        
        # Mapeo de colores de aluminio a códigos hexadecimales para el borde
        css_colores = {"Blanco": "#e2e8f0", "Negro": "#000000", "Natural": "#94a3b8", "Bronce": "#854d0e", "Madera": "#a16207"}
        color_borde = css_colores.get(color, "#000000")
        
        # Lógica de escalado para que el dibujo no se salga de la pantalla
        max_dim_mm = max(ancho, alto)
        canvas_height_px = 400
        # Escalamos proporcionalmente las medidas de mm a px
        scale_factor = (canvas_height_px - 40) / max_dim_mm if max_dim_mm > 0 else 1
        
        w_px = ancho * scale_factor
        h_px = alto * scale_factor

        # Dibujo Técnico usando HTML/CSS dentro de Streamlit
        st.markdown(f"""
            <div style="background-color:white; border:2px solid #cbd5e1; border-radius:15px; padding:20px; height:{canvas_height_px}px; display:flex; flex-direction:column; align-items:center; justify-content:center;">
                <div style="width:{w_px}px; text-align:center; border-bottom:1px solid #94a3b8; color:#64748b; font-size:12px; margin-bottom:5px;">
                    {ancho} mm
                </div>
                <div style="display:flex; align-items:center;">
                    <div style="width:{w_px}px; height:{h_px}px; border:8px solid {color_borde}; background-color:rgba(186,230,253,0.3); display:flex; align-items:center; justify-content:center; box-shadow: inset 0 0 10px rgba(0,0,0,0.1);">
                        <span style="color:{color_borde}; font-weight:bold; font-size:14px; background:white; padding:2px 5px; border-radius:3px;">
                            {modelo.upper()}
                        </span>
                    </div>
                    <div style="height:{h_px}px; display:flex; align-items:center; color:#64748b; font-size:12px; margin-left:10px; padding-left:5px; border-left:1px solid #94a3b8;">
                        {alto} mm
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        if guardar and cliente:
            st.success(f"Presupuesto para {cliente} guardado (Simulación).")
            st.balloons()
