# Agente Meteorológico — Documentación Técnica

## Resumen Ejecutivo

Agente meteorológico completo construido con Python y Flask. Consulta datos reales en tiempo real a través de la API **Open-Meteo** (gratuita, sin registro, sin API key). Incluye dashboard interactivo, histórico en SQLite, sistema de alertas configurables y suite completa de pruebas automatizadas.

| | |
|---|---|
| **Fecha de inicio** | 17 de marzo de 2026 |
| **Fecha de finalización** | 19 de marzo de 2026 |
| **Estado** | ✅ Completado |
| **Tests** | 59/59 pasando |
| **Idiomas** | Español (ES) + Ruso (RU) |
| **Entorno** | Windows, XAMPP, Python 3.13.9 |

---

## Stack Tecnológico

| Capa | Tecnología | Versión |
|---|---|---|
| Backend | Python + Flask | 3.13.9 / 2.3.3 |
| ORM / BD | SQLAlchemy + SQLite | 2.0.36 / Flask-SQLAlchemy 3.1.1 |
| Internacionalización | Flask-Babel + Babel | 4.0.0 / 2.18.0 |
| API Clima | Open-Meteo | Sin registro, sin API key |
| Frontend | HTML5 + Bootstrap 5 + JS vanilla | CDN |
| Iconos clima | Bootstrap Icons | CDN |
| Gráficos | Chart.js | CDN |
| Config | python-dotenv | 1.0.0 |
| HTTP client | requests | 2.31.0 |
| Testing | pytest + pytest-flask + pytest-cov | 7.4.3 / 1.3.0 / 4.1.0 |
| Datos de prueba | Faker | 19.13.0 |
| Pruebas E2E | Selenium + webdriver-manager | 4.15.2 / 4.0.1 |

---

## Estructura del Proyecto

```
agente meteorologico/
├── app/
│   ├── __init__.py          # Factory Flask, inicializa DB
│   ├── routes.py            # Blueprints: HTML + API REST
│   ├── models.py            # ORM: Ciudad, RegistroClima, ConfigAlerta, HistorialAlerta
│   ├── services.py          # Cliente Open-Meteo (geocoding + weather)
│   └── alerts.py            # Motor de evaluación de alertas
├── static/
│   ├── css/style.css        # Estilos personalizados
│   └── js/
│       ├── main.js          # Utilidades compartidas (apiFetch, formatTemp, iconoHtml…)
│       ├── dashboard.js     # Lógica del dashboard
│       └── alertas.js       # Lógica de la página de alertas
├── templates/
│   ├── base.html            # Layout base con navbar y footer
│   ├── dashboard.html       # Dashboard principal
│   └── alertas.html         # Gestión de alertas
├── tests/
│   ├── conftest.py          # Fixtures pytest (app, client, mocks Open-Meteo)
│   ├── unit/
│   │   ├── test_services.py # Tests del cliente Open-Meteo y parsers WMO
│   │   ├── test_alerts.py   # Tests del motor de alertas
│   │   └── test_models.py   # Tests de los modelos ORM
│   ├── integration/
│   │   ├── test_routes.py   # Tests de todos los endpoints HTTP
│   │   └── test_database.py # Tests de persistencia SQLite
│   └── e2e/
│       └── test_dashboard.py # Tests Selenium (requiere servidor corriendo)
├── config.py                # DevelopmentConfig, TestingConfig, ProductionConfig
├── babel.cfg                # Configuración pybabel (extractores python + jinja2)
├── translations/
│   ├── messages.pot         # Template de strings extraído por pybabel
│   └── ru/LC_MESSAGES/
│       ├── messages.po      # Traducciones al ruso (~60 cadenas)
│       └── messages.mo      # Compilado binario
├── .github/
│   └── copilot-instructions.md  # Instrucciones para GitHub Copilot
├── requirements.txt         # Dependencias de producción
├── requirements-dev.txt     # Dependencias de testing
├── run.py                   # Punto de entrada
├── pytest.ini               # Configuración pytest
├── .env.example             # Variables de entorno de ejemplo
├── .gitignore
├── README.md                # Documentación de usuario
└── agents.md                # Este archivo
```

