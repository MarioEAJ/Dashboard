"""
registro.py — Módulo de auto-registro con aprobación del asesor.

Flujo:
  1. Cliente llena el formulario en la página de login
  2. Sus datos quedan en "pendientes" (pending_users.yaml)
  3. El asesor recibe un email de notificación
  4. El asesor aprueba desde su panel de administración
  5. El sistema mueve al usuario a config.yaml (activo)
  6. El cliente puede iniciar sesión

No requiere base de datos — todo se guarda en archivos YAML locales.
"""

import yaml
import bcrypt
import smtplib
import os
import re
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

PENDING_PATH = "pending_users.yaml"
CONFIG_PATH  = "config.yaml"


# ─────────────────────────────────────────────
#  UTILIDADES
# ─────────────────────────────────────────────

def _leer_yaml(path: str) -> dict:
    if not os.path.exists(path):
        return {}
    with open(path, "r") as f:
        return yaml.safe_load(f) or {}


def _escribir_yaml(path: str, data: dict):
    with open(path, "w") as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True)


def _hashear(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def _validar_email(email: str) -> bool:
    return bool(re.match(r"^[\w\.-]+@[\w\.-]+\.\w{2,}$", email))


def _validar_username(username: str) -> bool:
    """Solo letras, números y guión bajo. Sin espacios ni acentos."""
    return bool(re.match(r"^[a-z0-9_]{3,30}$", username))


def _validar_password(password: str) -> tuple[bool, str]:
    if len(password) < 8:
        return False, "Mínimo 8 caracteres."
    if not any(c.isupper() for c in password):
        return False, "Debe incluir al menos una mayúscula."
    if not any(c.isdigit() for c in password):
        return False, "Debe incluir al menos un número."
    return True, ""


def _username_existe(username: str) -> bool:
    """Verifica si el username ya existe en activos o pendientes."""
    config   = _leer_yaml(CONFIG_PATH)
    pending  = _leer_yaml(PENDING_PATH)
    activos  = config.get("credentials", {}).get("usernames", {})
    pendientes = pending.get("pendientes", {})
    return username in activos or username in pendientes


def _enviar_email_asesor(nombre_cliente: str, username: str, email_cliente: str):
    """Notifica al asesor que hay una solicitud de registro pendiente."""
    EMAIL_ASESOR = os.environ.get("EMAIL_ASESOR", "")
    EMAIL_ORIGEN = os.environ.get("EMAIL_ORIGEN", "")
    EMAIL_PASS   = os.environ.get("EMAIL_PASS",   "")

    if not all([EMAIL_ASESOR, EMAIL_ORIGEN, EMAIL_PASS]):
        return  # Sin credenciales configuradas, se omite silenciosamente

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"Nueva solicitud de acceso — {nombre_cliente}"
        msg["From"]    = EMAIL_ORIGEN
        msg["To"]      = EMAIL_ASESOR

        cuerpo = f"""
        <h3>Nueva solicitud de acceso al portal</h3>
        <table>
          <tr><td><b>Nombre:</b></td><td>{nombre_cliente}</td></tr>
          <tr><td><b>Usuario:</b></td><td>{username}</td></tr>
          <tr><td><b>Email:</b></td><td>{email_cliente}</td></tr>
          <tr><td><b>Fecha:</b></td><td>{datetime.now().strftime('%d/%m/%Y %H:%M')}</td></tr>
        </table>
        <br>
        <p>Ingresa al panel de administración para aprobar o rechazar esta solicitud.</p>
        """
        msg.attach(MIMEText(cuerpo, "html"))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL_ORIGEN, EMAIL_PASS)
            server.sendmail(EMAIL_ORIGEN, EMAIL_ASESOR, msg.as_string())
    except Exception:
        pass  # El registro se guarda aunque el email falle


def _enviar_email_cliente_aprobado(nombre: str, email: str, username: str, firma: str):
    """Notifica al cliente que su cuenta fue aprobada."""
    EMAIL_ORIGEN = os.environ.get("EMAIL_ORIGEN", "")
    EMAIL_PASS   = os.environ.get("EMAIL_PASS",   "")

    if not all([EMAIL_ORIGEN, EMAIL_PASS]):
        return

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"{firma} — Tu acceso al portal ha sido activado"
        msg["From"]    = EMAIL_ORIGEN
        msg["To"]      = email

        cuerpo = f"""
        <h3>Tu cuenta ha sido activada</h3>
        <p>Hola {nombre},</p>
        <p>Tu solicitud de acceso al portal de inversiones de <b>{firma}</b>
        ha sido aprobada. Ya puedes iniciar sesión con tu usuario <b>{username}</b>.</p>
        <p>Si tienes alguna duda, no dudes en contactar a tu asesor.</p>
        """
        msg.attach(MIMEText(cuerpo, "html"))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL_ORIGEN, EMAIL_PASS)
            server.sendmail(EMAIL_ORIGEN, email, msg.as_string())
    except Exception:
        pass


