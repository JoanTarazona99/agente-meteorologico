import pytest
from app import create_app, db as _db
from app.models import Ciudad, RegistroClima, ConfigAlerta, HistorialAlerta
from faker import Faker

fake = Faker('es_ES')


@pytest.fixture(scope='session')
def app():
    """Crea la aplicación Flask en modo testing (BD en memoria)."""
    application = create_app('testing')
    yield application


@pytest.fixture(scope='session')
def db(app):
    """Crea todas las tablas al inicio de la sesión de pruebas."""
    with app.app_context():
        _db.create_all()
        yield _db
        _db.drop_all()


@pytest.fixture(scope='function')
def db_session(db, app):
    """Provee una sesión de BD limpia por cada test (con rollback automático)."""
    with app.app_context():
        connection = db.engine.connect()
        transaction = connection.begin()
        yield db.session
        db.session.remove()
        transaction.rollback()
        connection.close()


@pytest.fixture(scope='function')
def client(app, db):
    """Cliente de pruebas Flask."""
    with app.app_context():
        _db.create_all()
        yield app.test_client()
        _db.session.remove()
        _db.drop_all()
        _db.create_all()


@pytest.fixture
def ciudad_ejemplo(db, app):
    """Crea una ciudad de ejemplo en la BD."""
    with app.app_context():
        ciudad = Ciudad(
            nombre='Madrid',
            pais='ES',
            latitud=40.4168,
            longitud=-3.7038
        )
        _db.session.add(ciudad)
        _db.session.commit()
        return ciudad


@pytest.fixture
def datos_clima_mock():
    """Retorna datos de clima simulados de Open-Meteo (sin API key)."""
    return {
        'ciudad': 'Madrid',
        'pais': 'ES',
        'latitud': 40.4168,
        'longitud': -3.7038,
        'temperatura': 22.5,
        'sensacion_termica': 21.0,
        'temp_min': None,
        'temp_max': None,
        'humedad': 65,
        'presion': 1013.0,
        'velocidad_viento': 5.5,
        'direccion_viento': 180,
        'descripcion': 'cielo despejado',
        'icono': 'sun',
        'nubosidad': 5,
        'visibilidad': 10000.0,
        'precipitacion': 0.0,
        'timestamp': '2026-03-18T12:00',
    }


@pytest.fixture
def respuesta_geo_mock():
    """Simula la respuesta del endpoint de geocodificación de Open-Meteo."""
    return {
        'results': [{
            'name': 'Madrid',
            'latitude': 40.4168,
            'longitude': -3.7038,
            'country_code': 'ES',
            'country': 'España',
        }]
    }


@pytest.fixture
def respuesta_api_mock():
    """Simula la respuesta JSON del endpoint /v1/forecast de Open-Meteo."""
    return {
        'current': {
            'time': '2026-03-18T12:00',
            'temperature_2m': 22.5,
            'relative_humidity_2m': 65,
            'apparent_temperature': 21.0,
            'precipitation': 0.0,
            'weather_code': 0,
            'surface_pressure': 1013.0,
            'wind_speed_10m': 5.5,
            'wind_direction_10m': 180,
            'cloud_cover': 5,
            'visibility': 10000.0,
        },
        'latitude': 40.4168,
        'longitude': -3.7038,
        'timezone': 'Europe/Madrid',
    }


@pytest.fixture
def respuesta_pronostico_mock():
    """Simula la respuesta de pronóstico diario de Open-Meteo."""
    return {
        'daily': {
            'time': ['2026-03-18', '2026-03-19', '2026-03-20'],
            'weather_code': [0, 2, 61],
            'temperature_2m_max': [25.0, 22.0, 18.0],
            'temperature_2m_min': [14.0, 12.0, 10.0],
            'precipitation_sum': [0.0, 0.5, 8.0],
            'wind_speed_10m_max': [10.0, 15.0, 20.0],
        },
        'latitude': 40.4168,
        'longitude': -3.7038,
        'timezone': 'Europe/Madrid',
    }
