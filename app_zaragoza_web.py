import streamlit as st
import pandas as pd
from fpdf import FPDF
import datetime
import os

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="VA Zaragoza - Presupuestos Pro", layout="wide")

# Color Institucional (Azul Marino Zaragoza extraído de tu logo)
AZUL_ZARAGOZA = (24, 46, 82) 

class PDF_Pro(FPDF):
    def header(self):
        # Localización del logo en la carpeta assets
        logo_path = os.path.join("assets", "logo_zaragoza.png")
        
        if os.path.exists(logo_path):
            self.image(logo_path, 10, 8, 55)
        else:
            self.set_font('Arial', 'B', 15)
            self.set_text_color(*AZUL_ZARAGOZA)
            self.cell(60, 10, 'VIDRIOS Y ALUMINIOS ZARAGOZA')
        
        # Información de contacto (Derecha)
        self.set_font('Arial', 'B', 10)
        self.set_text_color(*AZUL_ZARAGOZA)
        self.set_xy(120, 10)
        self.cell(80, 5, "VIDRIOS Y ALUMINIOS ZARAGOZA", 0, 1, 'R')
        self.set_font('Arial', '', 8)
        self.set_text_color(0, 0, 0)
        self.set_x(120)
        self.cell(80, 4, "Cancelaría de Aluminio y Cristal", 0, 1, 'R')
        self.set_x(120)
        self.cell(80, 4, "Tehuacán, Puebla", 0, 1, 'R')
        
        # Línea decorativa bajo el encabezado
        self.set_draw_color(*AZUL_ZARAGOZA)
        self.line(10, 35, 200, 35)
        self.ln(25)

    def draw_box(self, x, y, w, h, title):
        # Dibujar encabezado de sección azul
        self.set_fill_color(*AZUL_ZARAGOZA)
        self.set_text_color(255, 255, 255)
        self.set_xy(x, y)
        self.set_font('Arial', 'B', 9)
        self.cell(w, 6, f"  {title}", 0, 1, 'L', fill=True)
        self.set_text_color(0, 0, 0)
        self.rect(x, y, w, h)

def generar_pdf_estilo_pro(cliente, ancho, alto, sistema, total, df_despiece):
    pdf = PDF_Pro()
    pdf.add_page()
    
    # --- BLOQUES DE INFORMACIÓN (Coordenadas ajustadas para no encimarse) ---
    # Datos del Presupuesto
    pdf.draw_box(10, 45, 90, 25, "DATOS DEL PRESUPUESTO")
    pdf.set_font('Arial', '', 9)
    pdf.set_xy(12, 52)
    pdf.cell(80, 5, f"FECHA: {datetime.date.today()}", 0, 1)
    pdf.set_x(12)
    pdf.cell(80, 5, "VALIDEZ: 15 Días naturales", 0, 1)
    pdf.set_x(12)
    pdf.cell(80, 5, "FORMA DE PAGO: 50% Anticipo / 50% Final", 0, 1)

    # Datos del Cliente
    pdf.draw_box(105, 45, 95, 25, "DATOS DEL CLIENTE")
    pdf.set_xy(107, 52)
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(90, 5, f"CLIENTE: {cliente.upper()}", 0, 1)
    pdf.set_font('Arial', '', 9)
    pdf.set_x(107)
    pdf.cell(90, 5, "Entrega a domicilio e Instalación incluida", 0, 1)

    # --- SECCIÓN TÉCNICA (GRÁFICO Y DESCRIPCIÓN) ---
    pdf.set_fill_color(*AZUL_ZARAGOZA)
    pdf.set_text_color(255, 255, 255)
    pdf.set_xy(10, 78)
    pdf.set_font('Arial', 'B', 9)
    pdf.cell(90, 7, "  DISEÑO ESTIMADO", 1, 0, 'L', fill=True)
    pdf.cell(95, 7, "  ESPECIFICACIONES TÉCNICAS", 1, 1, 'L', fill=True)
    
    pdf.set_text_color(0, 0, 0)
    pdf.rect(10, 85, 90, 55) # Recuadro del gráfico
    pdf.set_xy(15, 105)
    pdf.set_font('Arial', 'I', 9)
    pdf.cell(80, 5, f"Modelo: {sistema}", 0, 1, 'C')
    pdf.set_x(15)
    pdf.cell(80, 5, f"Medida Total: {ancho} mm x {alto} mm", 0, 1, 'C')

    # Descripción a la derecha
    pdf.set_xy(105, 88)
    pdf.set_font('Arial', 'B', 11)
    pdf.cell(90, 6, f"{sistema}", 0, 1)
    pdf.set_font('Arial', '', 9)
    pdf.set_x(105)
    pdf.multi_cell(95, 5, f"* Perfilería: Aluminio de alta resistencia\n* Medida: {ancho} x {alto} mm\n* Vidrio: Claro 6mm (Calidad Automotriz)\n* Sellado: Silicón antihongos\n* Herrajes: Carretillas de uso rudo.")

    # --- TABLA DE COSTOS FINAL ---
    pdf.set_xy(10, 148)
    pdf.set_font('Arial', 'B', 9)
    pdf.set_fill_color(240, 240, 240)
    pdf.cell(100, 8, "CONCEPTO", 1, 0, 'C', fill=True)
    pdf.cell(30, 8, "CANTIDAD", 1, 0, 'C', fill=True)
    pdf.cell(60, 8, "IMPORTE TOTAL", 1, 1, 'C', fill=True)
    
    pdf.set_font('Arial', '', 10)
    pdf.cell(100, 12, f"Suministro e Instalación de {sistema}", 1)
    pdf.cell(30, 12, "1", 1, 0, 'C')
    pdf.set_font('Arial', 'B', 11)
    pdf.cell(60, 12, f"$ {total:,.2f} MXN", 1, 1, 'C')

    # Nota final
    pdf.ln(8)
    pdf.set_font('Arial', 'I', 8)
    pdf.set_text_color(100, 100, 100)
    pdf.multi_cell(190, 4, "Nota: Este presupuesto no incluye IVA. Las medidas son rectificadas en obra antes de fabricar. Cualquier cambio en el diseño original puede afectar el costo final.")

    return pdf.output(dest='S').encode('latin-1')

