"""Pruebas de integración para la base de datos."""
import pytest
from datetime import datetime


class TestPersistenciaCiudad:
    """Pruebas de persistencia para el modelo Ciudad."""

    def test_guardar_y_recuperar_ciudad(self, app):
        """Verifica que una ciudad se guarda y recupera correctamente."""
        with app.app_context():
            from app.models import Ciudad
            from app import db

            ciudad = Ciudad(nombre='Bilbao', pais='ES', latitud=43.263, longitud=-2.935)
            db.session.add(ciudad)
            db.session.commit()

            recuperada = Ciudad.query.filter_by(nombre='Bilbao', pais='ES').first()
            assert recuperada is not None
            assert recuperada.latitud == 43.263

    def test_relacion_ciudad_registros(self, app, ciudad_ejemplo):
        """Verifica la relación entre Ciudad y sus RegistroClima."""
        with app.app_context():
            from app.models import RegistroClima
            from app import db

            ciudad = db.session.merge(ciudad_ejemplo)
            r1 = RegistroClima(ciudad_id=ciudad.id, temperatura=20.0)
            r2 = RegistroClima(ciudad_id=ciudad.id, temperatura=22.0)
            db.session.add_all([r1, r2])
            db.session.commit()

            ciudad_bd = db.session.merge(ciudad)
            assert len(ciudad_bd.registros) >= 2

    def test_eliminar_ciudad_elimina_registros(self, app):
        """Al eliminar una ciudad, sus registros se eliminan en cascada."""
        with app.app_context():
            from app.models import Ciudad, RegistroClima
            from app import db

            ciudad = Ciudad(nombre='CiudadTemp', pais='TT')
            db.session.add(ciudad)
            db.session.commit()

            registro = RegistroClima(ciudad_id=ciudad.id, temperatura=18.0)
            db.session.add(registro)
            db.session.commit()

            ciudad_id = ciudad.id
            db.session.delete(ciudad)
            db.session.commit()

            registros = RegistroClima.query.filter_by(ciudad_id=ciudad_id).all()
            assert len(registros) == 0


class TestPersistenciaRegistroClima:
    """Pruebas de persistencia para RegistroClima."""

    def test_guardar_registro_con_todos_campos(self, app, ciudad_ejemplo):
        """Verifica que todos los campos de un registro se persisten."""
        with app.app_context():
            from app.models import RegistroClima
            from app import db

            ciudad = db.session.merge(ciudad_ejemplo)
            registro = RegistroClima(
                ciudad_id=ciudad.id,
                temperatura=23.5,
                sensacion_termica=22.0,
                temp_min=19.0,
                temp_max=27.0,
                humedad=72,
                presion=1012,
                velocidad_viento=6.3,
                direccion_viento=270,
                descripcion='parcialmente nublado',
                icono='02d',
                nubosidad=30,
                visibilidad=9000
            )
            db.session.add(registro)
            db.session.commit()

            r = RegistroClima.query.get(registro.id)
            assert r.temperatura == 23.5
            assert r.humedad == 72
            assert r.descripcion == 'parcialmente nublado'
            assert r.icono == '02d'

    def test_ordenar_registros_por_fecha(self, app, ciudad_ejemplo):
        """Verifica que los registros se pueden ordenar por fecha."""
        with app.app_context():
            from app.models import RegistroClima
            from app import db

            ciudad = db.session.merge(ciudad_ejemplo)
            for temp in [15.0, 20.0, 25.0]:
                db.session.add(RegistroClima(ciudad_id=ciudad.id, temperatura=temp))
            db.session.commit()

            registros = RegistroClima.query.filter_by(ciudad_id=ciudad.id) \
                .order_by(RegistroClima.registrado_en.desc()).all()
            assert len(registros) >= 3


class TestPersistenciaAlertas:
    """Pruebas de persistencia para configuración e historial de alertas."""

    def test_crear_y_listar_config_alertas(self, app, ciudad_ejemplo):
        """Verifica que se pueden crear y listar configuraciones de alerta."""
        with app.app_context():
            from app.models import ConfigAlerta
            from app import db

            ciudad = db.session.merge(ciudad_ejemplo)
            configs = [
                ConfigAlerta(ciudad_id=ciudad.id, tipo='temp_max', umbral=35.0),
                ConfigAlerta(ciudad_id=ciudad.id, tipo='viento', umbral=20.0),
            ]
            db.session.add_all(configs)
            db.session.commit()

            todas = ConfigAlerta.query.filter_by(ciudad_id=ciudad.id, activa=True).all()
            tipos = [c.tipo for c in todas]
            assert 'temp_max' in tipos
            assert 'viento' in tipos

    def test_desactivar_config_alerta(self, app, ciudad_ejemplo):
        """Verifica que una alerta se puede desactivar."""
        with app.app_context():
            from app.models import ConfigAlerta
            from app import db

            ciudad = db.session.merge(ciudad_ejemplo)
            config = ConfigAlerta(ciudad_id=ciudad.id, tipo='humedad', umbral=90.0, activa=True)
            db.session.add(config)
            db.session.commit()

            config.activa = False
            db.session.commit()

            c = ConfigAlerta.query.get(config.id)
            assert c.activa is False

    def test_historial_alertas_ordenado(self, app, ciudad_ejemplo):
        """Verifica que el historial de alertas se puede ordenar."""
        with app.app_context():
            from app.models import HistorialAlerta
            from app import db

            ciudad = db.session.merge(ciudad_ejemplo)
            for i in range(3):
                db.session.add(HistorialAlerta(
                    ciudad_id=ciudad.id, tipo='temp_max',
                    mensaje=f'Alerta {i}', valor_actual=30.0 + i, umbral=28.0
                ))
            db.session.commit()

            historial = HistorialAlerta.query.filter_by(ciudad_id=ciudad.id) \
                .order_by(HistorialAlerta.disparado_en.desc()).all()
            assert len(historial) >= 3
