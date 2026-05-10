import streamlit as st
import mysql.connector
import pandas as pd
from datetime import datetime
import random

# --- CONFIGURACIÓN DE IDENTIDAD ---
st.set_page_config(page_title="Sistemas VAZ Zaragoza", layout="wide", page_icon="🏢")

# --- 1. CAPA DE DATOS (CONEXIÓN Y PERSISTENCIA) ---
class DatabaseManager:
    @staticmethod
    def conectar():
        try:
            return mysql.connector.connect(
                host=st.secrets["mysql"]["host"],
                user=st.secrets["mysql"]["user"],
                password=st.secrets["mysql"]["password"],
                database=st.secrets["mysql"]["database"],
                port=st.secrets["mysql"]["port"]
            )
        except Exception as e:
            st.error(f"Error de conexión: {e}")
            return None

    @classmethod
    def ejecutar_query(cls, query, valores=None, fetch=False):
        conn = cls.conectar()
        if not conn: return None
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(query, valores or ())
            resultado = cursor.fetchall() if fetch else None
            conn.commit()
            return resultado
        finally:
            conn.close()

# --- 2. LÓGICA DE NEGOCIO ---
def calcular_presupuesto(ancho, alto, costo_base, margen_color):
    area_m2 = (ancho * alto) / 1000000
    subtotal = area_m2 * float(costo_base)
    # Aplicar 50% mano de obra y margen de color
    total = (subtotal * 1.50) * margen_color
    return total

