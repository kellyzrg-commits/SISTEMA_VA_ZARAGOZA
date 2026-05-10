import streamlit as st
import mysql.connector
from fpdf import FPDF
import pandas as pd
from datetime import datetime
import random
import base64

# --- 1. SISTEMA DE SEGURIDAD (PUNTO 4: LOGIN) ---
def check_password():
    def password_guessed():
        if st.session_state["password"] == st.secrets["admin_password"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.text_input("Acceso al Sistema - VA Zaragoza", type="password", on_change=password_guessed, key="password")
        return False
    elif not st.session_state["password_correct"]:
        st.text_input("Acceso al Sistema - VA Zaragoza", type="password", on_change=password_guessed, key="password")
        st.error("😕 Contraseña incorrecta")
        return False
    else:
        return True

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="VA Zaragoza Enterprise", page_icon="🏢", layout="wide")

if check_password():
    # --- ESTILOS DE INTERFAZ ---
    st.markdown("""
        <style>
        .main { background-color: #f8f9fa; }
        .stMetric { background-color: white; padding: 20px; border-radius: 12px; border-top: 5px solid #1e3a8a; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }
        .stTabs [aria-selected="true"] { background-color: #1e3a8a !important; color: white !important; }
        </style>
        """, unsafe_allow_html=True)

    # --- CONEXIÓN DB (SIN ALTERAR) ---
    def conectar_db():
        try:
            return mysql.connector.connect(
                user=st.secrets.mysql.user, password=st.secrets.mysql.password,
                host=st.secrets.mysql.host, port=st.secrets.mysql.port,
                database=st.secrets.mysql.database, ssl_ca='ca.pem'
            )
        except: return None

    # --- PUNTO 1: GESTIÓN DE PRECIOS DINÁMICA ---
    # Inicializamos precios en la sesión si no existen
    if 'precios_m2' not in st.session_state:
        st.session_state.precios_m2 = {"Serie 20": 1250, "Serie 35": 1550, "Eurovent": 2950, "Templado": 3600}

    # --- LÓGICA DE ACTUALIZACIÓN DE ESTADO (PUNTO 3) ---
    def actualizar_estado(id_pre, nuevo_estado):
        conn = conectar_db()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("UPDATE presupuestos SET estado = %s WHERE id_presupuesto = %s", (nuevo_estado, id_pre))
                conn.commit()
                return True
            finally: conn.close()
        return False

    def guardar_registro(datos):
        conn = conectar_db()
        if not conn: return False
        try:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO clientes (folio_vaz, nombre_completo) VALUES (%s, %s)", (datos['folio'], datos['nombre']))
            id_cli = cursor.lastrowid
            query = "INSERT INTO presupuestos (id_cliente, ancho, alto, importe_neto, fecha_emision, estado) VALUES (%s, %s, %s, %s, %s, %s)"
            cursor.execute(query, (id_cli, datos['ancho'], datos['alto'], datos['monto'], datetime.now().date(), 'Cotizado'))
            conn.commit()
            return True
        except: return False
        finally: conn.close()

    # --- GENERADOR DE PDF (SIN IVA) ---
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
        pdf.cell(90, 8, "SISTEMA", 1, 0, 'C', fill=True)
        pdf.cell(30, 8, "MEDIDAS", 1, 0, 'C', fill=True)
        pdf.cell(30, 8, "ÁREA", 1, 0, 'C', fill=True)
        pdf.cell(40, 8, "PRECIO NETO", 1, 1, 'C', fill=True)
        pdf.set_font('Arial', '', 10)
        pdf.cell(90, 12, f" {datos['sistema']}", 1, 0, 'L')
        pdf.cell(30, 12, f" {datos['ancho']}x{datos['alto']}", 1, 0, 'C')
        pdf.cell(30, 12, f" {((datos['ancho']*datos['alto'])/1000000):.2f}m2", 1, 0, 'C')
        pdf.cell(40, 12, f" $ {datos['monto']:,.2f}", 1, 1, 'R')
        return pdf.output(dest='S').encode('latin-1')

    # --- DIBUJO TÉCNICO (SVG) ---
    def dibujar_svg(ancho, alto, acabado):
        colores = {"Blanco": "#FFFFFF", "Negro": "#262626", "Natural": "#A6A6A6", "Madera": "#734A29"}
        hex_c = colores.get(acabado, "#A6A6A6")
        base = 350
        w = base if ancho >= alto else (ancho / alto) * base
        h = base if alto > ancho else (alto / ancho) * base
        return f"""
        <svg width="{w + 60}" height="{h + 60}" viewBox="0 0 {w + 60} {h + 60}" xmlns="http://www.w3.org/2000/svg">
            <rect x="30" y="10" width="{w}" height="{h}" fill="#d1e9ff" stroke="{hex_c}" stroke-width="12" rx="2"/>
            <line x1="{w/2 + 30}" y1="10" x2="{w/2 + 30}" y2="{h + 10}" stroke="{hex_c}" stroke-width="5"/>
            <text x="{w/2 + 10}" y="{h + 40}" font-family="Arial" font-size="12" fill="#1e3a8a" font-weight="bold">{ancho} mm</text>
            <text x="10" y="{h/2 + 20}" font-family="Arial" font-size="12" fill="#1e3a8a" font-weight="bold" transform="rotate(-90, 20, {h/2 + 20})">{alto} mm</text>
        </svg>
        """

    # --- INTERFAZ DE USUARIO ---
    st.title("🏢 VA Zaragoza Enterprise")
    
    tabs = st.tabs(["📝 Cotizador Pro", "📋 Seguimiento", "📊 Dashboard", "⚙️ Admin Precios"])

    # --- TAB 1: COTIZADOR ---
    with tabs[0]:
        c1, c2 = st.columns([1, 1.2])
        with c1:
            nombre = st.text_input("Nombre del Cliente")
            f1, f2 = st.columns(2)
            sis = f1.selectbox("Línea", list(st.session_state.precios_m2.keys()))
            col_alum = f2.selectbox("Acabado", ["Blanco", "Negro", "Natural", "Madera"])
            
            f3, f4 = st.columns(2)
            anc = f3.number_input("Ancho (mm)", min_value=100, value=1200)
            alt = f4.number_input("Alto (mm)", min_value=100, value=1500)
            
            # Punto 2: Validación de Ingeniería
            if anc > 2500 or alt > 2500:
                st.warning("⚠️ Medida crítica detectada. Consultar espesor de vidrio recomendado.")

            total = ((anc * alt) / 1000000) * st.session_state.precios_m2[sis]
            st.metric("Total Neto", f"${total:,.2f}")

            if st.button("💾 Guardar y Generar PDF"):
                if nombre:
                    fol = f"VAZ-{random.randint(1000, 9999)}"
                    d = {'nombre': nombre, 'ancho': anc, 'alto': alt, 'monto': total, 'folio': fol, 'sistema': sis, 'color': col_alum}
                    if guardar_registro(d):
                        st.success(f"Registrado con éxito. Folio: {fol}")
                        st.download_button("📥 Descargar PDF", generar_pdf(d), f"{fol}.pdf")
                else: st.error("Ingresa el nombre del cliente.")

        with c2:
            st.subheader("Vista Previa")
            st.markdown(f'<div style="display:flex; justify-content:center; background:white; padding:25px; border-radius:15px; border:1px solid #ddd;">{dibujar_svg(anc, alt, col_alum)}</div>', unsafe_allow_html=True)

    # --- TAB 2: SEGUIMIENTO (PUNTO 3) ---
    with tabs[1]:
        st.subheader("Control de Producción")
        conn = conectar_db()
        if conn:
            df = pd.read_sql("SELECT p.id_presupuesto, c.nombre_completo, p.importe_neto, p.estado FROM presupuestos p JOIN clientes c ON p.id_cliente = c.id_cliente ORDER BY p.id_presupuesto DESC", conn)
            for index, row in df.iterrows():
                col_a, col_b, col_c = st.columns([2, 1, 1])
                col_a.write(f"**{row['nombre_completo']}** - ${row['importe_neto']:,.2f}")
                nuevo_st = col_b.selectbox("Estado", ["Cotizado", "En Proceso", "Terminado", "Entregado"], key=f"sel_{row['id_presupuesto']}", index=["Cotizado", "En Proceso", "Terminado", "Entregado"].index(row['estado']))
                if col_c.button("Actualizar", key=f"btn_{row['id_presupuesto']}"):
                    if actualizar_estado(row['id_presupuesto'], nuevo_st):
                        st.rerun()
            conn.close()

    # --- TAB 3: DASHBOARD (PUNTO 6) ---
    with tabs[2]:
        st.subheader("Analítica de Negocio")
        m1, m2 = st.columns(2)
        m1.metric("Proyección de Ingresos", "$94,200", "+8%")
        m2.metric("Sistema más Vendido", "Eurovent")
        st.bar_chart(pd.DataFrame({'Ventas': [15, 25, 40, 10]}, index=list(st.session_state.precios_m2.keys())))

    # --- TAB 4: ADMIN PRECIOS (PUNTO 1) ---
    with tabs[3]:
        st
