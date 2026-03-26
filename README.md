# 🌤️ Agente Meteorológico

Agente meteorológico completo con dashboard interactivo, histórico en SQLite, sistema de alertas configurables y soporte bilingüe (Español / Ruso).

Consulta datos reales en tiempo real vía **Open-Meteo** (gratuita, sin registro, sin API key).

---

## Características

- **Dashboard** — Clima actual, pronóstico 7 días, gráfica histórica con Chart.js
- **Ciudades** — Búsqueda por nombre, guardado automático, eliminación
- **Alertas** — Configuración de umbrales (temp max/min, viento, humedad) con notificaciones
- **Histórico** — Registros almacenados en SQLite, consultables por ciudad
- **Bilingüe** — Interfaz completa en Español (ES) y Ruso (RU)

---

## Requisitos

- Python 3.13+
- pip

---

## Instalación

```bash
# Clonar o copiar el proyecto
cd "agente meteorologico"

# Crear y activar entorno virtual
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux/Mac

# Instalar dependencias
pip install -r requirements.txt

# Crear archivo .env
copy .env.example .env       # Windows
# cp .env.example .env       # Linux/Mac

# Arrancar el servidor
python run.py
```

Abrir **http://localhost:5000** en el navegador.

---

## Cambiar idioma

Desde la navbar se puede alternar entre **ES** (Español) y **RU** (Ruso). El cambio es inmediato y se guarda en la sesión.

---

## Tests

```bash
# Instalar dependencias de testing
pip install -r requirements-dev.txt

# Correr toda la suite (59 tests)
pytest tests/unit/ tests/integration/ -v

# Con reporte de cobertura
pytest tests/unit/ tests/integration/ --cov=app --cov-report=html
```

---

## Stack tecnológico

| Capa | Tecnología |
|---|---|
| Backend | Python 3.13 + Flask 2.3.3 |
| BD | SQLAlchemy 2.0.36 + SQLite |
| i18n | Flask-Babel 4.0.0 |
| API Clima | Open-Meteo (sin API key) |
| Frontend | Bootstrap 5 + Chart.js + JS vanilla |
| Testing | pytest (59 tests) |

---

## Licencia

Proyecto educativo / personal.