# --- 3. COMPONENTES VISUALES ---
def render_grafico_tecnico(ancho, alto, color_name, modelo):
    # Colores CSS para el dibujo
    colores_map = {
        "Blanco": "#FFFFFF", "Negro": "#1a1a1a", 
        "Natural": "#94a3b8", "Bronce": "#451a03", "Madera": "#78350f"
    }
    color_hex = colores_map.get(color_name, "#000000")
    
    # Escalado proporcional para el canvas
    max_dim = max(ancho, alto)
    scale = 300 / max_dim if max_dim > 0 else 1
    w_px, h_px = ancho * scale, alto * scale

    st.markdown(f"""
        <div style="background:#f1f5f9; border-radius:10px; padding:30px; display:flex; flex-direction:column; align-items:center; border:1px solid #cbd5e1;">
            <div style="width:{w_px}px; text-align:center; border-bottom:2px solid #64748b; margin-bottom:10px; color:#1e293b; font-weight:bold;">{ancho} mm</div>
            <div style="display:flex; align-items:center;">
                <div style="width:{w_px}px; height:{h_px}px; border:10px solid {color_hex}; background:rgba(14, 165, 233, 0.2); box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1); display:flex; align-items:center; justify-content:center;">
                    <span style="background:white; padding:5px; border-radius:5px; font-size:12px; color:black; font-weight:bold; border:1px solid {color_hex}">{modelo}</span>
                </div>
                <div style="height:{h_px}px; margin-left:15px; border-left:2px solid #64748b; display:flex; align-items:center; padding-left:10px; color:#1e293b; font-weight:bold;">{alto} mm</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

# --- 4. APLICACIÓN PRINCIPAL ---
def main():
    if 'logged_in' not in st.session_state: st.session_state.logged_in = False

    # --- LOGIN ---
    if not st.session_state.logged_in:
        st.title("🔐 Acceso VAZ Zaragoza")
        with st.form("login"):
            u = st.text_input("Usuario")
            p = st.text_input("Contraseña", type="password")
            if st.form_submit_button("Entrar"):
                res = DatabaseManager.ejecutar_query("SELECT * FROM usuarios WHERE nombre_usuario=%s AND password_hash=%s", (u, p), fetch=True)
                if res:
                    st.session_state.logged_in = True
                    st.session_state.update({"rol": res[0]['rol'], "nombre": res[0]['nombre_real'], "uid": res[0]['id_usuario']})
                    st.rerun()
                else: st.error("Credenciales incorrectas")
        return

    # --- PANEL DE CONTROL ---
    st.sidebar.title("VAZ Zaragoza")
    st.sidebar.write(f"Usuario: {st.session_state.nombre}")
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state.logged_in = False
        st.rerun()

    # --- MODO ADMIN: GESTIÓN DE PRECIOS ---
    if st.session_state.rol == 'administrador':
        st.header("⚙️ Configuración Global de Precios")
        precios = pd.DataFrame(DatabaseManager.ejecutar_query("SELECT * FROM configuracion_precios", fetch=True))
        if not precios.empty:
            editado = st.data_editor(precios, hide_index=True, disabled=["id_config", "concepto"])
            if st.button("Actualizar Base de Datos"):
                for _, r in editado.iterrows():
                    DatabaseManager.ejecutar_query("UPDATE configuracion_precios SET costo_base_m2=%s WHERE id_config=%s", (r['costo_base_m2'], r['id_config']))
                st.success("Lista de precios actualizada.")

    # --- MODO ASESOR: COTIZADOR TÉCNICO ---
    else:
        st.header("📝 Nueva Cotización Profesional")
        
        with st.form("cotizador"):
            c1, c2 = st.columns(2)
            with c1:
                st.subheader("👤 Cliente")
                nombre = st.text_input("Nombre Completo")
                tel = st.text_input("Teléfono")
                dir_obra = st.text_area("Dirección de la Obra")
            
            with c2:
                st.subheader("📐 Especificaciones")
                precios_db = pd.DataFrame(DatabaseManager.ejecutar_query("SELECT * FROM configuracion_precios", fetch=True))
                serie = st.selectbox("Serie de Aluminio", precios_db['concepto'].tolist())
                modelo = st.selectbox("Tipo de Producto", ["Ventana Corrediza", "Puerta Batiente", "Fijo", "Mosquitero"])
                
                m_colores = {"Blanco": 1.0, "Negro": 1.05, "Natural": 1.0, "Bronce": 1.10, "Madera": 1.20}
                color = st.selectbox("Acabado/Color", list(m_colores.keys()))
                
                f1, f2, f3 = st.columns(3)
                ancho = f1.number_input("Ancho (mm)", min_value=100, value=1000)
                alto = f2.number_input("Alto (mm)", min_value=100, value=1000)
                espesor = f3.selectbox("Cristal", ["6mm", "10mm Templado", "DuoVent"])

            st.divider()
            
            # Cálculos en tiempo real
            c_base = precios_db[precios_db['concepto'] == serie]['costo_base_m2'].values[0]
            total = calcular_presupuesto(ancho, alto, c_base, m_colores[color])
            
            # Renderizado del Gráfico
            render_grafico_tecnico(ancho, alto, color, modelo)
            
            st.write(f"## Presupuesto Estimado: ${total:,.2f} MXN")
            
            if st.form_submit_button("💾 Guardar y Finalizar"):
                if nombre and ancho > 100:
                    folio = f"VAZ-{random.randint(1000, 9999)}"
                    # Insertar Cliente
                    DatabaseManager.ejecutar_query("INSERT INTO clientes (folio_vaz, nombre_completo, telefono, direccion) VALUES (%s, %s, %s, %s)", (folio, nombre, tel, dir_obra))
                    # Obtener ID Cliente (Simplicidad para este ejemplo)
                    last_c = DatabaseManager.ejecutar_query("SELECT id_cliente FROM clientes ORDER BY id_cliente DESC LIMIT 1", fetch=True)[0]['id_cliente']
                    # Insertar Presupuesto
                    q_pre = "INSERT INTO presupuestos (id_cliente, id_usuario, serie, modelo, color, espesor, ancho_mm, alto_mm, monto_total) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
                    DatabaseManager.ejecutar_query(q_pre, (last_c, st.session_state.uid, serie, modelo, color, espesor, ancho, alto, total))
                    
                    st.success(f"¡Guardado! Folio: {folio}")
                    st.balloons()
                else: st.warning("Completa los campos obligatorios.")

if __name__ == "__main__":
    main()
