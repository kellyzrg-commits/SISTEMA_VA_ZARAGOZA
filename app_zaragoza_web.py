import streamlit as st
import pandas as pd
from fpdf import FPDF
from datetime import datetime
import random
import base64

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="VAZ Zaragoza | Sistema de Control",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- DISEÑO DE INTERFAZ (CSS PERSONALIZADO) ---
def aplicar_estilos_premium():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
        
        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
            background-color: #f8fafc;
        }
        
        .main-header {
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
            padding: 2rem;
            border-radius: 0 0 20px 20px;
            color: white;
            text-align: center;
            margin-bottom: 2rem;
            box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1);
        }

        .stCard {
            background: white;
            padding: 1.5rem;
            border-radius: 12px;
            border: 1px solid #e2e8f0;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            margin-bottom: 1rem;
        }

        .metric-card {
            background: #ffffff;
            border-left: 5px solid #3b82f6;
            padding: 1rem;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            text-align: center;
        }

        .price-text {
            color: #1e40af;
            font-size: 2rem;
            font-weight: 700;
        }

        /* Botón personalizado */
        .stButton>button {
            width: 100%;
            background: #1e40af;
            color: white;
            border-radius: 8px;
            padding: 0.75rem;
            font-weight: 600;
            transition: all 0.3s;
            border: none;
        }
        .stButton>button:hover {
            background: #1d4ed8;
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(30, 64, 175, 0.3);
        }
        </style>
    """, unsafe_allow_html=True)

# --- LÓGICA TÉCNICA (Optimización de despiece) ---
class VAZIngenieria:
    @staticmethod
    def obtener_despiece(ancho, alto, serie):
        # Lógica de taller refinada
        descuentos = {
            "Serie 20": {"h": 12, "v": 45},
            "Serie 35": {"h": 15, "v": 48},
            "Eurovent": {"h": 10, "v": 40}
        }
        d = descuentos.get(serie, {"h": 12, "v": 45})
        
        return [
            {"Componente": "Cabezal/Riel Superior", "Cantidad": 2, "Corte (mm)": ancho - d['h']},
            {"Componente": "Jambas Laterales", "Cantidad": 2, "Corte (mm)": alto},
            {"Componente": "Traslapes Centrales", "Cantidad": 2, "Corte (mm)": alto - d['v']},
            {"Componente": "Zoclo Inferior", "Cantidad": 2, "Corte (mm)": ancho - d['h']}
        ]

# --- MOTOR DE PDF (Formato Zaragoza Original) ---
class PDF_Zaragoza(FPDF):
    def header(self):
        self.set_font('Helvetica', 'B', 16)
        self.set_text_color(15, 23, 42)
        self.cell(0, 10, 'VIDRIOS Y ALUMINIOS ZARAGOZA', 0, 1, 'C')
        self.set_font('Helvetica', 'I', 10)
        self.set_text_color(100, 100, 100)
        self.cell(0, 5, 'Expertos en canceleria de aluminio, cristal templado, fachadas integrales y mucho mas...', 0, 1, 'C')
        self.set_font('Helvetica', '', 9)
        self.cell(0, 5, 'Tehuacan, Puebla, Mexico', 0, 1, 'C')
        self.ln(5)
        self.line(10, 38, 200, 38)

def exportar_pdf(datos):
    pdf = PDF_Zaragoza()
    pdf.add_page()
    
    # Bloque Cliente
    pdf.set_fill_color(241, 245, 249)
    pdf.set_font('Helvetica', 'B', 10)
    pdf.cell(130, 8, f" CLIENTE: {datos['nombre'].upper()}", 1, 0, 'L', 1)
    pdf.cell(60, 8, f" FOLIO: {datos['folio']}", 1, 1, 'C', 1)
    
    # Detalles
    pdf.ln(10)
    pdf.set_font('Helvetica', 'B', 11)
    pdf.cell(0, 8, "ESPECIFICACIONES DEL PROYECTO", 0, 1)
    pdf.set_font('Helvetica', '', 10)
    espec = f"Serie: {datos['serie']} | Color: {datos['color']} | Vidrio: {datos['vidrio']} | Dim: {datos['ancho']}x{datos['alto']} mm"
    pdf.multi_cell(0, 8, espec, 1)

    # Tabla de Taller
    pdf.ln(5)
    pdf.set_fill_color(15, 23, 42)
    pdf.set_text_color(255)
    pdf.cell(90, 8, " COMPONENTE", 1, 0, 'L', 1)
    pdf.cell(30, 8, " CANT", 1, 0, 'C', 1)
    pdf.cell(70, 8, " CORTE REAL", 1, 1, 'C', 1)
    
    pdf.set_text_color(0)
    for c in datos['cortes']:
        pdf.cell(90, 8, f" {c['Componente']}", 1)
        pdf.cell(30, 8, str(c['Cantidad']), 1, 0, 'C')
        pdf.cell(70, 8, f"{c['Corte (mm)']} mm", 1, 1, 'C')

    # TOTAL FINAL
    pdf.ln(15)
    pdf.set_font('Helvetica', 'B', 14)
    pdf.set_fill_color(220, 230, 250)
    pdf.cell(120, 12, "COSTO TOTAL ", 1, 0, 'R', 1)
    pdf.cell(70, 12, f"$ {datos['total']:,.2f} MXN ", 1, 1, 'R', 1)
    
    return pdf.output(dest='S').encode('latin-1')

# --- COMPONENTE VISUAL (Canvas Técnico) ---
def dibujar_referencia(ancho, alto, color_nombre):
    colores = {"Blanco": "#ffffff", "Negro": "#1e293b", "Natural": "#94a3b8", "Madera": "#713f12"}
    c = colores.get(color_nombre, "#1e293b")
    
    # Escalado dinámico para no romper la UI
    ratio = ancho / alto if alto != 0 else 1
    w_display = 300 if ratio >= 1 else 300 * ratio
    h_display = 300 / ratio if ratio >= 1 else 300
    
    # Limitar altura máxima
    if h_display > 400:
        h_display = 400
        w_display = 400 * ratio

    st.markdown(f"""
        <div style="display: flex; flex-direction: column; align-items: center; padding: 20px; background: #f1f5f9; border-radius: 15px; border: 1px dashed #cbd5e1;">
            <div style="width: {w_display}px; text-align: center; border-bottom: 2px solid #64748b; margin-bottom: 8px; font-size: 12px; font-weight: bold;">{ancho} mm</div>
            <div style="display: flex; align-items: center;">
                <div style="width: {w_display}px; height: {h_display}px; border: 12px solid {c}; background: #e0f2fe; box-shadow: inset 0 0 20px rgba(0,0,0,0.1); display: flex; align-items: center; justify-content: center;">
                    <div style="color: {c}; font-size: 10px; opacity: 0.5; font-weight: bold;">VA ZARAGOZA</div>
                </div>
                <div style="height: {h_display}px; border-left: 2px solid #64748b; margin-left: 8px; display: flex; align-items: center; padding-left: 8px; font-size: 12px; font-weight: bold;">{alto} mm</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

