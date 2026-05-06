"""
pages/admin.py — Panel de administración del asesor.
Incluye su propio flujo de autenticación para funcionar
correctamente como página separada en Streamlit.
"""

import streamlit as st
import yaml
import os
import sys
from yaml.loader import SafeLoader
import streamlit_authenticator as stauth

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import registro

st.set_page_config(
    page_title="Administración",
    page_icon="🔧",
    layout="wide",
)

CONFIG_PATH     = "config.yaml"
ASESOR_USERNAME = "marioeaj"
MARCA_FIRMA     = os.environ.get("NOMBRE_FIRMA", "Tu Firma de Inversiones")

# ─────────────────────────────────────────────
#  AUTENTICACIÓN — necesaria en cada página
# ─────────────────────────────────────────────
if not os.path.exists(CONFIG_PATH):
    st.error("No se encontró config.yaml")
    st.stop()

with open(CONFIG_PATH) as f:
    config = yaml.load(f, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config["credentials"],
    config["cookie"]["name"],
    config["cookie"]["key"],
    config["cookie"]["expiry_days"],
)

# Streamlit reutiliza la cookie de sesión entre páginas —
# si ya iniciaste sesión en app.py, authentication_status
# ya estará en session_state. Si no, mostramos el login.
estado_auth = st.session_state.get("authentication_status")

if not estado_auth:
    st.markdown("### Acceso — Panel de administración")
    authenticator.login(location="main")
    estado_auth = st.session_state.get("authentication_status")

    if estado_auth is False:
        st.error("Usuario o contraseña incorrectos.")
        st.stop()
    if not estado_auth:
        st.stop()

username = st.session_state.get("username")
nombre   = st.session_state.get("name")

# ─────────────────────────────────────────────
#  VERIFICAR QUE ES EL ASESOR
# ─────────────────────────────────────────────
if username != ASESOR_USERNAME:
    st.error(f"Acceso restringido. Esta sección es solo para el asesor.")
    st.info(f"Estás conectado como: **{nombre}** (`{username}`)")
    authenticator.logout("Cerrar sesión", "main")
    st.stop()

# ─────────────────────────────────────────────
#  PANEL DE ADMINISTRACIÓN
# ─────────────────────────────────────────────
col_titulo, col_logout = st.columns([4, 1])
with col_titulo:
    st.markdown("## Panel de administración")
    st.caption(f"Conectado como {nombre} · {MARCA_FIRMA}")
with col_logout:
    authenticator.logout("Cerrar sesión", "main")

st.divider()

# ── Solicitudes pendientes ───────────────────
st.markdown("### Solicitudes de acceso pendientes")

pendientes = registro.obtener_pendientes()

if not pendientes:
    st.success("No hay solicitudes pendientes en este momento.")
else:
    st.info(f"{len(pendientes)} solicitud(es) esperando aprobación.")
    st.markdown("")

    for uname, datos in pendientes.items():
        with st.container(border=True):
            col_info, col_fecha, col_acciones = st.columns([3, 2, 1])

            with col_info:
                st.markdown(f"**{datos['name']}**")
                st.caption(f"Usuario: `{uname}`")
                st.caption(f"Email: {datos['email']}")

            with col_fecha:
                st.caption("Solicitado:")
                st.caption(datos['fecha'])

            with col_acciones:
                if st.button("✅ Aprobar", key=f"ap_{uname}", use_container_width=True, type="primary"):
                    if registro.aprobar_usuario(uname, MARCA_FIRMA):
                        st.success(f"**{datos['name']}** aprobado.")
                        st.info(f"Recuerda crear **{uname}.xlsx** con su portafolio.")
                        st.rerun()

                if st.button("❌ Rechazar", key=f"re_{uname}", use_container_width=True):
                    if registro.rechazar_usuario(uname, MARCA_FIRMA):
                        st.warning(f"Solicitud de {datos['name']} rechazada.")
                        st.rerun()

st.divider()

# ── Usuarios activos ─────────────────────────
st.markdown("### Usuarios activos")

with open(CONFIG_PATH) as f:
    config_actual = yaml.safe_load(f)

activos = config_actual.get("credentials", {}).get("usernames", {})
clientes = {u: d for u, d in activos.items() if u != ASESOR_USERNAME}

if not clientes:
    st.info("No hay clientes activos todavía.")
else:
    for uname, datos in clientes.items():
        with st.container(border=True):
            col_u, col_archivo = st.columns([3, 2])
            with col_u:
                st.markdown(f"**{datos['name']}**")
                st.caption(f"`{uname}` · {datos.get('email', '—')}")
            with col_archivo:
                archivo = f"{uname}.xlsx"
                if os.path.exists(archivo):
                    st.success(f"📄 {archivo} ✓", icon="✅")
                else:
                    st.error(f"📄 {archivo} — falta subir el Excel", icon="⚠️")
