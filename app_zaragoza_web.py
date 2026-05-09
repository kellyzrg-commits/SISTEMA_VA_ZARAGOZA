import streamlit as st
import pandas as pd
from fpdf import FPDF
import datetime

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="VA Zaragoza - Gestión de Ventas", layout="wide")

# --- CLASE PDF PERSONALIZADA (ESTILO PROFESIONAL) ---
class PDF(FPDF):
    def header(self):
        try:
            # Intenta cargar el logo de Vidrios y Aluminios Zaragoza
            self.image('assets/logo_zaragoza.png', 10, 8, 50)
        except:
            self.set_font('Arial', 'B', 12)
            self.cell(50, 10, 'VIDRIOS Y ALUMINIOS ZARAGOZA')
        
        self.set_font('Arial', '', 9)
        self.set_xy(140, 10)
        self.cell(60, 5, f"Fecha: {datetime.date.today()}", ln=True, align='R')
        self.set_x(140)
        self.cell(60, 5, "Nota de Venta / Presupuesto", ln=True, align='R')
        self.ln(20)

def generar_pdf_final(cliente, ancho, alto, sistema, df, total_precio):
    pdf = PDF()
    pdf.add_page()
    
    # Encabezado Cliente
    pdf.set_fill_color(240, 240, 240)
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(190, 8, f" DATOS DEL CLIENTE: {cliente.upper()}", 1, ln=True, fill=True)
    pdf.set_font('Arial', '', 10)
    pdf.cell(95, 8, f"Modelo: {sistema}", 1)
    pdf.cell(95, 8, f"Dimensiones: {ancho} x {alto} mm", 1, ln=True)
    
    pdf.ln(5)
    
    # Tabla de Despiece y Costos
    pdf.set_font('Arial', 'B', 9)
    pdf.set_fill_color(200, 200, 200)
    pdf.cell(80, 8, "DESCRIPCIÓN", 1, 0, 'C', fill=True)
    pdf.cell(30, 8, "CANTIDAD", 1, 0, 'C', fill=True)
    pdf.cell(40, 8, "MEDIDA (mm)", 1, 0, 'C', fill=True)
    pdf.cell(40, 8, "OBSERVACIONES", 1, 1, 'C', fill=True)
    
    pdf.set_font('Arial', '', 9)
    for i, row in df.iterrows():
        pdf.cell(80, 8, str(row['Componente']), 1)
        pdf.cell(30, 8, str(row['Cantidad']), 1, 0, 'C')
        pdf.cell(40, 8, str(row['Medida (mm)']), 1, 0, 'C')
        pdf.cell(40, 8, str(row['Observaciones']), 1, 1)
    
    # Total Final (Sin IVA como pediste)
    pdf.ln(5)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(150, 10, "TOTAL ESTIMADO (MXN):", 0, 0, 'R')
    pdf.cell(40, 10, f"${total_precio:,.2f}", 1, 1, 'C', fill=True)
    
    pdf.ln(10)
    pdf.set_font('Arial', 'I', 8)
    pdf.multi_cell(190, 5, "Esta cotización no incluye IVA. Precios sujetos a cambios según el material elegido.")
    
    return pdf.output(dest='S').encode('latin-1')

# --- INTERFAZ DE USUARIO ---
st.title("📂 Sistema de Ventas: Vidrios y Aluminios Zaragoza")

col_form, col_view = st.columns([1, 1])

with col_form:
    cliente = st.text_input("Nombre del Cliente", "Kelly Zaragoza")
    sistema = st.selectbox("Tipo de Trabajo", ["Ventana Corrediza", "Ventana Fija", "Puerta Batiente"])
    
    # Medidas en mm directamente
    ancho_mm = st.number_input("Ancho (mm)", min_value=1, value=1200)
    alto_mm = st.number_input("Alto (mm)", min_value=1, value=1000)
    
    precio_unitario = st.number_input("Precio por m² (Material + Mano de Obra)", value=1500)

with col_view:
    st.subheader("Vista Previa del Diseño")
    # Dibujo proporcional
    canvas_w = min(ancho_mm / 4, 300)
    canvas_h = min(alto_mm / 4, 300)
    st.markdown(f"""
        <div style="border: 3px solid #333; width: {canvas_w}px; height: {canvas_h}px; margin: auto; background: #cce7ff; position: relative;">
            <div style="position: absolute; width: 100%; top: 45%; text-align: center; font-size: 20px;">🪟</div>
            <p style="position: absolute; bottom: -30px; width: 100%; text-align: center;">{ancho_mm} mm</p>
            <p style="position: absolute; left: -90px; top: 40%; transform: rotate(-90deg);">{alto_mm} mm</p>
        </div>
    """, unsafe_allow_html=True)

# --- CÁLCULOS ---
area_m2 = (ancho_mm / 1000) * (alto_mm / 1000)
total_estimado = area_m2 * precio_unitario

# Lógica de despiece (serie 2" ejemplo)
zoclo_final = int((ancho_mm - 180) / 2) # Descuento de 180mm (18cm)

datos = {
    "Componente": ["Cabezal", "Sillar", "Jambas", "Zoclos", "Traslapes"],
    "Medida (mm)": [ancho_mm, ancho_mm, alto_mm, zoclo_final, alto_mm - 50],
    "Cantidad": [1, 1, 2, 2, 2],
    "Observaciones": ["Corte Recto", "Corte Recto", "Corte Recto", "Precisión mm", "Corte Recto"]
}
df_vista = pd.DataFrame(datos)

st.write("---")
st.table(df_vista)

if st.button("💾 Guardar y Descargar Cotización"):
    pdf_bytes = generar_pdf_final(cliente, ancho_mm, alto_mm, sistema, df_vista, total_estimado)
    st.download_button(
        label="📥 Descargar PDF para el Cliente",
        data=pdf_bytes,
        file_name=f"Cotizacion_{cliente}.pdf",
        mime="application/pdf"
    )