def _enviar_email_cliente_rechazado(nombre: str, email: str, firma: str):
    """Notifica al cliente que su solicitud fue rechazada."""
    EMAIL_ORIGEN = os.environ.get("EMAIL_ORIGEN", "")
    EMAIL_PASS   = os.environ.get("EMAIL_PASS",   "")

    if not all([EMAIL_ORIGEN, EMAIL_PASS]):
        return

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"{firma} — Solicitud de acceso no aprobada"
        msg["From"]    = EMAIL_ORIGEN
        msg["To"]      = email

        cuerpo = f"""
        <h3>Solicitud de acceso</h3>
        <p>Hola {nombre},</p>
        <p>Tu solicitud de acceso al portal de <b>{firma}</b> no pudo ser aprobada
        en este momento. Por favor contacta directamente a tu asesor para más información.</p>
        """
        msg.attach(MIMEText(cuerpo, "html"))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL_ORIGEN, EMAIL_PASS)
            server.sendmail(EMAIL_ORIGEN, email, msg.as_string())
    except Exception:
        pass


# ─────────────────────────────────────────────
#  API PÚBLICA
# ─────────────────────────────────────────────

def registrar_usuario(nombre: str, username: str, email: str, password: str) -> tuple[bool, str]:
    """
    Guarda un nuevo usuario en la lista de pendientes.
    Retorna (éxito, mensaje).
    """
    # Validaciones
    if not nombre.strip():
        return False, "El nombre no puede estar vacío."
    if not _validar_username(username):
        return False, "El usuario solo puede tener letras minúsculas, números y guión bajo (mín. 3 caracteres)."
    if not _validar_email(email):
        return False, "El email no tiene un formato válido."
    ok, msg = _validar_password(password)
    if not ok:
        return False, msg
    if _username_existe(username):
        return False, "Ese nombre de usuario ya está en uso. Elige otro."

    # Guardar en pendientes
    pending = _leer_yaml(PENDING_PATH)
    if "pendientes" not in pending:
        pending["pendientes"] = {}

    pending["pendientes"][username] = {
        "name":      nombre.strip(),
        "email":     email.strip().lower(),
        "password":  _hashear(password),
        "fecha":     datetime.now().strftime("%Y-%m-%d %H:%M"),
        "aprobado":  False,
    }
    _escribir_yaml(PENDING_PATH, pending)

    # Notificar al asesor
    _enviar_email_asesor(nombre, username, email)

    return True, "ok"


def obtener_pendientes() -> dict:
    """Retorna todos los usuarios pendientes de aprobación."""
    pending = _leer_yaml(PENDING_PATH)
    return pending.get("pendientes", {})


def aprobar_usuario(username: str, firma: str = "") -> bool:
    """
    Mueve al usuario de pendientes a config.yaml (activo).
    Retorna True si tuvo éxito.
    """
    pending = _leer_yaml(PENDING_PATH)
    pendientes = pending.get("pendientes", {})

    if username not in pendientes:
        return False

    usuario = pendientes[username]

    # Agregar a config.yaml
    config = _leer_yaml(CONFIG_PATH)
    if "credentials" not in config:
        config["credentials"] = {"usernames": {}}
    if "usernames" not in config["credentials"]:
        config["credentials"]["usernames"] = {}

    config["credentials"]["usernames"][username] = {
        "name":     usuario["name"],
        "email":    usuario["email"],
        "password": usuario["password"],
    }
    _escribir_yaml(CONFIG_PATH, config)

    # Eliminar de pendientes
    del pendientes[username]
    pending["pendientes"] = pendientes
    _escribir_yaml(PENDING_PATH, pending)

    # Notificar al cliente
    _enviar_email_cliente_aprobado(usuario["name"], usuario["email"], username, firma)

    return True


def rechazar_usuario(username: str, firma: str = "") -> bool:
    """
    Elimina al usuario de la lista de pendientes.
    Retorna True si tuvo éxito.
    """
    pending = _leer_yaml(PENDING_PATH)
    pendientes = pending.get("pendientes", {})

    if username not in pendientes:
        return False

    usuario = pendientes[username]

    # Notificar al cliente
    _enviar_email_cliente_rechazado(usuario["name"], usuario["email"], firma)

    # Eliminar de pendientes
    del pendientes[username]
    pending["pendientes"] = pendientes
    _escribir_yaml(PENDING_PATH, pending)

    return True
