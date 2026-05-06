import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
from datetime import datetime
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
import registro  # módulo de auto-registro

# ─────────────────────────────────────────────
#  CONFIGURACIÓN DE PÁGINA
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Portal de inversiones",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
#  BRANDING
# ─────────────────────────────────────────────
MARCA = {
    "nombre_firma":   os.environ.get("NOMBRE_FIRMA", "Servicios Maravilla del Norte"),
    "color_primario": "#185FA5",
    "color_acento":   "#1D9E75",
    "logo_path":      "logo.png",
}

def inyectar_css():
    p = MARCA["color_primario"]
    a = MARCA["color_acento"]
    st.markdown(f"""
    <style>
        header[data-testid="stHeader"] {{ background-color: {p}; }}
        [data-testid="stSidebar"] {{ background-color: #f8f9fc; border-right: 1px solid #e8eaf0; }}
        .stButton > button[kind="primary"] {{
            background-color: {p}; border: none; color: white;
            border-radius: 8px; padding: 10px 24px; font-weight: 500;
        }}
        .stButton > button[kind="primary"]:hover {{ background-color: {a}; }}
        #MainMenu {{ visibility: hidden; }}
        footer {{ visibility: hidden; }}
        .firma-nombre {{ font-size: 15px; font-weight: 600; color: {p}; margin: 0; }}
        .firma-sub {{ font-size: 11px; color: #888; margin-top: 2px; }}
        .revision-card {{
            background: linear-gradient(135deg, {p}18, {a}18);
            border: 1px solid {p}44;
            border-radius: 12px; padding: 20px 24px; margin: 16px 0;
        }}
        .registro-card {{
            background: #f8f9fc; border: 1px solid #e0e4ea;
            border-radius: 12px; padding: 20px 24px; margin-top: 8px;
        }}
    </style>
    """, unsafe_allow_html=True)

inyectar_css()

COLORES = {
    "azul":   MARCA["color_primario"],
    "verde":  MARCA["color_acento"],
    "rojo":   "#D85A30",
    "ambar":  "#BA7517",
    "morado": "#534AB7",
    "gris":   "#888780",
}

# ─────────────────────────────────────────────
#  AUTENTICACIÓN
# ─────────────────────────────────────────────
CONFIG_PATH = "config.yaml"

if not os.path.exists(CONFIG_PATH):
    st.error("No se encontró config.yaml — ejecuta `python setup_usuarios.py` primero.")
    st.stop()

with open(CONFIG_PATH) as f:
    config = yaml.load(f, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config["credentials"],
    config["cookie"]["name"],
    config["cookie"]["key"],
    config["cookie"]["expiry_days"],
)

# ─────────────────────────────────────────────
#  PANTALLA DE LOGIN + REGISTRO
# ─────────────────────────────────────────────
estado_auth = st.session_state.get("authentication_status")

if not estado_auth:
    # Centrar el contenido
    _, col_centro, _ = st.columns([1, 2, 1])

    with col_centro:
        # Logo o nombre de la firma
        if os.path.exists(MARCA["logo_path"]):
            st.image(MARCA["logo_path"], width=160)
        else:
            st.markdown(f"### {MARCA['nombre_firma']}")

        st.markdown("---")

        # Tabs: Iniciar sesión / Crear cuenta
        tab_login, tab_registro = st.tabs(["Iniciar sesión", "Solicitar acceso"])

        with tab_login:
            authenticator.login(location="main")
            estado_auth = st.session_state.get("authentication_status")
            if estado_auth is False:
                st.error("Usuario o contraseña incorrectos.")

        with tab_registro:
            st.markdown('<div class="registro-card">', unsafe_allow_html=True)
            st.markdown("**Solicita acceso al portal**")
            st.caption("Tu asesor revisará tu solicitud y te notificará por email cuando esté activa.")

            with st.form("form_registro", clear_on_submit=True):
                nombre_reg   = st.text_input("Nombre completo",  placeholder="Carlos Mendoza")
                username_reg = st.text_input("Usuario",          placeholder="carlos_mendoza  (sin espacios ni acentos)")
                email_reg    = st.text_input("Email",            placeholder="carlos@email.com")
                pass_reg     = st.text_input("Contraseña",       type="password",
                                             help="Mínimo 8 caracteres, una mayúscula y un número.")
                pass_reg2    = st.text_input("Confirmar contraseña", type="password")
                enviado      = st.form_submit_button("Enviar solicitud", use_container_width=True, type="primary")

            if enviado:
                if pass_reg != pass_reg2:
                    st.error("Las contraseñas no coinciden.")
                else:
                    ok, msg = registro.registrar_usuario(
                        nombre_reg, username_reg, email_reg, pass_reg
                    )
                    if ok:
                        st.success("✅ Solicitud enviada. Tu asesor te contactará cuando tu cuenta esté activa.")
                    else:
                        st.error(msg)

            st.markdown('</div>', unsafe_allow_html=True)

    # Detener aquí si no está autenticado
    estado_auth = st.session_state.get("authentication_status")
    if not estado_auth:
        st.stop()

