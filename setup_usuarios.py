"""
setup_usuarios.py — Compatible con streamlit-authenticator >= 0.4.0
Genera config.yaml con contraseñas hasheadas usando bcrypt.

    python setup_usuarios.py
"""
import yaml
import bcrypt

# ─────────────────────────────────────────────────────────────────────────────
#  TU CUENTA DE ASESOR  ← agrega tu usuario aquí primero
# ─────────────────────────────────────────────────────────────────────────────
ASESOR = {
    "username": "MarioEAJ",          # ← este debe coincidir con ASESOR_USERNAME en tus secrets
    "name":     "Mario Alcaraz",       # ← tu nombre completo
    "email":    "malcaraz@maravillamx.com",    # ← tu email
    "password": "MarioEAJ_Am10", # ← tu contraseña (cámbiala)
}

# ─────────────────────────────────────────────────────────────────────────────
#  CLIENTES  ← agrega cada cliente aquí
# ─────────────────────────────────────────────────────────────────────────────
CLIENTES = [
    {
        "username": "carlos_mendoza",
        "name":     "Carlos Mendoza",
        "email":    "carlos@ejemplo.com",
        "password": "CMendoza2024!",
    },
    # Agrega más clientes aquí
]

# ─────────────────────────────────────────────────────────────────────────────
#  NO MODIFIQUES DEBAJO DE ESTA LÍNEA
# ─────────────────────────────────────────────────────────────────────────────

def hashear(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

# Combinar asesor + clientes en un solo diccionario
todos = [ASESOR] + CLIENTES

credentials = {"usernames": {}}
for u in todos:
    credentials["usernames"][u["username"]] = {
        "name":     u["name"],
        "email":    u["email"],
        "password": hashear(u["password"]),
    }

config = {
    "credentials": credentials,
    "cookie": {
        "name":         "portafolio_session",
        "key":          "clave_secreta_cambia_esto_32chars",  # ← cambia por cadena aleatoria
        "expiry_days":  30,
    },
}

with open("config.yaml", "w") as f:
    yaml.dump(config, f, default_flow_style=False, allow_unicode=True)

print("✅ config.yaml generado correctamente.")
print(f"\n   Asesor:   {ASESOR['username']}")
print(f"   Clientes: {len(CLIENTES)}")
for c in CLIENTES:
    print(f"   · {c['username']}  →  {c['username']}.xlsx")
print(f"\n⚠️  El username del asesor '{ASESOR['username']}' debe coincidir")
print(f"    con la variable ASESOR_USERNAME en tu archivo .env o Streamlit secrets.")
