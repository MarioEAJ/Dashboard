# Sistema de portafolios — Guía de inicio rápido

## Estructura de archivos

```
portafolio_app/
│
├── app.py                  ← Dashboard principal de Streamlit
├── generar_plantilla.py    ← Script para crear el Excel de ejemplo
├── requirements.txt        ← Dependencias de Python
│
├── cliente_mendoza.xlsx    ← Un Excel por cliente (tú los creas)
├── cliente_garza.xlsx
└── ...
```

---

## Paso 1 — Instalar Python (si no lo tienes)

Descarga Python 3.11 o superior desde: https://python.org/downloads
Durante la instalación marca "Add Python to PATH".

---

## Paso 2 — Instalar las dependencias

Abre la terminal (CMD en Windows, Terminal en Mac) en la carpeta del proyecto y ejecuta:

```bash
pip install streamlit plotly pandas openpyxl numpy
```

---

## Paso 3 — Generar la plantilla Excel de ejemplo

```bash
python generar_plantilla.py
```

Esto crea el archivo `cliente_ejemplo.xlsx` con datos simulados.
Ábrelo en Excel y reemplaza con los datos reales de tu cliente.

---

## Paso 4 — Correr el dashboard

```bash
streamlit run app.py
```

Se abrirá automáticamente en tu navegador en http://localhost:8501

---

## Estructura del Excel por cliente

Cada cliente tiene su propio archivo .xlsx con 4 hojas:

### Hoja: cliente
| campo             | valor              |
|-------------------|--------------------|
| nombre            | Carlos Mendoza     |
| perfil            | Moderado           |
| asesor            | Tu nombre          |
| objetivo          | Crecimiento        |
| horizonte_anios   | 5                  |
| fecha_inicio      | 2022-01-01         |

### Hoja: posiciones
Columnas requeridas:
- `nombre`              — Nombre del activo
- `clase`               — Renta Variable / Renta Fija / Alternativos / Efectivo
- `valor_actual`        — Valor en pesos
- `peso_pct`            — Porcentaje del portafolio (ej: 26.0)
- `rendimiento_ytd_pct` — Rendimiento YTD en % (ej: 15.2)
- `ganancia_perdida`    — Ganancia o pérdida en pesos

Columnas opcionales (para gráfica de sectores):
- `sector`              — Sector del activo (ej: Tecnología)

Columnas opcionales (para matriz de correlaciones):
- `ret_ene`, `ret_feb`, etc. — Retorno mensual de cada activo (ej: 0.032 = 3.2%)
  Nómbralas `ret_` + lo que quieras. Deben estar en todas las filas.

### Hoja: historial
| fecha      | valor_portafolio | benchmark |
|------------|-----------------|-----------|
| 2022-01-03 | 1615680         | 100.00    |
| 2022-01-04 | 1621340         | 100.32    |
| ...        | ...             | ...       |

- `fecha`             — Fecha (formato YYYY-MM-DD)
- `valor_portafolio`  — Valor total del portafolio ese día
- `benchmark`         — Índice de comparación (puede iniciar en 100)

### Hoja: flujos
| fecha      | tipo        | monto    | nota                  |
|------------|-------------|----------|-----------------------|
| 2022-01-15 | Aportación  | 500000   | Apertura de cuenta    |
| 2023-03-10 | Retiro      | -80000   | Retiro parcial        |

- Montos positivos = aportaciones
- Montos negativos = retiros

---

## Agregar un nuevo cliente

1. Duplica el archivo `cliente_ejemplo.xlsx`
2. Renómbralo (ej: `cliente_garza.xlsx`)
3. Edita las 4 hojas con los datos del nuevo cliente
4. Al abrir el dashboard verás ambos en el selector de la barra lateral

---

## Próximos pasos (Fases 2 y 3)

- **Fase 2:** Subir a Railway para acceso web con login por cliente
- **Fase 3:** Integrar Claude API para briefings automáticos

---

## Soporte

Si algo no funciona, el error más común es un nombre de columna
incorrecto en el Excel. Verifica que los nombres coincidan exactamente
con los de esta guía (minúsculas, sin acentos, con guión bajo).