# ─── A partir de aquí el usuario está autenticado ───────────────────────────

nombre   = st.session_state.get("name")
username = st.session_state.get("username")

# ─────────────────────────────────────────────
#  SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    if os.path.exists(MARCA["logo_path"]):
        st.image(MARCA["logo_path"], width=140)
    else:
        st.markdown(f'<p class="firma-nombre">{MARCA["nombre_firma"]}</p>', unsafe_allow_html=True)
    st.markdown('<p class="firma-sub">Portal de inversiones</p>', unsafe_allow_html=True)
    st.markdown("---")

    ASESOR_USERNAME = "marioeaj"
    st.write(f"DEBUG username: '{username}' | ASESOR: '{ASESOR_USERNAME}'")
    archivo_cliente = f"{username}.xlsx"
    if username == ASESOR_USERNAME:
        st.info("Bienvenido al portal de administración.")
        st.markdown("Accede al **panel de administración** desde el menú de la izquierda.")
        st.stop()

    if not os.path.exists(archivo_cliente):
     st.error(f"No se encontró {archivo_cliente}")
     st.info("El asesor debe subir el Excel del portafolio.")
     authenticator.logout("Cerrar sesión", "sidebar")
     st.stop()

    st.caption(f"Sesión: {nombre}")
    st.caption(f"Actualizado: {datetime.now().strftime('%d/%m/%Y')}")
    st.markdown("---")
    authenticator.logout("Cerrar sesión", "sidebar")

# ─────────────────────────────────────────────
#  CARGA DE DATOS
# ─────────────────────────────────────────────
@st.cache_data(ttl=300)
def cargar_datos(archivo):
    xl = pd.ExcelFile(archivo)
    datos = {}
    datos["cliente"]    = pd.read_excel(xl, sheet_name="cliente",   index_col=0, header=None).squeeze("columns")
    datos["posiciones"] = pd.read_excel(xl, sheet_name="posiciones")
    datos["historial"]  = pd.read_excel(xl, sheet_name="historial", parse_dates=["fecha"])
    datos["historial"].sort_values("fecha", inplace=True)
    datos["flujos"]     = pd.read_excel(xl, sheet_name="flujos",    parse_dates=["fecha"])
    return datos


def calcular_metricas(historial, posiciones):
    valor_actual  = historial["valor_portafolio"].iloc[-1]
    valor_inicial = historial["valor_portafolio"].iloc[0]
    inicio_anio   = historial[historial["fecha"].dt.year == datetime.now().year]
    ytd = (valor_actual / inicio_anio["valor_portafolio"].iloc[0] - 1) * 100 if not inicio_anio.empty else 0
    bench_ytd = None
    if "benchmark" in historial.columns and not inicio_anio.empty:
        bench_ytd = (historial["benchmark"].iloc[-1] / inicio_anio["benchmark"].iloc[0] - 1) * 100
    retornos    = historial["valor_portafolio"].pct_change().dropna()
    volatilidad = retornos.std() * np.sqrt(252) * 100 if len(retornos) > 5 else 0
    retorno_anual = (valor_actual / valor_inicial) ** (252 / max(len(historial), 1)) - 1
    sharpe = (retorno_anual - 0.10) / (volatilidad / 100) if volatilidad > 0 else 0
    var_dia = (historial["valor_portafolio"].iloc[-1] / historial["valor_portafolio"].iloc[-2] - 1) * 100 \
              if len(historial) >= 2 else 0
    return {
        "valor_actual":   valor_actual,
        "ganancia_total": valor_actual - valor_inicial,
        "ytd":            ytd,
        "bench_ytd":      bench_ytd,
        "volatilidad":    volatilidad,
        "sharpe":         sharpe,
        "var_dia":        var_dia,
    }


try:
    datos = cargar_datos(archivo_cliente)
except Exception as e:
    st.error(f"Error al leer el portafolio: {e}")
    st.stop()

cliente    = datos["cliente"]
posiciones = datos["posiciones"]
historial  = datos["historial"]
flujos     = datos["flujos"]
metricas   = calcular_metricas(historial, posiciones)

