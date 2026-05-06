"""
Ejecuta este script UNA SOLA VEZ para generar la plantilla Excel con datos de ejemplo.
Luego edita el archivo generado con los datos reales de tu cliente.

    python generar_plantilla.py
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

NOMBRE_ARCHIVO = "cliente_ejemplo.xlsx"

# ── Hoja 1: cliente ──────────────────────────────────────────────────────────
cliente = pd.DataFrame({
    "campo": [
        "nombre", "perfil", "asesor",
        "objetivo", "horizonte_anios", "fecha_inicio"
    ],
    "valor": [
        "Carlos Mendoza", "Moderado", "Tu nombre aquí",
        "Crecimiento patrimonial", 5, "2022-01-01"
    ]
}).set_index("campo")

# ── Hoja 2: posiciones ───────────────────────────────────────────────────────
posiciones = pd.DataFrame([
    {
        "nombre":               "MSCI World ETF",
        "clase":                "Renta Variable",
        "sector":               "Diversificado",
        "valor_actual":         480200,
        "peso_pct":             26.0,
        "rendimiento_ytd_pct":  15.2,
        "ganancia_perdida":     72400,
        # Columnas ret_* — retornos mensuales históricos para correlaciones
        # (agrega tantos meses como tengas; deben ser los mismos para todos los activos)
        "ret_ene": 0.032, "ret_feb": 0.018, "ret_mar": -0.012,
        "ret_abr": 0.024, "ret_may": 0.009, "ret_jun": -0.005,
    },
    {
        "nombre":               "Apple Inc.",
        "clase":                "Renta Variable",
        "sector":               "Tecnología",
        "valor_actual":         198300,
        "peso_pct":             10.7,
        "rendimiento_ytd_pct":  22.1,
        "ganancia_perdida":     43200,
        "ret_ene": 0.041, "ret_feb": 0.022, "ret_mar": -0.018,
        "ret_abr": 0.031, "ret_may": 0.014, "ret_jun": -0.003,
    },
    {
        "nombre":               "Bono Gov. MX 2030",
        "clase":                "Renta Fija",
        "sector":               "Gobierno MX",
        "valor_actual":         175000,
        "peso_pct":             9.5,
        "rendimiento_ytd_pct":  5.8,
        "ganancia_perdida":     9800,
        "ret_ene": 0.005, "ret_feb": 0.004, "ret_mar": 0.006,
        "ret_abr": 0.005, "ret_may": 0.005, "ret_jun": 0.004,
    },
    {
        "nombre":               "S&P 500 Index Fund",
        "clase":                "Renta Variable",
        "sector":               "Diversificado",
        "valor_actual":         163400,
        "peso_pct":             8.8,
        "rendimiento_ytd_pct":  13.4,
        "ganancia_perdida":     21600,
        "ret_ene": 0.029, "ret_feb": 0.016, "ret_mar": -0.011,
        "ret_abr": 0.022, "ret_may": 0.008, "ret_jun": -0.004,
    },
    {
        "nombre":               "CETES 182 días",
        "clase":                "Renta Fija",
        "sector":               "Gobierno MX",
        "valor_actual":         150000,
        "peso_pct":             8.1,
        "rendimiento_ytd_pct":  8.1,
        "ganancia_perdida":     5900,
        "ret_ene": 0.007, "ret_feb": 0.007, "ret_mar": 0.007,
        "ret_abr": 0.007, "ret_may": 0.007, "ret_jun": 0.007,
    },
    {
        "nombre":               "Gold ETC",
        "clase":                "Alternativos",
        "sector":               "Materias primas",
        "valor_actual":         132000,
        "peso_pct":             7.1,
        "rendimiento_ytd_pct":  18.3,
        "ganancia_perdida":     20400,
        "ret_ene": -0.010, "ret_feb": 0.025, "ret_mar": 0.018,
        "ret_abr": -0.008, "ret_may": 0.030, "ret_jun": 0.012,
    },
    {
        "nombre":               "Real Estate FIBRA",
        "clase":                "Alternativos",
        "sector":               "Bienes raíces",
        "valor_actual":         88000,
        "peso_pct":             4.8,
        "rendimiento_ytd_pct":  -2.1,
        "ganancia_perdida":     -3200,
        "ret_ene": -0.005, "ret_feb": -0.008, "ret_mar": 0.003,
        "ret_abr": -0.002, "ret_may": -0.006, "ret_jun": 0.001,
    },
    {
        "nombre":               "Efectivo / MMKT",
        "clase":                "Efectivo",
        "sector":               "Efectivo",
        "valor_actual":         148000,
        "peso_pct":             8.0,
        "rendimiento_ytd_pct":  6.9,
        "ganancia_perdida":     5100,
        "ret_ene": 0.006, "ret_feb": 0.006, "ret_mar": 0.006,
        "ret_abr": 0.006, "ret_may": 0.006, "ret_jun": 0.006,
    },
])

# ── Hoja 3: historial ────────────────────────────────────────────────────────
# Genera 24 meses de historial simulado con tendencia alcista y algo de ruido
np.random.seed(42)
fechas = pd.date_range(end=datetime.today(), periods=500, freq="B")  # días hábiles
valor_inicio = 1_615_680

retornos_diarios = np.random.normal(0.0004, 0.008, len(fechas))
valores = valor_inicio * np.cumprod(1 + retornos_diarios)

retornos_bench = np.random.normal(0.0003, 0.006, len(fechas))
benchmark = 100 * np.cumprod(1 + retornos_bench)

historial = pd.DataFrame({
    "fecha":             fechas,
    "valor_portafolio":  valores.round(0),
    "benchmark":         benchmark.round(2),
})

# ── Hoja 4: flujos ───────────────────────────────────────────────────────────
flujos = pd.DataFrame([
    {"fecha": "2022-01-15", "tipo": "Aportación",  "monto":  500000, "nota": "Apertura de cuenta"},
    {"fecha": "2022-06-01", "tipo": "Aportación",  "monto":  200000, "nota": "Aportación semestral"},
    {"fecha": "2022-12-15", "tipo": "Aportación",  "monto":  150000, "nota": "Aportación fin de año"},
    {"fecha": "2023-03-10", "tipo": "Retiro",       "monto": -80000,  "nota": "Retiro parcial"},
    {"fecha": "2023-09-01", "tipo": "Aportación",  "monto":  250000, "nota": "Aportación extraordinaria"},
    {"fecha": "2024-01-20", "tipo": "Aportación",  "monto":  300000, "nota": "Aportación anual"},
    {"fecha": "2024-07-15", "tipo": "Retiro",       "monto": -50000,  "nota": "Retiro vacaciones"},
    {"fecha": "2025-01-10", "tipo": "Aportación",  "monto":  200000, "nota": "Aportación anual"},
])
flujos["fecha"] = pd.to_datetime(flujos["fecha"])
flujos["monto"] = flujos["monto"].astype(float)

# ── Escribir Excel ───────────────────────────────────────────────────────────
with pd.ExcelWriter(NOMBRE_ARCHIVO, engine="openpyxl") as writer:
    cliente.to_excel(writer,    sheet_name="cliente",    header=False)
    posiciones.to_excel(writer, sheet_name="posiciones", index=False)
    historial.to_excel(writer,  sheet_name="historial",  index=False)
    flujos.to_excel(writer,     sheet_name="flujos",     index=False)

print(f"✅ Plantilla generada: {NOMBRE_ARCHIVO}")
print(f"   Hojas: cliente, posiciones, historial, flujos")
print(f"   Ahora puedes editarla con los datos reales de tu cliente.")
