import streamlit as st
import pandas as pd
from fpdf import FPDF
from datetime import datetime
import random
import base64
import matplotlib.pyplot as plt
import io

# ==========================================
# CONFIGURACIÓN DE LA APLICACIÓN (UI/UX)
# ==========================================
st.set_page_config(
    page_title="SISTEMA VA ZARAGOZA",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS - Minimalista Industrial Moderno
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Roboto', sans-serif;
    }
    
    /* Paleta de Colores: Azul Aluminio (#0f172a), Negro, Blanco */
    .stApp { background-color: #ffffff; }
    
    .sidebar .sidebar-content { background-color: #0f172a; }
    
    h1, h2, h3 { color: #0f172a; font-weight: 700; }
    
    .card {
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
    }
    
    .total-box {
        background-color: #0f172a;
        color: white;
        padding: 20px;
        border-radius: 8px;
        text-align: center;
        margin-top: 20px;
    }
    .total-box h2 { color: #00d2ff; margin: 0; font-size: 2.5rem; }
    
    /* Botones Grandes e Intuitivos */
    .stButton>button {
        width: 100%;
        background-color: #0f172a;
        color: white;
        border: none;
        padding: 15px;
        font-size: 18px;
        font-weight: bold;
        border-radius: 8px;
        transition: 0.3s;
    }
    .stButton>button:hover { background-color: #1e293b; box-shadow: 0 4px 12px rgba(15, 23, 42, 0.4); }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# MOTOR DE INGENIERÍA Y COSTOS
# ==========================================
class VAZ_Motor:
    # Costos base de MATERIAL por m2 (Se multiplicarán para obtener ganancia)
    PRECIOS_BASE = {
        "Línea 2”": 800,   # Costo puro de material aprox
        "Línea 3”": 1100,
        "Eurovent": 1800
    }

    @staticmethod
    def calcular_cotizacion(ancho, alto, linea, color):
        # 1. Calcular Área en m2
        area_m2 = (ancho * alto) / 1000000.0
        
        # 2. Costo Base de Material
        costo_material = area_m2 * VAZ_Motor.PRECIOS_BASE.get(linea, 1000)
        
        # 3. Factor de Color (Ej. Madera es más caro)
        factor_color = 1.35 if color == "Madera" else 1.0
        costo_material *= factor_color
        
        # 4. APLICAR MARGEN DE GANANCIA (50%)
        # Si el costo es 1000, cobramos 1500.
        precio_venta_final = costo_material * 1.50 
        
        return area_m2, precio_venta_final

    @staticmethod
    def generar_hoja_taller(ancho, alto, tipo):
        """Fórmulas reales de taller en milímetros"""
        if tipo == "Ventana Corrediza":
            # Fórmula: (Ancho total - 18) / 2
            ancho_hoja = (ancho - 18) / 2
            # Fórmula: Alto total - 45 (o -4 según tu nota, usaré 45 estándar de ventana)
            alto_hoja = alto - 45
            
            return [
                {"Pieza": "Cabezal/Zoclo (Hoja)", "Cant": 4, "Corte": f"{ancho_hoja:.1f} mm"},
                {"Pieza": "Cerco/Traslape (Hoja)", "Cant": 4, "Corte": f"{alto_hoja:.1f} mm"},
                {"Pieza": "Riel/Bolsa (Marco)", "Cant": 2, "Corte": f"{ancho - 12} mm"},
                {"Pieza": "Jambas (Marco)", "Cant": 2, "Corte": f"{alto} mm"},
                {"Pieza": "Cristal", "Cant": 2, "Corte": f"{ancho_hoja - 65:.1f} x {alto_hoja - 65:.1f} mm"}
            ]
        return []

# ==========================================
# GENERADOR DE DIBUJO TÉCNICO (Matplotlib)
# ==========================================
def generar_dibujo_tecnico(ancho, alto, tipo):
    fig, ax = plt.subplots(figsize=(6, 4))
    
    # Dibujar marco exterior
    marco = plt.Rectangle((0, 0), ancho, alto, fill=False, edgecolor='black', linewidth=3)
    ax.add_patch(marco)
    
    if "Corrediza" in tipo:
        # Dibujar división central
        mitad = ancho / 2
        ax.plot([mitad, mitad], [0, alto], color='black', linewidth=2)
        
        # Flechas de deslizamiento
        ax.annotate('◄═══════', xy=(mitad/2, alto/2), ha='center', va='center', fontsize=12)
        ax.annotate('═══════►', xy=(mitad + mitad/2, alto/2), ha='center', va='center', fontsize=12)
    elif "Abatible" in tipo:
        ax.annotate('↻', xy=(ancho/2, alto/2), ha='center', va='center', fontsize=24)

    # Acotaciones Automáticas
    ax.annotate(f'Ancho = {ancho} mm', xy=(ancho/2, alto + (alto*0.05)), ha='center', fontsize=10, color='#0f172a', weight='bold')
    ax.annotate(f'Alto = {alto} mm', xy=(-(ancho*0.05), alto/2), va='center', rotation=90, fontsize=10, color='#0f172a', weight='bold')

    # Configuración de los ejes
    ax.set_xlim(-ancho*0.1, ancho*1.1)
    ax.set_ylim(-alto*0.1, alto*1.2)
    ax.axis('off') # Ocultar ejes coordenados
    
    # Guardar en memoria
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', dpi=150)
    buf.seek(0)
    return buf

# ==========================================
# GENERADOR DE PDF PROFESIONAL
# ==========================================
class CotizacionPDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 18)
        self.set_text_color(15, 23, 42) # Azul Aluminio
        self.cell(0, 10, 'VIDRIOS Y ALUMINIOS ZARAGOZA', 0, 1, 'C')
        self.set_font('Arial', 'I', 10)
        self.set_text_color(100, 100, 100)
        self.cell(0, 5, 'Expertos en canceleria de aluminio, cristal templado, fachadas integrales y mucho mas...', 0, 1, 'C')
        self.ln(5)
        self.line(10, 30, 200, 30)

def crear_pdf(datos, imagen_buf):
    pdf = CotizacionPDF()
    pdf.add_page()
    
    # Datos Generales
    pdf.set_font('Arial', 'B', 10)
    pdf.set_fill_color(240, 240, 240)
    pdf.cell(130, 8, f" CLIENTE: {datos['cliente'].upper()}", 1, 0, 'L', 1)
    pdf.cell(60, 8, f" FOLIO: {datos['folio']}", 1, 1, 'C', 1)
    
    pdf.set_font('Arial', '', 9)
    pdf.cell(130, 8, f" Obra/Dirección: {datos['direccion']}", 1, 0, 'L')
    pdf.cell(60, 8, f" Fecha: {datetime.now().strftime('%d/%m/%Y')}", 1, 1, 'C')
    
    pdf.ln(5)
    
    # Descripción del Trabajo
    pdf.set_font('Arial', 'B', 11)
    pdf.cell(0, 8, "DESCRIPCIÓN DEL PROYECTO", 0, 1)
    pdf.set_font('Arial', '', 10)
    descripcion = f"Producto: {datos['tipo']} | Linea: {datos['linea']} | Color: {datos['color']} | Cristal: {datos['cristal']}\nDimensiones: {datos['ancho']} mm (Ancho) x {datos['alto']} mm (Alto)"
    pdf.multi_cell(0, 7, descripcion, border=1)
    
    # Insertar Dibujo Técnico
    pdf.ln(5)
    # Guardamos temporalmente la imagen para insertarla
    with open("temp_draw.png", "wb") as f:
        f.write(imagen_buf.getbuffer())
    pdf.image("temp_draw.png", x=60, w=90)
    
    # Total Final (SIN IVA, SIN COSTOS INTERNOS)
    pdf.ln(5)
    pdf.set_font('Arial', 'B', 16)
    pdf.set_fill_color(15, 23, 42)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(120, 15, " TOTAL A PAGAR NETO", 1, 0, 'R', 1)
    pdf.cell(70, 15, f"$ {datos['total']:,.2f} MXN ", 1, 1, 'R', 1)
    
    # Vigencia
    pdf.ln(10)
    pdf.set_font('Arial', 'I', 9)
    pdf.set_text_color(50, 50, 50)
    pdf.cell(0, 5, "Esta cotizacion tiene una vigencia de 15 dias naturales a partir de su fecha de emision.", 0, 1, 'C')
    
    return pdf.output(dest='S').encode('latin-1')

# ==========================================
# INTERFAZ PRINCIPAL STREAMLIT
# ==========================================
def main():
    st.title("🏢 Sistema VA Zaragoza - Panel de Control")
    
    # Menú lateral simulando los módulos requeridos
    menu = st.sidebar.radio("Navegación", ["📝 Nueva Cotización", "📦 Inventario (Sobrantes)", "👥 Clientes", "📊 Reportes"])
    
    if menu == "📝 Nueva Cotización":
        col1, col2 = st.columns([1, 1.2])
        
        with col1:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.subheader("Datos del Proyecto")
            cliente = st.text_input("Nombre del Cliente")
            direccion = st.text_input("Dirección (Opcional)")
            
            st.markdown("---")
            st.subheader("Configuración Técnica")
            tipo = st.selectbox("Producto", ["Ventana Corrediza", "Ventana Fija", "Puerta Abatible", "Cancel de Baño"])
            linea = st.selectbox("Línea de Aluminio", ["Línea 2”", "Línea 3”", "Eurovent"])
            color = st.selectbox("Color / Acabado", ["Blanco", "Negro", "Natural", "Madera"])
            cristal = st.selectbox("Cristal", ["Claro", "Filtrasol", "Esmerilado", "Templado"])
            
            # TODO EN MILÍMETROS
            c_ancho, c_alto = st.columns(2)
            ancho = c_ancho.number_input("Ancho (mm)", min_value=100, value=1500)
            alto = c_alto.number_input("Alto (mm)", min_value=100, value=1200)
            st.markdown('</div>', unsafe_allow_html=True)

        with col2:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.subheader("Visualización y Costos")
            
            # Generar y mostrar dibujo
            img_buf = generar_dibujo_tecnico(ancho, alto, tipo)
            st.image(img_buf, use_container_width=True)
            
            # Calcular Costo con 50% de ganancia
            area, total = VAZ_Motor.calcular_cotizacion(ancho, alto, linea, color)
            
            st.markdown(f"""
                <div class="total-box">
                    <p style="margin:0; font-size:14px; opacity:0.8;">Cálculo Área: {area:.2f} m² | Ganancia Aplicada: 50%</p>
                    <h2>$ {total:,.2f} MXN</h2>
                </div>
            """, unsafe_allow_html=True)
            
            # Mostrar Hoja de Taller (Solo visible en pantalla para el trabajador)
            with st.expander("🛠️ Ver Hoja de Taller (Cortes Internos)"):
                cortes = VAZ_Motor.generar_hoja_taller(ancho, alto, tipo)
                if cortes:
                    st.table(pd.DataFrame(cortes))
                else:
                    st.info("Fórmulas en desarrollo para este tipo de producto.")

            # Generar PDF
            if st.button("📄 GENERAR COTIZACIÓN OFICIAL"):
                if cliente:
                    folio = f"VAZ-{random.randint(1000, 9999)}"
                    datos_pdf = {
                        "cliente": cliente, "direccion": direccion, "folio": folio,
                        "tipo": tipo, "linea": linea, "color": color, "cristal": cristal,
                        "ancho": ancho, "alto": alto, "total": total
                    }
                    pdf_bytes = crear_pdf(datos_pdf, img_buf)
                    
                    st.success(f"¡Cotización {folio} generada exitosamente!")
                    st.download_button(
                        label="📥 Descargar PDF",
                        data=pdf_bytes,
                        file_name=f"Cotizacion_{folio}_{cliente}.pdf",
                        mime="application/pdf"
                    )
                else:
                    st.error("⚠️ Debes ingresar el nombre del cliente para generar el PDF.")
            st.markdown('</div>', unsafe_allow_html=True)
            
    elif menu == "📦 Inventario (Sobrantes)":
        st.info("Módulo de inventario y detección inteligente de sobrantes en construcción...")
        
if __name__ == "__main__":
    main()