# ─────────────────────────────────────────────
#  ENCABEZADO
# ─────────────────────────────────────────────
col_titulo, col_perfil = st.columns([3, 1])
with col_titulo:
    st.markdown(f"## Bienvenido, {nombre.split()[0]}")
    st.caption(f"Portafolio al {historial['fecha'].iloc[-1].strftime('%d de %B, %Y')}")
with col_perfil:
    st.markdown(f"**Perfil:** {cliente.get('perfil', 'Moderado')}")
    st.markdown(f"**Asesor:** {cliente.get('asesor', MARCA['nombre_firma'])}")

st.divider()

# ─────────────────────────────────────────────
#  MÉTRICAS
# ─────────────────────────────────────────────
m = metricas
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.metric("Valor total",       f"${m['valor_actual']:,.0f}", f"{m['var_dia']:+.2f}% hoy")
with c2:
    bench_str = f"benchmark {m['bench_ytd']:+.1f}%" if m["bench_ytd"] else None
    st.metric("Rendimiento YTD",   f"{m['ytd']:+.1f}%", bench_str)
with c3:
    st.metric("Ganancia acumulada", f"${m['ganancia_total']:+,.0f}")
with c4:
    st.metric("Volatilidad anual", f"{m['volatilidad']:.1f}%", f"Sharpe {m['sharpe']:.2f}", delta_color="off")

st.divider()

# ─────────────────────────────────────────────
#  GRÁFICAS
# ─────────────────────────────────────────────
col_linea, col_dona = st.columns([3, 2])

with col_linea:
    st.markdown("#### Rendimiento histórico")
    periodo  = st.radio("", ["1M","3M","6M","1A","Todo"], horizontal=True, index=2, label_visibility="collapsed")
    dias_map = {"1M":30,"3M":90,"6M":180,"1A":365,"Todo":99999}
    hist_fil = historial[historial["fecha"] >= historial["fecha"].max() - pd.Timedelta(days=dias_map[periodo])]

    fig_linea = go.Figure()
    fig_linea.add_trace(go.Scatter(
        x=hist_fil["fecha"], y=hist_fil["valor_portafolio"],
        name="Portafolio", line=dict(color=COLORES["azul"], width=2),
        fill="tozeroy", fillcolor="rgba(24,95,165,0.07)"
    ))
    if "benchmark" in hist_fil.columns:
        factor = hist_fil["valor_portafolio"].iloc[0] / hist_fil["benchmark"].iloc[0]
        fig_linea.add_trace(go.Scatter(
            x=hist_fil["fecha"], y=hist_fil["benchmark"] * factor,
            name="Benchmark", line=dict(color=COLORES["gris"], width=1.5, dash="dot")
        ))
    fig_linea.update_layout(
        height=260, margin=dict(l=0,r=0,t=10,b=0),
        legend=dict(orientation="h", y=-0.15),
        xaxis=dict(showgrid=False),
        yaxis=dict(gridcolor="rgba(150,150,150,0.1)"),
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)"
    )
    st.plotly_chart(fig_linea, use_container_width=True)

with col_dona:
    st.markdown("#### Asignación de activos")
    if "clase" in posiciones.columns and "valor_actual" in posiciones.columns:
        asig = posiciones.groupby("clase")["valor_actual"].sum().reset_index()
        fig_dona = go.Figure(go.Pie(
            labels=asig["clase"], values=asig["valor_actual"], hole=0.62,
            marker_colors=[COLORES["azul"], COLORES["verde"], COLORES["ambar"], COLORES["gris"], COLORES["morado"]][:len(asig)],
            textinfo="label+percent", textfont_size=12,
        ))
        fig_dona.update_layout(
            height=260, margin=dict(l=0,r=0,t=10,b=0), showlegend=False,
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)"
        )
        st.plotly_chart(fig_dona, use_container_width=True)

st.divider()

