import streamlit as st
import pandas as pd
from fpdf import FPDF
import datetime

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="VA Zaragoza - Presupuestos Pro", layout="wide")

class PDF_Pro(FPDF):
    def header(self):
        # Logo de Vidrios y Aluminios Zaragoza
        try:
            self.image('assets/logo_zaragoza.png', 10, 8, 55)
        except:
            self.set_font('Arial', 'B', 15)
            self.cell(60, 10, 'VA ZARAGOZA')
        
        # Información del Negocio (Arriba Derecha)
        self.set_font('Arial', 'B', 10)
        self.set_text_color(26, 35, 126) # Azul oscuro
        self.set_xy(120, 10)
        self.cell(80, 5, "VIDRIOS Y ALUMINIOS ZARAGOZA", 0, 1, 'R')
        self.set_font('Arial', '', 8)
        self.set_text_color(0, 0, 0)
        self.set_x(120)
        self.cell(80, 4, "Cancelaría de Aluminio y Cristal", 0, 1, 'R')
        self.set_x(120)
        self.cell(80, 4, "Tehuacán, Puebla", 0, 1, 'R')
        self.ln(15)

    def draw_box(self, x, y, w, h, title):
        self.set_fill_color(26, 35, 126)
        self.set_text_color(255, 255, 255)
        self.set_xy(x, y)
        self.set_font('Arial', 'B', 9)
        self.cell(w, 6, f"  {title}", 0, 1, 'L', fill=True)
        self.set_text_color(0, 0, 0)
        self.rect(x, y, w, h)

def generar_pdf_estilo_pro(cliente, ancho, alto, sistema, total, img_path=None):
    pdf = PDF_Pro()
    pdf.add_page()
    
    # --- BLOQUES DE INFORMACIÓN ---
    # Datos del Presupuesto
    pdf.draw_box(10, 35, 90, 25, "DATOS DEL PRESUPUESTO")
    pdf.set_font('Arial', '', 9)
    pdf.set_xy(12, 42)
    pdf.cell(80, 5, f"FECHA: {datetime.date.today()}", 0, 1)
    pdf.set_x(12)
    pdf.cell(80, 5, f"VALIDEZ: 15 Días", 0, 1)
    pdf.set_x(12)
    pdf.cell(80, 5, "FORMA DE PAGO: 50% Anticipo / 50% Contra Entrega", 0, 1)

    # Datos del Cliente
    pdf.draw_box(105, 35, 95, 25, "DATOS DEL CLIENTE")
    pdf.set_xy(107, 42)
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(90, 5, f"CLIENTE: {cliente.upper()}", 0, 1)
    pdf.set_font('Arial', '', 9)
    pdf.set_x(107)
    pdf.cell(90, 5, "Entrega en Domicilio / Instalación Incluida", 0, 1)

    # --- SECCIÓN TÉCNICA (GRÁFICO Y DESCRIPCIÓN) ---
    pdf.set_fill_color(240, 240, 240)
    pdf.set_xy(10, 65)
    pdf.set_font('Arial', 'B', 9)
    pdf.cell(90, 7, "  GRAFICO", 1, 0, 'L', fill=True)
    pdf.cell(95, 7, "  DESCRIPCION", 1, 1, 'L', fill=True)
    
    # Espacio para el gráfico (aquí se podría insertar una captura del gráfico de la app)
    pdf.rect(10, 72, 90, 60)
    pdf.set_xy(15, 80)
    pdf.set_font('Arial', 'I', 8)
    pdf.cell(80, 5, f"Representación: {sistema}", 0, 1, 'C')
    pdf.set_x(15)
    pdf.cell(80, 5, f"{ancho} mm x {alto} mm", 0, 1, 'C')

    # Descripción detallada a la derecha
    pdf.set_xy(105, 75)
    pdf.set_font('Arial', 'B', 11)
    pdf.cell(90, 6, f"{sistema}", 0, 1)
    pdf.set_font('Arial', '', 9)
    pdf.set_x(105)
    pdf.multi_cell(90, 5, f"* Serie: Línea de 2 o 3 pulgadas\n* Color: Natural / Negro / Blanco\n* Medida: {ancho} x {alto} mm\n* Vidrio: Claro 6mm (Laminado opcional)\n* Incluye: Carretillas, felpa y sellado con silicón.")

    # --- TABLA DE COSTOS ---
    pdf.set_xy(10, 135)
    pdf.set_font('Arial', 'B', 9)
    pdf.cell(100, 8, "CONCEPTO", 1, 0, 'C', fill=True)
    pdf.cell(30, 8, "CANTIDAD", 1, 0, 'C', fill=True)
    pdf.cell(60, 8, "TOTAL NETO", 1, 1, 'C', fill=True)
    
    pdf.set_font('Arial', '', 10)
    pdf.cell(100, 10, f"Suministro e Instalación de {sistema}", 1)
    pdf.cell(30, 10, "1", 1, 0, 'C')
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(60, 10, f"$ {total:,.2f} MXN", 1, 1, 'C')

    # Pie de página (Notas)
    pdf.ln(10)
    pdf.set_font('Arial', 'I', 8)
    pdf.multi_cell(190, 4, "Este presupuesto es una estimación técnica basada en las medidas proporcionadas por el cliente. Las medidas definitivas serán rectificadas en obra por nuestro personal. Precios sin IVA.")

    return pdf.output(dest='S').encode('latin-1')

# --- APP INTERFAZ ---
st.title("🛡️ Generador de Presupuestos - VA Zaragoza")

with st.sidebar:
    st.image('assets/logo_zaragoza.png') if st.checkbox("Mostrar Logo") else None
    cliente = st.text_input("Cliente", "Kelly Zaragoza")
    sistema = st.selectbox("Producto", ["Ventana Corrediza", "Ventana Fija", "Puerta de Baño"])
    ancho = st.number_input("Ancho (mm)", value=1200)
    alto = st.number_input("Alto (mm)", value=1000)
    precio_m2 = st.number_input("Costo m²", value=1850)

area = (ancho/1000) * (alto/1000)
subtotal = area * precio_m2

st.info(f"### Presupuesto Estimado: ${subtotal:,.2f} MXN")

if st.button("📄 Crear PDF Profesional"):
    pdf_final = generar_pdf_estilo_pro(cliente, ancho, alto, sistema, subtotal)
    st.download_button(
        label="⬇️ Descargar Presupuesto",
        data=pdf_final,
        file_name=f"Presupuesto_{cliente}.pdf",
        mime="application/pdf"
    )