# --- APLICACIÓN PRINCIPAL ---
def main():
    aplicar_estilos_premium()
    
    st.markdown("""
        <div class="main-header">
            <h1>VIDRIOS Y ALUMINIOS ZARAGOZA</h1>
            <p>Sistema Profesional de Cotización e Ingeniería de Taller</p>
        </div>
    """, unsafe_allow_html=True)

    col_form, col_vis = st.columns([1, 1.2], gap="large")

    with col_form:
        st.markdown('<div class="stCard">', unsafe_allow_html=True)
        st.subheader("📋 Datos del Cliente")
        cliente = st.text_input("Nombre Completo / Razón Social", placeholder="Ej. Juan Pérez")
        obra = st.text_input("Dirección de Obra (Opcional)", placeholder="Tehuacán, Centro")
        
        st.subheader("🛠️ Especificaciones Técnicas")
        c1, c2 = st.columns(2)
        serie = c1.selectbox("Línea de Aluminio", ["Serie 20", "Serie 35", "Eurovent"])
        color = c2.selectbox("Acabado", ["Blanco", "Negro", "Natural", "Madera"])
        
        c3, c4 = st.columns(2)
        ancho = c3.number_input("Ancho Total (mm)", min_value=100, value=1200)
        alto = c4.number_input("Alto Total (mm)", min_value=100, value=1500)
        
        vidrio = st.selectbox("Tipo de Vidrio", ["6mm Claro", "6mm Filtrasol", "10mm Templado", "Esmerilado"])
        st.markdown('</div>', unsafe_allow_html=True)

    with col_vis:
        st.markdown('<div class="stCard">', unsafe_allow_html=True)
        st.subheader("📐 Vista Previa de Ingeniería")
        dibujar_referencia(ancho, alto, color)
        
        # Cálculos Económicos Refinados
        area_m2 = (ancho * alto) / 1,000,000
        base_precios = {"Serie 20": 1400, "Serie 35": 1850, "Eurovent": 3100}
        total_calculado = (area_m2 * base_precios[serie]) * (1.3 if color == "Madera" else 1.0)
        
        # Tarjetas de Métricas
        m1, m2 = st.columns(2)
        with m1:
            st.markdown(f'<div class="metric-card">Área Total<br><b>{area_m2:.2f} m²</b></div>', unsafe_allow_html=True)
        with m2:
            st.markdown(f'<div class="metric-card">Costo Estimado<br><b>${total_calculado:,.2f}</b></div>', unsafe_allow_html=True)
        
        st.divider()
        
        # Tabla de despiece rápida
        cortes = VAZIngenieria.obtener_despiece(ancho, alto, serie)
        st.write("**📝 Despiece para Taller:**")
        st.dataframe(pd.DataFrame(cortes), hide_index=True, use_container_width=True)

        if st.button("🚀 GENERAR COTIZACIÓN Y ORDEN"):
            if cliente:
                folio = f"VAZ-{random.randint(1000, 9999)}"
                datos = {
                    'nombre': cliente, 'dir': obra, 'serie': serie, 
                    'color': color, 'vidrio': vidrio, 'ancho': ancho, 
                    'alto': alto, 'total': total_calculado, 'folio': folio, 
                    'cortes': cortes
                }
                pdf_bytes = exportar_pdf(datos)
                
                st.success(f"Documento {folio} generado con éxito.")
                st.download_button(
                    label="📥 Descargar PDF Oficial",
                    data=pdf_bytes,
                    file_name=f"Cotizacion_{folio}_{cliente}.pdf",
                    mime="application/pdf"
                )
                
                # Vista previa del PDF embebida
                b64 = base64.b64encode(pdf_bytes).decode()
                pdf_display = f'<iframe src="data:application/pdf;base64,{b64}" width="100%" height="400" type="application/pdf"></iframe>'
                st.markdown(pdf_display, unsafe_allow_html=True)
            else:
                st.error("⚠️ El nombre del cliente es obligatorio.")
        st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
