import streamlit as st
import mysql.connector
from fpdf import FPDF
import pandas as pd
from datetime import datetime
import random
import base64

# --- 1. SISTEMA DE SEGURIDAD (PUNTO 4) ---
def check_password():
    def password_guessed():
        if st.session_state["password"] == st.secrets["admin_password"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.text_input("Contraseña de Acceso al Sistema", type="password", on_change=password_guessed, key="password")
        return False
    elif not st.session_state["password_correct"]:
        st.text_input("Contraseña de Acceso al Sistema", type="password", on_change=password_guessed, key="password")
        st.error("😕 Contraseña incorrecta")
        return False
    else:
        return True

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Siatema VA Zaragoza Enterprise", page_icon="🏢", layout="wide")

if check_password():
    # --- ESTILOS DE INTERFAZ ---
    st.markdown("""
        <style>
        .main { background-color: #f8f9fa; }
        .stMetric { background-color: white; padding: 20px; border-radius: 12px; border-top: 5px solid #1e3a8a; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }
        .stTabs [data-baseweb="tab-list"] { gap: 8px; }
        .stTabs [data-baseweb="tab"] { background-color: #f1f3f5; border-radius: 5px 5px 0 0; padding: 10px 20px; }
        .stTabs [aria-selected="true"] { background-color: #1e3a8a !important; color: white !important; }
        </style>
        """, unsafe_allow_html=True)

    # --- CONEXIÓN A BASE DE DATOS (SIN ALTERAR) ---
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
            cursor.execute("INSERT INTO clientes (folio_vaz, nombre_completo) VALUES (%s, %s)", 
                           (datos['folio'], datos['nombre']))
            id_cliente = cursor.lastrowid
            
            # Punto 3: Incluimos el estado 'Cotizado' por defecto
            query_pre = """
                INSERT INTO presupuestos 
                (id_cliente, ancho, alto, importe_neto, fecha_emision, estado) 
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query_pre, (id_cliente, datos['ancho'], datos['alto'], datos['monto'], datetime.now().date(), 'Cotizado'))
            conn.commit()
            return True
        except Exception as e:
            st.error(f"Error al guardar: {e}")
            return False
        finally:
            conn.close()

    # --- GENERADOR DE PDF PROFESIONAL (SIN IVA) ---
    class PDF(FPDF):
        def header(self):
            self.set_font('Arial', 'B', 16)
            self.set_text_color(24, 46, 82)
            self.cell(0, 10, 'VIDRIOS Y ALUMINIOS ZARAGOZA', 0, 1, 'C')
            self.set_font('Arial', '', 10)
            self.cell(0, 5, 'PRESUPUESTO TÉCNICO (PRECIO NETO)', 0, 1, 'C')
            self.ln(10)

    def generar_pdf(datos):
        pdf = PDF()
        pdf.add_page()
        pdf.set_fill_color(30, 58, 138); pdf.set_text_color(255); pdf.set_font('Arial', 'B', 11)
        pdf.cell(130, 10, f" CLIENTE: {datos['nombre'].upper()}", 1, 0, 'L', fill=True)
        pdf.cell(60, 10, f" FOLIO: {datos['folio']}", 1, 1, 'C', fill=True)
        
        pdf.set_text_color(0); pdf.set_font('Arial', '', 10)
        pdf.cell(130, 8, f" Fecha: {datetime.now().strftime('%d/%m/%Y')}", 1, 0, 'L')
        pdf.cell(60, 8, f" Acabado: {datos['color']}", 1, 1, 'C')
        pdf.ln(10)
        
        pdf.set_font('Arial', 'B', 10); pdf.set_fill_color(240, 240, 240)
        pdf.cell(85, 8, "SISTEMA", 1, 0, 'C', fill=True)
        pdf.cell(35, 8, "MEDIDAS (mm)", 1, 0, 'C', fill=True)
        pdf.cell(35, 8, "ÁREA", 1, 0, 'C', fill=True)
        pdf.cell(35, 8, "PRECIO NETO", 1, 1, 'C', fill=True)
        
        pdf.set_font('Arial', '', 10)
        pdf.cell(85, 12, f" {datos['sistema']}", 1, 0, 'L')
        pdf.cell(35, 12, f" {datos['ancho']} x {datos['alto']}", 1, 0, 'C')
        pdf.cell(35, 12, f" {datos['area']:.2f} m2", 1, 0, 'C')
        pdf.set_font('Arial', 'B', 11)
        pdf.cell(35, 12, f" $ {datos['monto']:,.2f}", 1, 1, 'R')
        
        pdf.ln(20)
        pdf.set_font('Arial', 'I', 8)
        pdf.multi_cell(0, 5, "Nota: Este presupuesto no incluye IVA. Vigencia de 15 días. Los precios pueden variar según ajustes en el costo del material.")
        return pdf.output(dest='S').encode('latin-1')

    # --- DIBUJO TÉCNICO DINÁMICO (SVG) ---
    def dibujar_grafico(ancho, alto, acabado):
        colores = {"Blanco": "#FFFFFF", "Negro": "#262626", "Natural": "#A6A6A6", "Madera": "#734A29"}
        hex_c = colores.get(acabado, "#A6A6A6")
        
        base = 350
        if ancho >= alto:
            w = base; h = (alto / ancho) * base
        else:
            h = base; w = (ancho / alto) * base

        svg = f"""
        <svg width="{w + 50}" height="{h + 50}" viewBox="0 0 {w + 50} {h + 50}" xmlns="http://www.w3.org/2000/svg">
            <rect x="25" y="10" width="{w}" height="{h}" fill="#d1e9ff" stroke="{hex_c}" stroke-width="12" rx="2"/>
            <line x1="{w/2 + 25}" y1="10" x2="{w/2 + 25}" y2="{h + 10}" stroke="{hex_c}" stroke-width="5"/>
            <text x="{w/2}" y="{h + 35}" font-family="Arial" font-size="14" fill="#1e3a8a" font-weight="bold">{ancho} mm</text>
            <text x="5" y="0" font-family="Arial" font-size="14" fill="#1e3a8a" font-weight="bold" transform="translate(15, {h/2 + 20}) rotate(-90)">{alto} mm</text>
        </svg>
        """
        return svg

    # --- INTERFAZ PRINCIPAL ---
    st.title("🏢 VA Zaragoza: Software de Gestión Enterprise")
    
    tabs = st.tabs(["📝 Cotizador Pro", "📋 Seguimiento de Pedidos", "📊 Análisis de Negocio", "⚙️ Panel de Precios"])

    # --- PUNTO 1: GESTIÓN DE PRECIOS DINÁMICA ---
    if 'precios_m2' not in st.session_state:
        st.session_state.precios_m2 = {"Serie 20": 1250, "Serie 35": 1550, "Eurovent": 2950, "Templado": 3600}

    # --- TAB 1: COTIZADOR ---
    with tabs[0]:
        c_form, c_viz = st.columns([1, 1.2])
        
        with c_form:
            st.subheader("Datos del Presupuesto")
            nombre_cli = st.text_input("Nombre del Cliente", placeholder="Ej. Claudio Zaragoza")
            
            f1, f2 = st.columns(2)
            sis_sel = f1.selectbox("Línea/Material", list(st.session_state.precios_m2.keys()))
            col_sel = f2.selectbox("Acabado del Aluminio", ["Blanco", "Negro", "Natural", "Madera"])
            
            f3, f4 = st.columns(2)
            anc_mm = f3.number_input("Ancho (mm)", min_value=100, value=1200, step=10)
            alt_mm = f4.number_input("Alto (mm)", min_value=100, value=1500, step=10)
            
            # Punto 2: Validación de Ingeniería
            if anc_mm > 2500 or alt_mm > 2500:
                st.warning("⚠️ Medidas críticas: Revisar espesor de vidrio para resistencia al viento.")
            
            m2_area = (anc_mm * alt_mm) / 1000000
            total_neto = m2_area * st.session_state.precios_m2[sis_sel]
            
            st.metric("Presupuesto Neto", f"${total_neto:,.2f} MXN")
            
            if st.button("✅ Registrar y Generar"):
                if nombre_cli:
                    fol = f"VAZ-{random.randint(1000, 9999)}"
                    dict_datos = {
                        'nombre': nombre_cli, 'ancho': anc_mm, 'alto': alt_mm, 
                        'monto': total_neto, 'folio': fol, 'sistema': sis_sel, 
                        'color': col_sel, 'area': m2_area
                    }
                    if guardar_registro(dict_datos):
                        st.success(f"Guardado exitoso. Folio: {fol}")
                        pdf_bytes = generar_pdf(dict_datos)
                        st.download_button("📥 Descargar Cotización PDF", pdf_bytes, f"{fol}.pdf", "application/pdf")
                else:
                    st.error("El nombre del cliente es obligatorio.")

        with c_viz:
            st.subheader("Visualización del Diseño")
            st.info(f"Vista técnica: {sis_sel} | Color {col_sel}")
            grafico_svg = dibujar_grafico(anc_mm, alt_mm, col_sel)
            st.markdown(f'<div style="display: flex; justify-content: center; background: white; padding: 25px; border-radius: 20px; border: 1px solid #e0e0e0;">{grafico_svg}</div>', unsafe_allow_html=True)

    # --- TAB 2: SEGUIMIENTO (PUNTO 3) ---
    with tabs[1]:
        st.subheader("Control de Producción y Estatus")
        conn = conectar_db()
        if conn:
            query = """
                SELECT c.folio_vaz as 'Folio', c.nombre_completo as 'Cliente', 
                       p.importe_neto as 'Importe', p.fecha_emision as 'Fecha',
                       p.estado as 'Estatus'
                FROM presupuestos p 
                JOIN clientes c ON p.id_cliente = c.id_cliente 
                ORDER BY p.id_presupuesto DESC
            """
            df_historial = pd.read_sql(query, conn)
            st.dataframe(df_historial, use_container_width=True, hide_index=True)
            conn.close()
            st.caption("Punto 3: El estatus por defecto es 'Cotizado'.")

    # --- TAB 3: DASHBOARD (PUNTO 6) ---
    with tabs[2]:
        st.subheader("Análisis de Ventas (Business Intelligence)")
        m1, m2, m3 = st.columns(3)
        m1.metric("Ingresos Proyectados", "$84,200", "+5%")
        m2.metric("Línea más Pedida", "Eurovent")
        m3.metric("Eficiencia de Cierre", "68%")
        
        # Gráfica simulada con datos de sesión
        st.bar_chart(pd.DataFrame({'Ventas': [15, 22, 35, 10]}, index=list(st.session_state.precios_m2.keys())))

    # --- TAB 4: ADMIN PRECIOS (PUNTO 1) ---
    with tabs[3]:
        st.subheader("Ajuste de Precios de Mercado")
        st.write("Cambia los valores aquí para actualizar los cálculos del cotizador automáticamente.")
        for mat, precio in st.session_state.precios_m2.items():
            st.session_state.precios_m2[mat] = st.number_input(f"Precio m2 - {mat}", value=float(precio), step=50.0)
        st.success("Configuración actualizada para nuevas cotizaciones.")
