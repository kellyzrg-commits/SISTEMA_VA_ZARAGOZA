import streamlit as st
import mysql.connector
from fpdf import FPDF
import pandas as pd
from datetime import datetime
import random
import base64

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Siatema VA Zaragoza | Profesional",
    page_icon="🏢",
    layout="wide"
)

# --- ESTILOS VISUALES (UI) ---
st.markdown("""
    <style>
    .main { background-color: #f4f7f9; }
    .stMetric { 
        background-color: #ffffff; 
        padding: 20px; 
        border-radius: 12px; 
        box-shadow: 0 4px 6px rgba(0,0,0,0.05); 
        border-top: 4px solid #1e3a8a; 
    }
    .stButton>button { 
        background-color: #1e3a8a; 
        color: white; 
        border-radius: 8px; 
        font-weight: bold; 
        width: 100%; 
        height: 3em;
    }
    </style>
    """, unsafe_allow_html=True)

# --- CONEXIÓN A BASE DE DATOS (SIN CAMBIOS) ---
def conectar_db():
    try:
        config = {
            'user': st.secrets.mysql.user,
            'password': st.secrets.mysql.password,
            'host': st.secrets.mysql.host,
            'port': st.secrets.mysql.port,
            'database': st.secrets.mysql.database,
            'ssl_ca': 'ca.pem'
        }
        return mysql.connector.connect(**config)
    except Exception as err:
        st.error(f"Error de conexión: {err}")
        return None

