# Fase 2 — Guía de deploy en Streamlit Community Cloud

## Qué cambia respecto a la Fase 1

| Fase 1 | Fase 2 |
|--------|--------|
| Solo tú lo ves en tu computadora | El cliente accede desde su navegador |
| Sin login | Login por cliente con contraseña |
| Sin branding | Colores y logo de tu firma |
| Sin notificaciones | Botón que te manda email cuando solicita revisión |

---

## Paso 1 — Preparar el entorno local

```bash
pip install streamlit streamlit-authenticator plotly pandas openpyxl numpy pyyaml bcrypt
```

---

## Paso 2 — Configurar tu marca

Abre `app.py` y edita el bloque MARCA al inicio del archivo:

```python
MARCA = {
    "nombre_firma":   "Tu Firma de Inversiones",   # nombre real de tu firma
    "color_primario": "#185FA5",                    # color principal en HEX
    "color_acento":   "#1D9E75",                    # color secundario en HEX
    "logo_path":      "logo.png",                   # pon tu logo PNG en la misma carpeta
}
```

También edita `.streamlit/config.toml` para cambiar `primaryColor` al mismo valor.

---

## Paso 3 — Crear los usuarios de tus clientes

Abre `setup_usuarios.py` y agrega cada cliente:

```python
CLIENTES = [
    {
        "username": "carlos_mendoza",   # sin espacios, sin acentos
        "name":     "Carlos Mendoza",
        "email":    "carlos@email.com",
        "password": "PasswordSegura1!", # mínimo 8 chars, mayúscula, número
    },
    # ... más clientes
]
```

Luego ejecuta:

```bash
python setup_usuarios.py
```

Esto genera `config.yaml` con las contraseñas hasheadas.

---

## Paso 4 — Nombrar los archivos Excel

El Excel de cada cliente DEBE llamarse igual que su `username`:

```
carlos_mendoza.xlsx   ← para username "carlos_mendoza"
patricia_garza.xlsx   ← para username "patricia_garza"
```

---

## Paso 5 — Subir a GitHub

1. Crea un repositorio **privado** en github.com (importante: privado)
2. Inicializa git en tu carpeta:

```bash
git init
git add app.py setup_usuarios.py requirements.txt .streamlit/ .gitignore
# NO agregues: config.yaml, *.xlsx, .env
git commit -m "Portal portafolios fase 2"
git remote add origin https://github.com/TU_USUARIO/TU_REPO.git
git push -u origin main
```

⚠️ Verifica que `.gitignore` está funcionando. Nunca subas config.yaml ni los Excel.

---

## Paso 6 — Deploy en Streamlit Community Cloud

1. Ve a https://share.streamlit.io
2. Inicia sesión con tu cuenta de GitHub
3. Clic en "New app"
4. Selecciona tu repositorio, rama `main`, archivo `app.py`
5. Clic en "Deploy"

La app estará disponible en:
`https://TU_USUARIO-TU_REPO-app-XXXXX.streamlit.app`

---

## Paso 7 — Subir archivos secretos (config.yaml y Excel)

Como NO subiste config.yaml ni los Excel a GitHub, debes subirlos
directamente en Streamlit Cloud:

1. En el dashboard de tu app, clic en los tres puntos → "Edit secrets"
2. Ahora bien — para los archivos Excel y config.yaml hay dos opciones:

### Opción A (recomendada para empezar): GitHub privado con Git LFS
Sube los archivos al repo pero usando Git LFS para archivos grandes.
Los Excel de clientes son archivos privados del repo privado.
Esto funciona porque el repo ya es privado.

```bash
# Quitar *.xlsx del .gitignore temporalmente, agregar los Excel y volver a proteger
git add carlos_mendoza.xlsx patricia_garza.xlsx config.yaml
git commit -m "datos clientes (repo privado)"
git push
```

### Opción B: Streamlit Secrets para config.yaml
En "Edit secrets" de Streamlit Cloud, pega el contenido de config.yaml:

```toml
[credentials.usernames.carlos_mendoza]
name = "Carlos Mendoza"
email = "carlos@email.com"
password = "$2b$12$HASH_GENERADO_POR_SETUP_USUARIOS"

[cookie]
name = "portafolio_session"
key = "tu_clave_secreta_aqui"
expiry_days = 30
```

---

## Paso 8 — Configurar notificaciones de email (opcional)

Para que el botón "Solicitar revisión" te mande un email real:

1. En Streamlit Cloud → "Edit secrets", agrega:

```toml
EMAIL_ASESOR = "tu@email.com"
EMAIL_ORIGEN = "tu@gmail.com"
EMAIL_PASS   = "tu_app_password_gmail"
```

2. Para obtener el App Password de Gmail:
   myaccount.google.com → Seguridad → Contraseñas de aplicaciones

---

## Resultado final

- URL única para todos tus clientes: `https://tu-app.streamlit.app`
- Cada cliente entra con su usuario y contraseña
- Solo ve su propio portafolio
- Cuando hace clic en "Solicitar revisión" te llega un email con su nombre,
  valor del portafolio y el motivo que escribió

---

## Actualizar datos de un cliente

Cuando actualices el Excel de un cliente:

```bash
git add carlos_mendoza.xlsx
git commit -m "actualizar portafolio Carlos - abril 2026"
git push
```

Streamlit Cloud detecta el cambio y actualiza automáticamente en segundos.
