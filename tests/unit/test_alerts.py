"""Pruebas unitarias para app/alerts.py"""
import pytest
from app.models import ConfigAlerta, HistorialAlerta


class TestSistemaAlertasEvaluacion:
    """Pruebas para la evaluación de condiciones de alerta."""

    def test_alerta_temp_max_se_dispara(self, app, ciudad_ejemplo):
        """Alerta de temperatura máxima se dispara cuando se supera el umbral."""
        with app.app_context():
            from app.alerts import SistemaAlertas
            from app import db

            ciudad = db.session.merge(ciudad_ejemplo)
            config = ConfigAlerta(ciudad_id=ciudad.id, tipo='temp_max', umbral=30.0, activa=True)
            db.session.add(config)
            db.session.commit()

            sistema = SistemaAlertas()
            datos = {'temperatura': 22.0, 'temp_max': 35.0, 'temp_min': 18.0, 'humedad': 60, 'velocidad_viento': 5.0}
            alertas = sistema.evaluar_alertas(ciudad.id, datos)

            assert len(alertas) >= 1
            assert any(a.tipo == 'temp_max' for a in alertas)

    def test_alerta_temp_max_no_se_dispara(self, app, ciudad_ejemplo):
        """Alerta de temperatura máxima NO se dispara cuando está por debajo del umbral."""
        with app.app_context():
            from app.alerts import SistemaAlertas
            from app import db

            ciudad = db.session.merge(ciudad_ejemplo)
            config = ConfigAlerta(ciudad_id=ciudad.id, tipo='temp_max', umbral=40.0, activa=True)
            db.session.add(config)
            db.session.commit()

            sistema = SistemaAlertas()
            datos = {'temperatura': 22.0, 'temp_max': 28.0, 'temp_min': 18.0, 'humedad': 60, 'velocidad_viento': 5.0}
            alertas = sistema.evaluar_alertas(ciudad.id, datos)

            assert all(a.tipo != 'temp_max' for a in alertas)

    def test_alerta_temp_min_se_dispara(self, app, ciudad_ejemplo):
        """Alerta de temperatura mínima se dispara cuando baja del umbral."""
        with app.app_context():
            from app.alerts import SistemaAlertas
            from app import db

            ciudad = db.session.merge(ciudad_ejemplo)
            config = ConfigAlerta(ciudad_id=ciudad.id, tipo='temp_min', umbral=10.0, activa=True)
            db.session.add(config)
            db.session.commit()

            sistema = SistemaAlertas()
            datos = {'temperatura': 7.0, 'temp_max': 15.0, 'temp_min': 5.0, 'humedad': 80, 'velocidad_viento': 10.0}
            alertas = sistema.evaluar_alertas(ciudad.id, datos)

            assert any(a.tipo == 'temp_min' for a in alertas)

    def test_alerta_viento_se_dispara(self, app, ciudad_ejemplo):
        """Alerta de viento se dispara cuando supera el umbral."""
        with app.app_context():
            from app.alerts import SistemaAlertas
            from app import db

            ciudad = db.session.merge(ciudad_ejemplo)
            config = ConfigAlerta(ciudad_id=ciudad.id, tipo='viento', umbral=15.0, activa=True)
            db.session.add(config)
            db.session.commit()

            sistema = SistemaAlertas()
            datos = {'temperatura': 20.0, 'temp_max': 25.0, 'temp_min': 15.0, 'humedad': 70, 'velocidad_viento': 20.0}
            alertas = sistema.evaluar_alertas(ciudad.id, datos)

            assert any(a.tipo == 'viento' for a in alertas)

    def test_alerta_inactiva_no_se_evalua(self, app, ciudad_ejemplo):
        """Las alertas desactivadas no se evalúan."""
        with app.app_context():
            from app.alerts import SistemaAlertas
            from app import db

            ciudad = db.session.merge(ciudad_ejemplo)

            # Eliminar configs activas para esta ciudad primero
            ConfigAlerta.query.filter_by(ciudad_id=ciudad.id, activa=True).delete()
            db.session.commit()

            config = ConfigAlerta(ciudad_id=ciudad.id, tipo='temp_max', umbral=0.0, activa=False)
            db.session.add(config)
            db.session.commit()

            sistema = SistemaAlertas()
            datos = {'temperatura': 50.0, 'temp_max': 99.0, 'temp_min': 30.0, 'humedad': 100, 'velocidad_viento': 100.0}
            alertas = sistema.evaluar_alertas(ciudad.id, datos)

            assert len(alertas) == 0


class TestSistemaAlertasCRUD:
    """Pruebas para crear, desactivar y leer alertas."""

    def test_crear_alerta_valida(self, app, ciudad_ejemplo):
        """Verifica que se puede crear una alerta con tipo válido."""
        with app.app_context():
            from app.alerts import SistemaAlertas
            from app import db

            ciudad = db.session.merge(ciudad_ejemplo)
            sistema = SistemaAlertas()
            config = sistema.crear_alerta(ciudad.id, 'viento', 20.0)

            assert config.id is not None
            assert config.tipo == 'viento'
            assert config.umbral == 20.0
            assert config.activa is True

    def test_crear_alerta_tipo_invalido(self, app, ciudad_ejemplo):
        """Verifica que se lanza ValueError con tipo de alerta inválido."""
        with app.app_context():
            from app.alerts import SistemaAlertas
            from app import db

            ciudad = db.session.merge(ciudad_ejemplo)
            sistema = SistemaAlertas()

            with pytest.raises(ValueError):
                sistema.crear_alerta(ciudad.id, 'tipo_inexistente', 10.0)

    def test_marcar_alerta_leida(self, app, ciudad_ejemplo):
        """Verifica que se puede marcar una alerta del historial como leída."""
        with app.app_context():
            from app.alerts import SistemaAlertas
            from app import db

            ciudad = db.session.merge(ciudad_ejemplo)
            historial = HistorialAlerta(
                ciudad_id=ciudad.id,
                tipo='temp_max',
                mensaje='Temperatura alta',
                valor_actual=40.0,
                umbral=35.0,
                leida=False
            )
            db.session.add(historial)
            db.session.commit()

            sistema = SistemaAlertas()
            resultado = sistema.marcar_leida(historial.id)

            assert resultado.leida is True

    def test_obtener_alertas_no_leidas(self, app, ciudad_ejemplo):
        """Verifica que se retornan solo las alertas no leídas."""
        with app.app_context():
            from app.alerts import SistemaAlertas
            from app import db

            ciudad = db.session.merge(ciudad_ejemplo)

            leida = HistorialAlerta(ciudad_id=ciudad.id, tipo='temp_max', mensaje='Leída', leida=True, umbral=30, valor_actual=35)
            no_leida = HistorialAlerta(ciudad_id=ciudad.id, tipo='viento', mensaje='Sin leer', leida=False, umbral=15, valor_actual=20)
            db.session.add_all([leida, no_leida])
            db.session.commit()

            sistema = SistemaAlertas()
            alertas = sistema.obtener_alertas_no_leidas(ciudad.id)

            assert all(not a.leida for a in alertas)
            assert any(a.tipo == 'viento' for a in alertas)