# --- LÓGICA DE LA INTERFAZ DE USUARIO ---
st.title("📂 Control de Ventas - Vidrios y Aluminios Zaragoza")

col_left, col_right = st.columns([1, 1])

with col_left:
    st.subheader("Configuración")
    cliente = st.text_input("Nombre del Cliente", "Kelly Zaragoza")
    sistema_nom = st.selectbox("Tipo de Estructura", ["Ventana Corrediza", "Ventana Fija", "Puerta Batiente", "Cancel de Baño"])
    
    # Entradas en milímetros
    ancho_val = st.number_input("Ancho Total (mm)", min_value=1, value=1200)
    alto_val = st.number_input("Alto Total (mm)", min_value=1, value=1000)
    
    # Cálculo de precio (Área m2 x Precio unitario)
    precio_unitario = st.number_input("Precio por m² (MXN)", value=1850)
    area_m2 = (ancho_val / 1000) * (alto_val / 1000)
    total_mxn = area_m2 * precio_unitario

with col_right:
    st.subheader("Vista Previa")
    st.info(f"**Área total:** {area_m2:.2f} m²")
    st.success(f"**Costo Estimado:** ${total_mxn:,.2f} MXN")
    
    # Simulación de dibujo técnico escalado
    c_w = min(ancho_val / 5, 250)
    c_h = min(alto_val / 5, 250)
    st.markdown(f"""
        <div style="border: 2px solid {AZUL_ZARAGOZA}; width: {c_w}px; height: {c_h}px; background: #f0f8ff; margin: auto; display: flex; align-items: center; justify-content: center; font-weight: bold; color: {AZUL_ZARAGOZA};">
            {ancho_val} x {alto_val} mm
        </div>
    """, unsafe_allow_html=True)

# Lógica simple de despiece para la tabla interna
datos_despiece = {
    "Componente": ["Marco Perimetral", "Hojas Móviles", "Cristales", "Herrajes"],
    "Cantidad": [1, 2, 2, 1],
    "Medida (mm)": [f"{ancho_val} x {alto_val}", f"{int(ancho_val/2)} x {alto_val-40}", "A medida", "Kit completo"]
}
df_resumen = pd.DataFrame(datos_despiece)

st.write("---")
if st.button("🖨️ Generar PDF Profesional"):
    pdf_output = generar_pdf_estilo_pro(cliente, ancho_val, alto_val, sistema_nom, total_mxn, df_resumen)
    st.download_button(
        label="📥 Descargar Nota de Venta",
        data=pdf_output,
        file_name=f"Presupuesto_{cliente}_{datetime.date.today()}.pdf",
        mime="application/pdf"
    )