---

## Funcionamiento de la API Open-Meteo

El cliente usa un flujo de **dos pasos** por búsqueda (sin API key):

```
1. GET https://geocoding-api.open-meteo.com/v1/search?name=<ciudad>
   → Retorna: latitud, longitud, nombre, country_code

2. GET https://api.open-meteo.com/v1/forecast
      ?latitude=<lat>&longitude=<lon>
      &current=temperature_2m,relative_humidity_2m,...
      &daily=temperature_2m_max,temperature_2m_min
   → Retorna: clima actual + min/max del día
```

Los **códigos WMO** que devuelve Open-Meteo se traducen internamente a:
- Descripciones en español (`_WMO_DESC_ES`) o ruso (`_WMO_DESC_RU`) según el locale activo
- Nombres de iconos Bootstrap Icons (`_WMO_ICONO`, ej. `'sun'`, `'cloud-rain'`)

---

## Modelos de Base de Datos

| Modelo | Tabla | Descripción |
|---|---|---|
| `Ciudad` | `ciudades` | Ciudades buscadas (nombre, país, lat, lon) |
| `RegistroClima` | `registros_clima` | Snapshot de clima por ciudad y timestamp |
| `ConfigAlerta` | `config_alertas` | Umbrales de alerta por ciudad y tipo |
| `HistorialAlerta` | `historial_alertas` | Alertas disparadas (leída/no leída) |

Tipos de alerta disponibles: `temp_max`, `temp_min`, `viento`, `humedad`.

---

## API REST — Endpoints

| Método | Ruta | Descripción |
|---|---|---|
| `GET` | `/set-lang/<lang>` | Cambiar idioma (ES/RU) — guarda en sesión |
| `GET` | `/` | Dashboard principal |
| `GET` | `/alertas` | Página de gestión de alertas |
| `GET` | `/api/clima/actual?ciudad=<nombre>` | Clima actual + guarda registro |
| `GET` | `/api/clima/pronostico?ciudad=<nombre>` | Pronóstico 7 días |
| `GET` | `/api/historico?ciudad_id=<id>&limite=<n>` | Registros históricos |
| `GET` | `/api/ciudades` | Lista de ciudades guardadas |
| `DELETE` | `/api/ciudades/<id>` | Eliminar ciudad y sus registros |
| `GET` | `/api/alertas?ciudad_id=<id>` | Alertas no leídas |
| `POST` | `/api/alertas` | Crear configuración de alerta |
| `POST` | `/api/alertas/<id>/desactivar` | Desactivar alerta |
| `POST` | `/api/alertas/<id>/leer` | Marcar alerta como leída |

---

## Instalación y Ejecución

```bash
# 1. Navegar al directorio
cd "c:\xampp\htdocs\proyectos\agente meteorologico"

# 2. Crear entorno virtual
python -m venv venv

# 3. Activar (Windows)
venv\Scripts\activate

# 4. Instalar dependencias
pip install -r requirements.txt -r requirements-dev.txt

# 5. Crear .env (sin API key necesaria)
copy .env.example .env

# 6. Arrancar servidor
python run.py
# → http://localhost:5000
```

`.env.example` mínimo:
```
SECRET_KEY=cambia-esto-en-produccion
FLASK_ENV=development
PORT=5000
```

---

## Internacionalización (ES / RU)

El soporte multiidioma usa **Flask-Babel 4.0.0** con locale basado en sesión.

### Arquitectura i18n

| Componente | Técnica |
|---|---|
| Templates Jinja2 | `_('cadena')` — traducción en tiempo de renderizado |
| Python (alertas) | `lazy_gettext()` — traducción diferida segura en módulos |
| JavaScript | `window.I18N` — objeto inyectado por Jinja2 en `base.html` |
| Descripciones WMO | `_WMO_DESC_ES` / `_WMO_DESC_RU` según `get_locale()` |
| Selector de locale | Sesión Flask (`session['lang']`) vía ruta `/set-lang/<lang>` |

### Flujo de cambio de idioma

