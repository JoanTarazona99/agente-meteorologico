# Copilot Instructions — Agente Meteorológico

## Stack

- **Python 3.13.9** · Flask 2.3.3 · SQLAlchemy 2.0.36 · Flask-SQLAlchemy 3.1.1
- **Flask-Babel 4.0.0** (Babel 2.18.0) — locale basado en sesión (`session['lang']`)
- **Open-Meteo API** — sin API key, sin registro
- **SQLite** — `weather_dev.db` (dev), `:memory:` (tests)
- **Frontend** — HTML5, Bootstrap 5 (CDN), Chart.js (CDN), JS vanilla

## Estructura clave

```
app/__init__.py   → Factory create_app(), init Babel con get_locale()
app/routes.py     → Blueprint principal (HTML + API REST)
app/models.py     → ORM: Ciudad, RegistroClima, ConfigAlerta, HistorialAlerta
app/services.py   → Cliente Open-Meteo (geocoding + weather), mapas WMO bilingües
app/alerts.py     → Motor de evaluación de alertas con lazy_gettext
config.py         → DevelopmentConfig / TestingConfig / ProductionConfig
```

## Convenciones de código

- **Idioma del código**: español (nombres de variables, funciones, comentarios, docstrings).
- **i18n en templates**: usar `_('cadena')` para toda cadena visible al usuario.
- **i18n en Python**: usar `lazy_gettext` (`_l`) para strings en nivel de módulo, `gettext` (`_`) dentro de funciones.
- **i18n en JavaScript**: usar `window.I18N.clave` (objeto inyectado por `base.html`).
- **Descripciones WMO**: mantener `_WMO_DESC_ES` y `_WMO_DESC_RU` sincronizados en `services.py`.
- **Blueprints**: toda ruta en `app/routes.py` vía `bp = Blueprint('main', __name__)`.
- **Factory pattern**: `create_app(config_class)` en `app/__init__.py`.
- **Tests**: pytest con fixtures en `tests/conftest.py`. No requieren servidor ni API real.

## Flujo de traducciones (pybabel)

```bash
# Extraer strings nuevos
venv\Scripts\pybabel.exe extract -F babel.cfg -k "_l" -o translations/messages.pot .

# Actualizar .po
venv\Scripts\pybabel.exe update -i translations/messages.pot -d translations

# Compilar .mo
venv\Scripts\pybabel.exe compile -d translations
```

## Tests

```bash
# Activar venv y correr suite completa
venv\Scripts\activate
pytest tests/unit/ tests/integration/ -v

# Con cobertura
pytest tests/unit/ tests/integration/ --cov=app --cov-report=html
```

- 59 tests: 17 unit services + 9 unit alerts + 9 unit models + 16 integration routes + 8 integration database.
- E2E Selenium opcional (`tests/e2e/`), requiere servidor corriendo + Chrome.

## Notas importantes

- `BABEL_TRANSLATION_DIRECTORIES` apunta a la carpeta `translations/` en la raíz del proyecto (no dentro de `app/`).
- `SQLAlchemy >= 2.0.36` es necesario para Python 3.13.
- La presión atmosférica (`presion`) es `Float`, no `Integer`.
- Open-Meteo: el pronóstico min/max se obtiene con `daily=temperature_2m_max,temperature_2m_min` en la misma llamada que `current`.
