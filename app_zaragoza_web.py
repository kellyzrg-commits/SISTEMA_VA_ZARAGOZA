import streamlit as st
import mysql.connector
import pandas as pd
from fpdf import FPDF
from datetime import datetime
import random
import base64

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="VAZ Zaragoza - Pro Control v6.5", layout="wide", page_icon="🏢")

# --- ESTILOS VISUALES PREMIUM ---
def aplicar_estilos():
    st.markdown("""
        <style>
        .main { background-color: #f1f5f9; }
        .vaz-card {
            background: white; padding: 25px; border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.05); border: 1px solid #e2e8f0;
            margin-bottom: 20px;
        }
        .costo-banner {
            background: #0f172a; color: #38bdf8; padding: 15px;
            border-radius: 10px; text-align: center; margin-top: 10px;
        }
        .tech-label {
            color: #64748b; font-size: 0.8rem; text-transform: uppercase;
            letter-spacing: 0.1em; font-weight: bold; margin-bottom: 5px;
        }
        </style>
    """, unsafe_allow_html=True)

# --- CLASE DE INGENIERÍA Y CORTES ---
class VAZEngine:
    @staticmethod
    def calcular_cortes(ancho, alto, serie):
        # Descuentos técnicos (Medidas de corte para taller)
        return [
            {"Pieza": "Cabezal/Riel", "Cant": 2, "Medida": f"{ancho - 12} mm"},
            {"Pieza": "Jambas", "Cant": 2, "Medida": f"{alto} mm"},
            {"Pieza": "Traslapes", "Cant": 2, "Medida": f"{alto - 45} mm"}
        ]

# --- GENERADOR DE PDF (FORMATO ZARAGOZA OFICIAL) ---
class ZaragozaPDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 16)
        self.set_text_color(20, 40, 80)
        self.cell(0, 10, 'VIDRIOS Y ALUMINIOS ZARAGOZA', 0, 1, 'C')
        self.set_font('Arial', 'I', 10)
        self.set_text_color(100, 100, 100)
        self.cell(0, 5, 'Expertos en canceleria de aluminio, cristal templado, fachadas integrales y mucho mas...', 0, 1, 'C')
        self.set_font('Arial', '', 9)
        self.cell(0, 5, 'Tehuacán, Puebla', 0, 1, 'C')
        self.ln(5)
        self.line(10, 37, 200, 37)

def generar_pdf_vaz(datos):
    pdf = ZaragozaPDF()
    pdf.add_page()
    
    # Datos Cliente
    pdf.set_fill_color(240, 240, 240)
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(130, 8, f" CLIENTE: {datos['nombre'].upper()}", 1, 0, 'L', 1)
    pdf.cell(60, 8, f" FOLIO: {datos['folio']}", 1, 1, 'C', 1)
    pdf.set_font('Arial', '', 9)
    pdf.cell(130, 7, f" Ubicación: {datos['dir']}", 1)
    pdf.cell(60, 7, f" Fecha: {datetime.now().strftime('%d/%m/%Y')}", 1, 1, 'C')

    # Especificaciones
    pdf.ln(8)
    pdf.set_font('Arial', 'B', 11)
    pdf.cell(0, 8, "DETALLES TÉCNICOS", 0, 1)
    pdf.set_font('Arial', '', 10)
    pdf.multi_cell(0, 7, f"Sistema: {datos['serie']} | Color: {datos['color']} | Vidrio: {datos['vidrio']} | Medidas: {datos['ancho']}x{datos['alto']} mm", 1)

    # Tabla de Taller
    pdf.ln(5)
    pdf.set_font('Arial', 'B', 10)
    pdf.set_fill_color(30, 41, 59)
    pdf.set_text_color(255)
    pdf.cell(80, 8, "PIEZA", 1, 0, 'C', 1)
    pdf.cell(40, 8, "CANTIDAD", 1, 0, 'C', 1)
    pdf.cell(70, 8, "MEDIDA CORTE", 1, 1, 'C', 1)
    
    pdf.set_text_color(0)
    pdf.set_font('Arial', '', 9)
    for c in datos['cortes']:
        pdf.cell(80, 7, c['Pieza'], 1)
        pdf.cell(40, 7, str(c['Cant']), 1, 0, 'C')
        pdf.cell(70, 7, c['Medida'], 1, 1, 'C')

    # COSTO TOTAL
    pdf.ln(15)
    pdf.set_font('Arial', 'B', 14)
    pdf.set_fill_color(230, 230, 230)
    pdf.cell(130, 12, "COSTO TOTAL", 1, 0, 'R', 1)
    pdf.cell(60, 12, f"$ {datos['total']:,.2f} MXN", 1, 1, 'R', 1)
    
    return pdf.output(dest='S').encode('latin-1')

