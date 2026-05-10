import streamlit as st
import mysql.connector
import pandas as pd
from fpdf import FPDF
from datetime import datetime
import random
import base64

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="VAZ Zaragoza - Sistema Central", layout="wide", page_icon="🏢")

# --- ESTILOS VISUALES ---
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
        </style>
    """, unsafe_allow_html=True)

# --- CLASE DE INGENIERÍA Y CORTES ---
class VAZEngine:
    @staticmethod
    def calcular_cortes(ancho, alto, serie):
        # Descuentos reales (Medidas de corte para taller)
        return [
            {"Pieza": "Cabezal/Riel", "Cant": 2, "Medida": f"{ancho - 12} mm"},
            {"Pieza": "Jambas", "Cant": 2, "Medida": f"{alto} mm"},
            {"Pieza": "Traslapes", "Cant": 2, "Medida": f"{alto - 45} mm"}
        ]

# --- GENERADOR DE PDF (FORMATO ZARAGOZA) ---
class ZaragozaPDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 16)
        self.set_text_color(20, 40, 80)
        self.cell(0, 10, 'VIDRIOS Y ALUMINIOS ZARAGOZA', 0, 1, 'C')
        self.set_font('Arial', '', 9)
        self.cell(0, 5, 'Tehuacán, Puebla', 0, 1, 'C')
        self.ln(5)
        self.line(10, 32, 200, 32)

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

    # COSTO TOTAL (Ajustado)
    pdf.ln(15)
    pdf.set_font('Arial', 'B', 14)
    pdf.set_fill_color(230, 230, 230)
    pdf.cell(130, 12, "COSTO TOTAL", 1, 0, 'R', 1)
    pdf.cell(60, 12, f"$ {datos['total']:,.2f} MXN", 1, 1, 'R', 1)
    
    return pdf.output(dest='S').encode('latin-1')

# --- INTERFAZ ---
def main():
    aplicar_estilos()
    st.title("🏭 VAZ Zaragoza - Pro Control")
    
    c1, c2 = st.columns([1, 1.3])

    with c1:
        st.markdown('<div class="vaz-card">', unsafe_allow_html=True)
        st.subheader("Entrada de Datos")
        nombre = st.text_input("Nombre del Cliente")
        direccion = st.text_input("Ubicación")
        serie = st.selectbox("Línea", ["Serie 20", "Serie 35", "Eurovent"])
        color = st.selectbox("Color", ["Blanco", "Negro", "Natural", "Madera"])
        ancho = st.number_input("Ancho (mm)", value=1200)
        alto = st.number_input("Alto (mm)", value=1000)
        vidrio = st.selectbox("Vidrio", ["6mm Claro", "6mm Filtrasol", "10mm Templado"])
        st.markdown('</div>', unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="vaz-card">', unsafe_allow_html=True)
        # Cálculo de precio (Lógica de negocio)
        area = (ancho * alto) / 1000000
        total = (area * 2400) * (1.25 if color == "Madera" else 1.0)
        
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
                
                # Vista previa
                b64_pdf = base64.b64encode(pdf_bytes).decode('utf-8')
                st.markdown(f'<iframe src="data:application/pdf;base64,{b64_pdf}" width="100%" height="500"></iframe>', unsafe_allow_html=True)
            else:
                st.warning("Escribe el nombre del cliente.")
        st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