def guardar_registro(datos):
    conn = conectar_db()
    if not conn: return False
    try:
        cursor = conn.cursor()
        # 1. Insertar Cliente
        cursor.execute("INSERT INTO clientes (folio_vaz, nombre_completo) VALUES (%s, %s)", 
                       (datos['folio'], datos['nombre']))
        id_cliente = cursor.lastrowid
        
        # 2. Insertar Presupuesto
        query_pre = """
            INSERT INTO presupuestos 
            (id_cliente, ancho, alto, importe_neto, fecha_emision) 
            VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(query_pre, (id_cliente, datos['ancho'], datos['alto'], datos['monto'], datetime.now().date()))
        conn.commit()
        return True
    except Exception as e:
        st.error(f"Error al guardar: {e}")
        return False
    finally:
        conn.close()

# --- GENERADOR DE PDF (SIN IVA) ---
class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 16)
        self.set_text_color(24, 46, 82)
        self.cell(0, 10, 'VIDRIOS Y ALUMINIOS ZARAGOZA', 0, 1, 'C')
        self.set_font('Arial', '', 10)
        self.cell(0, 5, 'Presupuesto de Suministro e Instalación (Neto)', 0, 1, 'C')
        self.ln(10)

def generar_pdf(datos):
    pdf = PDF()
    pdf.add_page()
    # Encabezado azul
    pdf.set_fill_color(30, 58, 138); pdf.set_text_color(255); pdf.set_font('Arial', 'B', 11)
    pdf.cell(130, 10, f" CLIENTE: {datos['nombre'].upper()}", 1, 0, 'L', fill=True)
    pdf.cell(60, 10, f" FOLIO: {datos['folio']}", 1, 1, 'C', fill=True)
    
    pdf.set_text_color(0); pdf.set_font('Arial', '', 10)
    pdf.cell(130, 8, f" Fecha: {datetime.now().strftime('%d/%m/%Y')}", 1, 0, 'L')
    pdf.cell(60, 8, " Tipo: Cotización Privada", 1, 1, 'C')
    pdf.ln(10)
    
    # Tabla
    pdf.set_font('Arial', 'B', 10); pdf.set_fill_color(240, 240, 240)
    pdf.cell(80, 8, "SISTEMA / MATERIAL", 1, 0, 'C', fill=True)
    pdf.cell(35, 8, "ACABADO", 1, 0, 'C', fill=True)
    pdf.cell(35, 8, "MEDIDAS (mm)", 1, 0, 'C', fill=True)
    pdf.cell(40, 8, "PRECIO NETO", 1, 1, 'C', fill=True)
    
    pdf.set_font('Arial', '', 10)
    pdf.cell(80, 12, f" {datos['sistema']}", 1, 0, 'L')
    pdf.cell(35, 12, f" {datos['color']}", 1, 0, 'C')
    pdf.cell(35, 12, f" {datos['ancho']} x {datos['alto']}", 1, 0, 'C')
    pdf.set_font('Arial', 'B', 11)
    pdf.cell(40, 12, f" $ {datos['monto']:,.2f}", 1, 1, 'R')
    
    pdf.ln(20)
    pdf.set_font('Arial', 'I', 8)
    pdf.multi_cell(0, 5, "Nota: Los precios mostrados son netos y no incluyen IVA. Vigencia de 15 días naturales.")
    return pdf.output(dest='S').encode('latin-1')

# --- DIBUJO TÉCNICO DINÁMICO (SVG) ---
def dibujar_estructura(ancho, alto, acabado):
    colores = {"Blanco": "#FFFFFF", "Negro": "#262626", "Natural": "#A6A6A6", "Madera": "#734A29"}
    hex_c = colores.get(acabado, "#A6A6A6")
    
    # Escalar para que quepa en pantalla (max 350px)
    base = 350
    if ancho >= alto:
        w = base; h = (alto / ancho) * base
    else:
        h = base; w = (ancho / alto) * base

    svg = f"""
    <svg width="{w + 50}" height="{h + 50}" viewBox="0 0 {w + 50} {h + 50}" xmlns="http://www.w3.org/2000/svg">
        <rect x="25" y="10" width="{w}" height="{h}" fill="#d1e9ff" stroke="{hex_c}" stroke-width="10" rx="2"/>
        <line x1="{w/2 + 25}" y1="10" x2="{w/2 + 25}" y2="{h + 10}" stroke="{hex_c}" stroke-width="4"/>
        <text x="{w/2}" y="{h + 35}" font-family="Arial" font-size="14" fill="#1e3a8a" font-weight="bold">{ancho} mm</text>
        <text x="5" y="0" font-family="Arial" font-size="14" fill="#1e3a8a" font-weight="bold" transform="translate(15, {h/2 + 20}) rotate(-90)">{alto} mm</text>
    </svg>
    """
    return svg

# --- INTERFAZ PRINCIPAL ---
st.title("🏢 VA Zaragoza: Panel de Ingeniería")
st.markdown("---")

t1, t2 = st.tabs(["📝 Generar Presupuesto", "📜 Historial de Clientes"])

with t1:
    c_form, c_prev = st.columns([1, 1.2])
    
    with c_form:
        st.subheader("Configuración Técnica")
        nombre_cli = st.text_input("Nombre del Cliente")
        
        f1, f2 = st.columns(2)
        sis = f1.selectbox("Línea", ["Serie 20", "Serie 35", "Eurovent", "Templado"])
        col = f2.selectbox("Acabado", ["Blanco", "Negro", "Natural", "Madera"])
        
        f3, f4 = st.columns(2)
        anc_mm = f3.number_input("Ancho (mm)", min_value=100, value=1000, step=10)
        alt_mm = f4.number_input("Alto (mm)", min_value=100, value=1200, step=10)
        
        # Precios por M2
        precios_m2 = {"Serie 20": 1250, "Serie 35": 1550, "Eurovent": 2900, "Templado": 3600}
        total_neto = ((anc_mm * alt_mm) / 1000000) * precios_m2[sis]
        
        st.metric("Total Neto (Sin IVA)", f"${total_neto:,.2f} MXN")
        
        if st.button("🚀 Guardar y Generar Documento"):
            if nombre_cli:
                folio_vaz = f"VAZ-{random.randint(1000, 9999)}"
                info_final = {'nombre': nombre_cli, 'ancho': anc_mm, 'alto': alt_mm, 'monto': total_neto, 
                             'folio': folio_vaz, 'sistema': sis, 'color': col}
                
                if guardar_registro(info_final):
                    st.success(f"Registro guardado: {folio_vaz}")
                    pdf_out = generar_pdf(info_final)
                    st.download_button("📥 Descargar PDF Oficial", pdf_out, f"{folio_vaz}.pdf", "application/pdf")
            else:
                st.warning("El nombre del cliente es obligatorio.")

    with c_prev:
        st.subheader("Previsualización de Estructura")
        st.info(f"Visualización en acabado: **{col}**")
        grafico = dibujar_estructura(anc_mm, alt_mm, col)
        st.markdown(f'<div style="display: flex; justify-content: center; background: white; padding: 30px; border-radius: 20px; border: 1px solid #ddd;">{grafico}</div>', unsafe_allow_html=True)

with t2:
    st.subheader("Registros en Base de Datos")
    db_conn = conectar_db()
    if db_conn:
        query_hist = """
            SELECT c.folio_vaz as 'Folio', c.nombre_completo as 'Cliente', 
                   p.importe_neto as 'Monto', p.fecha_emision as 'Fecha'
            FROM presupuestos p 
            JOIN clientes c ON p.id_cliente = c.id_cliente 
            ORDER BY p.id_presupuesto DESC
        """
        df_hist = pd.read_sql(query_hist, db_conn)
        st.dataframe(df_hist, use_container_width=True, hide_index=True)
        db_conn.close()