# ─────────────────────────────────────────────
#  TABLA DE POSICIONES
# ─────────────────────────────────────────────
st.markdown("#### Posiciones principales")
cols = [c for c in ["nombre","clase","valor_actual","peso_pct","rendimiento_ytd_pct","ganancia_perdida"] if c in posiciones.columns]
if cols:
    df_tabla = posiciones[cols].copy()
    df_tabla.rename(columns={
        "nombre":"Activo","clase":"Clase","valor_actual":"Valor",
        "peso_pct":"Peso %","rendimiento_ytd_pct":"Rend. YTD %","ganancia_perdida":"G / P"
    }, inplace=True)
    if "Valor"       in df_tabla.columns: df_tabla["Valor"]       = df_tabla["Valor"].apply(lambda x: f"${x:,.0f}")
    if "Peso %"      in df_tabla.columns: df_tabla["Peso %"]      = df_tabla["Peso %"].apply(lambda x: f"{x:.1f}%")
    if "Rend. YTD %" in df_tabla.columns: df_tabla["Rend. YTD %"] = df_tabla["Rend. YTD %"].apply(lambda x: f"{x:+.1f}%")
    if "G / P"       in df_tabla.columns: df_tabla["G / P"]       = df_tabla["G / P"].apply(lambda x: f"${x:+,.0f}")
    st.dataframe(df_tabla, use_container_width=True, hide_index=True)

# ─────────────────────────────────────────────
#  CORRELACIONES
# ─────────────────────────────────────────────
cols_ret = [c for c in posiciones.columns if c.startswith("ret_")]
if len(cols_ret) >= 2:
    st.divider()
    st.markdown("#### Correlaciones entre activos")
    st.caption("Verde = diversifica bien · Rojo = alta correlación")
    matriz = posiciones[cols_ret].T.corr()
    matriz.index   = posiciones["nombre"].tolist()
    matriz.columns = posiciones["nombre"].tolist()
    fig_heat = go.Figure(go.Heatmap(
        z=matriz.values, x=matriz.columns.tolist(), y=matriz.index.tolist(),
        colorscale=[[0, COLORES["verde"]], [0.5, "#f5f5f0"], [1, COLORES["rojo"]]],
        zmin=-1, zmax=1,
        text=matriz.values.round(2), texttemplate="%{text}", textfont_size=11,
    ))
    fig_heat.update_layout(
        height=360, margin=dict(l=0,r=0,t=10,b=0),
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)"
    )
    st.plotly_chart(fig_heat, use_container_width=True)

# ─────────────────────────────────────────────
#  BOTÓN DE SOLICITUD DE REVISIÓN
# ─────────────────────────────────────────────
st.divider()
st.markdown("""
<div class="revision-card">
  <h4 style="margin:0 0 6px;">¿Tienes preguntas sobre tu portafolio?</h4>
  <p style="margin:0; color:#555; font-size:14px;">
    Tu asesor puede agendar una llamada de revisión contigo.
  </p>
</div>
""", unsafe_allow_html=True)

motivo   = st.text_area("Describe brevemente tu consulta (opcional)",
                         placeholder="Ej: Quiero revisar si debo rebalancear...", height=90)
col_btn, col_estado = st.columns([2, 3])
with col_btn:
    solicitar = st.button("Solicitar revisión con mi asesor", type="primary", use_container_width=True)

if solicitar:
    EMAIL_ASESOR = os.environ.get("EMAIL_ASESOR", "malcaraz@maravillamx.com")
    EMAIL_ORIGEN = os.environ.get("EMAIL_ORIGEN", "malcaraz@maravillamx.com")
    EMAIL_PASS   = os.environ.get("EMAIL_PASS",   "MarioEAJ_Am10")
    if EMAIL_ASESOR and EMAIL_ORIGEN and EMAIL_PASS:
        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = f"Solicitud de revisión — {nombre}"
            msg["From"]    = EMAIL_ORIGEN
            msg["To"]      = EMAIL_ASESOR
            cuerpo = f"""
            <h3>Nueva solicitud de revisión</h3>
            <p><b>Cliente:</b> {nombre} ({username})</p>
            <p><b>Fecha:</b> {datetime.now().strftime('%d/%m/%Y %H:%M')}</p>
            <p><b>Valor del portafolio:</b> ${m['valor_actual']:,.0f}</p>
            <p><b>Rendimiento YTD:</b> {m['ytd']:+.1f}%</p>
            <hr><p><b>Motivo:</b> {motivo or '(Sin motivo especificado)'}</p>
            """
            msg.attach(MIMEText(cuerpo, "html"))
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                server.login(EMAIL_ORIGEN, EMAIL_PASS)
                server.sendmail(EMAIL_ORIGEN, EMAIL_ASESOR, msg.as_string())
            with col_estado:
                st.success("Solicitud enviada. Tu asesor te contactará pronto.")
        except Exception:
            with col_estado:
                st.info("Solicitud registrada. Tu asesor te contactará.")
    else:
        with col_estado:
            st.info("Solicitud registrada. Tu asesor te contactará.")

st.divider()
st.caption(f"{MARCA['nombre_firma']} · Portal privado de inversiones · Información confidencial.")