# --- COMPONENTE DE DIBUJO TÉCNICO (CANVAS HTML) ---
def render_canvas_vaz(ancho, alto, color_name):
    # Mapeo de colores de aluminio a CSS
    mapa_colores = {
        "Blanco": "#FFFFFF", "Negro": "#111827", 
        "Natural": "#9ca3af", "Madera": "#854d0e"
    }
    hex_color = mapa_colores.get(color_name, "#111827")
    
    # Lógica de escalado proporcional
    max_dim = max(ancho, alto)
    canvas_max_height = 320
    # Escalamos mm a px
    scale = canvas_max_height / max_dim if max_dim > 0 else 1
    
    w_px = ancho * scale
    h_px = alto * scale

    st.markdown(f"""
        <div style="background-color:#f8fafc; border:1px solid #cbd5e1; border-radius:12px; padding:30px; display:flex; flex-direction:column; align-items:center; justify-content:center; margin-bottom:20px;">
            <div style="width:{w_px}px; text-align:center; border-bottom:2px solid #94a3af; margin-bottom:10px; color:#1e293b; font-family:monospace; font-size:12px; font-weight:bold;">
                {ancho} mm
            </div>
            <div style="display:flex; align-items:center;">
                <div style="width:{w_px}px; height:{h_px}px; border:12px solid {hex_color}; background:linear-gradient(135deg, #bae6fd 0%, #e0f2fe 100%); display:flex; align-items:center; justify-content:center; position:relative; box-shadow: inset 0 0 15px rgba(0,0,0,0.1);">
                    <div style="background:white; padding:4px 8px; border-radius:4px; font-size:10px; font-weight:bold; color:{hex_color}; border:1px solid {hex_color};">
                        VISTA PREVIA
                    </div>
                </div>
                <div style="height:{h_px}px; margin-left:15px; border-left:2px solid #94a3af; display:flex; align-items:center; padding-left:10px; color:#1e293b; font-family:monospace; font-size:12px; font-weight:bold;">
                    {alto} mm
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

# --- INTERFAZ ---
def main():
    aplicar_estilos()
    st.title("🏢 VAZ Zaragoza - Pro Control")
    
    c1, c2 = st.columns([1, 1.3])

    with c1:
        st.markdown('<div class="vaz-card">', unsafe_allow_html=True)
        st.subheader("Entrada de Datos")
        nombre = st.text_input("Nombre del Cliente")
        direccion = st.text_input("Ubicación")
        serie = st.selectbox("Línea", ["Serie 20", "Serie 35", "Eurovent"])
        color = st.selectbox("Color", ["Blanco", "Negro", "Natural", "Madera"])
        
        # Medidas en mm que actualizan el gráfico
        ancho = st.number_input("Ancho (mm)", min_value=100, value=1200, step=1)
        alto = st.number_input("Alto (mm)", min_value=100, value=1000, step=1)
        
        vidrio = st.selectbox("Vidrio", ["6mm Claro", "6mm Filtrasol", "10mm Templado"])
        st.markdown('</div>', unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="vaz-card">', unsafe_allow_html=True)
        st.markdown('<p class="tech-label">Vista Previa y Validación</p>', unsafe_allow_html=True)
        
        # --- NUEVO: REINCORPORACIÓN DEL CANVAS TÉCNICO ---
        render_canvas_vaz(ancho, alto, color)
        
        # Cálculo de precio (Lógica de negocio)
        area = (ancho * alto) / 1000000
        # Precio base ajustado para el ejemplo
        total = (area * 2600) * (1.25 if color == "Madera" else 1.0)
        
        st.markdown(f'<div class="costo-banner"><h2>COSTO TOTAL: ${total:,.2f} MXN</h2></div>', unsafe_allow_html=True)
        
        # Cortes
        cortes = VAZEngine.calcular_cortes(ancho, alto, serie)
        st.write("📋 **Guía de Corte taller:**")
        st.table(pd.DataFrame(cortes))

        if st.button("🖨️ GENERAR COTIZACIÓN FINAL"):
            if nombre:
                folio = f"VAZ-{random.randint(1000, 9999)}"
                datos = {
                    'nombre': nombre, 'dir': direccion, 'serie': serie, 
                    'color': color, 'vidrio': vidrio, 'ancho': ancho, 
                    'alto': alto, 'total': total, 'folio': folio, 'cortes': cortes
                }
                pdf_bytes = generar_pdf_vaz(datos)
                
                st.download_button("📥 Descargar PDF", pdf_bytes, f"VAZ_{folio}.pdf", "application/pdf")
                
                b64_pdf = base64.b64encode(pdf_bytes).decode('utf-8')
                st.markdown(f'<iframe src="data:application/pdf;base64,{b64_pdf}" width="100%" height="500"></iframe>', unsafe_allow_html=True)
            else:
                st.warning("Escribe el nombre del cliente.")
        st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