```
Usuario pulsa ES/RU  →  GET /set-lang/ru  →  session['lang'] = 'ru'
→  get_locale() devuelve 'ru'  →  Babel carga translations/ru/LC_MESSAGES/messages.mo
→  _() traduce todas las cadenas  →  window.I18N contiene strings en ruso
```

### Gestión de traducciones

```bash
# Re-extraer strings tras añadir nuevas cadenas
venv\Scripts\pybabel.exe extract -F babel.cfg -k "_l" -o translations/messages.pot .

# Actualizar .po existente (conserva traducciones ya hechas)
venv\Scripts\pybabel.exe update -i translations/messages.pot -d translations

# Recompilar después de editar .po
venv\Scripts\pybabel.exe compile -d translations
```

---

## Pruebas Automatizadas

```bash
# Suite completa (unit + integración)
pytest tests/unit/ tests/integration/ -v

# Con cobertura
pytest tests/unit/ tests/integration/ --cov=app --cov-report=html
# Reporte en: htmlcov/index.html

# Solo unitarias
pytest tests/unit/ -v

# Solo integración
pytest tests/integration/ -v

# E2E Selenium (requiere: servidor corriendo en :5000 + Chrome)
pytest tests/e2e/ -v

# Ignorar E2E
pytest tests/ --ignore=tests/e2e/
```

**Resultado actual: 59/59 tests pasando.**

| Suite | Archivo | Tests |
|---|---|---|
| Unit | `test_services.py` | 17 |
| Unit | `test_alerts.py` | 9 |
| Unit | `test_models.py` | 9 |
| Integration | `test_routes.py` | 16 |
| Integration | `test_database.py` | 8 |
| **Total** | | **59** |

---

## Decisiones Técnicas

| Aspecto | Decisión | Razón |
|---|---|---|
| API clima | Open-Meteo | Gratuita, sin registro, 10 000 llamadas/día, datos desde 1940 |
| Iconos | Bootstrap Icons | Sin CDN externo adicional, ya incluido en Bootstrap |
| Min/Max día | `daily` en misma llamada HTTP | Evita una petición extra; Open-Meteo lo permite con `forecast_days=1` |
| Ciudades dinámicas | JS actualiza vía `/api/ciudades` | El contador y dropdowns se refrescan sin recargar la página |
| BD | SQLite | Sin servidor, cero configuración, adecuada para volumen de este proyecto |
| ORM | SQLAlchemy 2.0.36 | Versión compatible con Python 3.13 (2.0.21 no lo era) |
| Tests templates | `template_folder` explícito en `create_app()` | Flask resuelve rutas relativas al módulo, no a la raíz del proyecto |

---

## Decisiones Resueltas Durante el Desarrollo

| Problema | Solución |
|---|---|
| `SQLCoreOperations` en Python 3.13 | Actualizar `SQLAlchemy==2.0.21` → `2.0.36` |
| `TemplateNotFound` en tests | Pasar `template_folder` y `static_folder` absolutos en `create_app()` |
| Min/Max mostraba `null` | Añadir `daily=temperature_2m_max,temperature_2m_min` a la llamada `current` |
| Ciudades guardadas no se actualizaba | Función `actualizarCiudades()` en JS tras cada búsqueda |
| Gráfico vacío sin mensaje | `renderGrafica()` dibuja texto en canvas cuando no hay registros |
| `presion` tipo `Integer` incorrecto | Corregido a `Float` (Open-Meteo devuelve `1013.2`, no `1013`) |

---

## Estado Final del Proyecto

```
✅ Fase 1 — Estructura base y configuración
✅ Fase 2 — Backend: modelos, servicios, alertas, rutas
✅ Fase 3 — Frontend: dashboard, alertas, estilos, JS
✅ Fase 4 — Suite de tests (59/59)
✅ Fase 5 — Documentación y limpieza de código
✅ Migración OpenWeatherMap → Open-Meteo
✅ Limpieza profunda (sin código muerto)
✅ Bugs reportados corregidos (min/max, histórico, ciudades)
✅ Mejoras responsive (container-xxl, clamp(), row-cols)
✅ Soporte multiidioma ES + RU (Flask-Babel 4.0.0)
✅ Organización final: copilot-instructions.md, README.md, limpieza imports
```
```

