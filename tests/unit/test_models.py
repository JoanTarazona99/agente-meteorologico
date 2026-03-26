"""Pruebas unitarias para app/models.py"""
import pytest
from datetime import datetime


class TestModeloCiudad:
    """Pruebas para el modelo Ciudad."""

    def test_crear_ciudad(self, app):
        """Verifica que se puede crear una ciudad correctamente."""
        with app.app_context():
            from app.models import Ciudad
            from app import db

            ciudad = Ciudad(nombre='Barcelona', pais='ES', latitud=41.3874, longitud=2.1686)
            db.session.add(ciudad)
            db.session.commit()

            assert ciudad.id is not None
            assert ciudad.nombre == 'Barcelona'
            assert ciudad.pais == 'ES'

    def test_ciudad_to_dict(self, app):
        """Verifica que to_dict retorna el formato correcto."""
        with app.app_context():
            from app.models import Ciudad
            from app import db

            ciudad = Ciudad(nombre='Sevilla', pais='ES', latitud=37.3891, longitud=-5.9845)
            db.session.add(ciudad)
            db.session.commit()

            d = ciudad.to_dict()
            assert d['nombre'] == 'Sevilla'
            assert d['pais'] == 'ES'
            assert 'id' in d
            assert 'creado_en' in d

    def test_ciudad_repr(self, app):
        """Verifica la representación string del modelo."""
        with app.app_context():
            ciudad = __import__('app.models', fromlist=['Ciudad']).Ciudad(nombre='Valencia', pais='ES')
            assert 'Valencia' in repr(ciudad)


class TestModeloRegistroClima:
    """Pruebas para el modelo RegistroClima."""

    def test_crear_registro_clima(self, app, ciudad_ejemplo):
        """Verifica que se puede crear un registro de clima."""
        with app.app_context():
            from app.models import RegistroClima
            from app import db

            ciudad = db.session.merge(ciudad_ejemplo)
            registro = RegistroClima(
                ciudad_id=ciudad.id,
                temperatura=25.0,
                humedad=70,
                presion=1015,
                descripcion='nublado',
                velocidad_viento=8.0
            )
            db.session.add(registro)
            db.session.commit()

            assert registro.id is not None
            assert registro.temperatura == 25.0

    def test_registro_clima_to_dict(self, app, ciudad_ejemplo):
        """Verifica que to_dict incluye todos los campos esperados."""
        with app.app_context():
            from app.models import RegistroClima
            from app import db

            ciudad = db.session.merge(ciudad_ejemplo)
            registro = RegistroClima(ciudad_id=ciudad.id, temperatura=20.0)
            db.session.add(registro)
            db.session.commit()

            d = registro.to_dict()
            campos = ['id', 'ciudad_id', 'temperatura', 'humedad', 'presion',
                      'velocidad_viento', 'descripcion', 'registrado_en']
            for campo in campos:
                assert campo in d


class TestModeloConfigAlerta:
    """Pruebas para el modelo ConfigAlerta."""

    def test_alerta_activa_por_defecto(self, app, ciudad_ejemplo):
        """Verifica que las alertas se crean activas por defecto."""
        with app.app_context():
            from app.models import ConfigAlerta
            from app import db

            ciudad = db.session.merge(ciudad_ejemplo)
            config = ConfigAlerta(ciudad_id=ciudad.id, tipo='temp_max', umbral=35.0)
            db.session.add(config)
            db.session.commit()

            assert config.activa is True

    def test_config_alerta_to_dict(self, app, ciudad_ejemplo):
        """Verifica el formato de to_dict para ConfigAlerta."""
        with app.app_context():
            from app.models import ConfigAlerta
            from app import db

            ciudad = db.session.merge(ciudad_ejemplo)
            config = ConfigAlerta(ciudad_id=ciudad.id, tipo='humedad', umbral=90.0)
            db.session.add(config)
            db.session.commit()

            d = config.to_dict()
            assert d['tipo'] == 'humedad'
            assert d['umbral'] == 90.0
            assert d['activa'] is True


class TestModeloHistorialAlerta:
    """Pruebas para el modelo HistorialAlerta."""

    def test_crear_historial_alerta(self, app, ciudad_ejemplo):
        """Verifica que se puede crear un historial de alerta."""
        with app.app_context():
            from app.models import HistorialAlerta
            from app import db

            ciudad = db.session.merge(ciudad_ejemplo)
            historial = HistorialAlerta(
                ciudad_id=ciudad.id,
                tipo='viento',
                mensaje='Viento muy fuerte',
                valor_actual=25.0,
                umbral=20.0
            )
            db.session.add(historial)
            db.session.commit()

            assert historial.id is not None
            assert historial.leida is False

    def test_historial_alerta_to_dict(self, app, ciudad_ejemplo):
        """Verifica el formato de to_dict para HistorialAlerta."""
        with app.app_context():
            from app.models import HistorialAlerta
            from app import db

            ciudad = db.session.merge(ciudad_ejemplo)
            historial = HistorialAlerta(
                ciudad_id=ciudad.id, tipo='temp_min',
                mensaje='Frío extremo', valor_actual=-5.0, umbral=0.0
            )
            db.session.add(historial)
            db.session.commit()

            d = historial.to_dict()
            assert 'mensaje' in d
            assert 'disparado_en' in d
            assert d['leida'] is False
