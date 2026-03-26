"""Pruebas unitarias para app/services.py (Open-Meteo API)"""
import pytest
from unittest.mock import patch, MagicMock, call


class TestServicioClimaParser:
    """Pruebas para el parsing de respuestas de Open-Meteo."""

    def test_parsear_clima_actual_campos_principales(self, app, respuesta_api_mock):
        """Verifica que _parsear_clima_actual extrae todos los campos correctamente."""
        with app.app_context():
            from app.services import ServicioClima
            servicio = ServicioClima.__new__(ServicioClima)
            resultado = servicio._parsear_clima_actual(
                respuesta_api_mock, 'Madrid', 'ES', 40.4168, -3.7038
            )

            assert resultado['ciudad'] == 'Madrid'
            assert resultado['pais'] == 'ES'
            assert resultado['temperatura'] == 22.5
            assert resultado['humedad'] == 65
            assert resultado['presion'] == 1013.0
            assert resultado['velocidad_viento'] == 5.5

    def test_parsear_clima_actual_descripcion_wmo(self, app, respuesta_api_mock):
        """Verifica que el código WMO se convierte a descripción correcta."""
        with app.app_context():
            from app.services import ServicioClima
            servicio = ServicioClima.__new__(ServicioClima)
            # weather_code=0 → 'cielo despejado', icono='sun'
            resultado = servicio._parsear_clima_actual(
                respuesta_api_mock, 'Madrid', 'ES', 40.4168, -3.7038
            )

            assert resultado['descripcion'] == 'cielo despejado'
            assert resultado['icono'] == 'sun'

    def test_parsear_clima_actual_coordenadas(self, app, respuesta_api_mock):
        """Verifica que las coordenadas se asignan correctamente."""
        with app.app_context():
            from app.services import ServicioClima
            servicio = ServicioClima.__new__(ServicioClima)
            resultado = servicio._parsear_clima_actual(
                respuesta_api_mock, 'Madrid', 'ES', 40.4168, -3.7038
            )

            assert resultado['latitud'] == 40.4168
            assert resultado['longitud'] == -3.7038

    def test_parsear_clima_respuesta_vacia(self, app):
        """Verifica que el parser maneja respuestas vacías sin error."""
        with app.app_context():
            from app.services import ServicioClima
            servicio = ServicioClima.__new__(ServicioClima)
            resultado = servicio._parsear_clima_actual({}, '', '', None, None)

            assert resultado['ciudad'] == ''
            assert resultado['temperatura'] is None

    def test_parsear_pronostico_estructura(self, app, respuesta_pronostico_mock):
        """Verifica la estructura del pronóstico diario parseado."""
        with app.app_context():
            from app.services import ServicioClima
            servicio = ServicioClima.__new__(ServicioClima)
            resultado = servicio._parsear_pronostico(respuesta_pronostico_mock, 'Madrid', 'ES')

            assert resultado['ciudad'] == 'Madrid'
            assert resultado['pais'] == 'ES'
            assert len(resultado['pronostico']) == 3
            assert resultado['pronostico'][0]['fecha'] == '2026-03-18'
            assert resultado['pronostico'][0]['temp_max'] == 25.0
            assert resultado['pronostico'][0]['temp_min'] == 14.0

    def test_parsear_pronostico_descripcion_wmo(self, app, respuesta_pronostico_mock):
        """Verifica que los códigos WMO del pronóstico se traducen correctamente."""
        with app.app_context():
            from app.services import ServicioClima
            servicio = ServicioClima.__new__(ServicioClima)
            resultado = servicio._parsear_pronostico(respuesta_pronostico_mock, 'Madrid', 'ES')

            # Día 0: code=0 → cielo despejado
            assert resultado['pronostico'][0]['descripcion'] == 'cielo despejado'
            # Día 2: code=61 → lluvia ligera
            assert resultado['pronostico'][2]['descripcion'] == 'lluvia ligera'


class TestWMOHelpers:
    """Pruebas para las funciones de mapeo de códigos WMO."""

    def test_wmo_desc_conocido(self, app):
        """Los códigos WMO conocidos retornan su descripción."""
        with app.app_context():
            from app.services import _wmo_desc
            assert _wmo_desc(0) == 'cielo despejado'
            assert _wmo_desc(61) == 'lluvia ligera'
            assert _wmo_desc(95) == 'tormenta'

    def test_wmo_desc_desconocido(self, app):
        """Los códigos WMO desconocidos retornan string con el código."""
        with app.app_context():
            from app.services import _wmo_desc
            resultado = _wmo_desc(999)
            assert '999' in resultado

    def test_wmo_icono_conocido(self, app):
        """Los códigos WMO conocidos retornan su icono Bootstrap."""
        with app.app_context():
            from app.services import _wmo_icono
            assert _wmo_icono(0) == 'sun'
            assert _wmo_icono(95) == 'cloud-lightning'

    def test_wmo_icono_desconocido(self, app):
        """Los códigos desconocidos retornan 'cloud' por defecto."""
        with app.app_context():
            from app.services import _wmo_icono
            assert _wmo_icono(999) == 'cloud'


class TestServicioClimaAPI:
    """Pruebas de las llamadas HTTP con mocks."""

    def test_geocodificar_retorna_coordenadas(self, app, respuesta_geo_mock):
        """Verifica que geocodificar retorna lat, lon, nombre, pais."""
        with app.app_context():
            from app.services import ServicioClima
            with patch('app.services.requests.get') as mock_get:
                mock_resp = MagicMock()
                mock_resp.json.return_value = respuesta_geo_mock
                mock_resp.raise_for_status = MagicMock()
                mock_get.return_value = mock_resp

                servicio = ServicioClima.__new__(ServicioClima)
                lat, lon, nombre, pais = servicio.geocodificar('Madrid')

                assert lat == 40.4168
                assert lon == -3.7038
                assert nombre == 'Madrid'
                assert pais == 'ES'

    def test_geocodificar_ciudad_no_encontrada(self, app):
        """Verifica que lanza ValueError si la ciudad no existe en la API."""
        with app.app_context():
            from app.services import ServicioClima
            with patch('app.services.requests.get') as mock_get:
                mock_resp = MagicMock()
                mock_resp.json.return_value = {'results': []}
                mock_resp.raise_for_status = MagicMock()
                mock_get.return_value = mock_resp

                servicio = ServicioClima.__new__(ServicioClima)
                with pytest.raises(ValueError):
                    servicio.geocodificar('CiudadInexistente')

    def test_obtener_clima_actual_llama_geo_y_weather(self, app, respuesta_geo_mock, respuesta_api_mock):
        """Verifica que obtener_clima_actual hace 2 llamadas: geocoding + weather."""
        with app.app_context():
            from app.services import ServicioClima
            respuestas = [MagicMock(), MagicMock()]
            respuestas[0].json.return_value = respuesta_geo_mock
            respuestas[0].raise_for_status = MagicMock()
            respuestas[1].json.return_value = respuesta_api_mock
            respuestas[1].raise_for_status = MagicMock()

            with patch('app.services.requests.get', side_effect=respuestas) as mock_get:
                servicio = ServicioClima.__new__(ServicioClima)
                resultado = servicio.obtener_clima_actual('Madrid')

                assert mock_get.call_count == 2
                assert resultado['ciudad'] == 'Madrid'
                assert resultado['temperatura'] == 22.5

    def test_obtener_pronostico_llama_geo_y_daily(self, app, respuesta_geo_mock, respuesta_pronostico_mock):
        """Verifica que obtener_pronostico hace 2 llamadas HTTP."""
        with app.app_context():
            from app.services import ServicioClima
            respuestas = [MagicMock(), MagicMock()]
            respuestas[0].json.return_value = respuesta_geo_mock
            respuestas[0].raise_for_status = MagicMock()
            respuestas[1].json.return_value = respuesta_pronostico_mock
            respuestas[1].raise_for_status = MagicMock()

            with patch('app.services.requests.get', side_effect=respuestas) as mock_get:
                servicio = ServicioClima.__new__(ServicioClima)
                resultado = servicio.obtener_pronostico('Madrid')

                assert mock_get.call_count == 2
                assert len(resultado['pronostico']) == 3

    def test_guardar_registro_persiste_en_bd(self, app, ciudad_ejemplo, datos_clima_mock):
        """Verifica que guardar_registro crea un RegistroClima en la BD."""
        with app.app_context():
            from app.services import ServicioClima
            from app.models import RegistroClima
            from app import db

            ciudad = db.session.merge(ciudad_ejemplo)
            servicio = ServicioClima.__new__(ServicioClima)
            registro = servicio.guardar_registro(ciudad.id, datos_clima_mock)

            assert registro.id is not None
            assert registro.temperatura == 22.5
            assert registro.humedad == 65

    def test_obtener_o_crear_ciudad_nueva(self, app, datos_clima_mock):
        """Verifica que se crea una nueva ciudad si no existe."""
        with app.app_context():
            from app.services import ServicioClima
            from app.models import Ciudad
            from app import db

            Ciudad.query.filter_by(nombre='TestCiudad', pais='TC').delete()
            db.session.commit()

            datos_clima_mock['ciudad'] = 'TestCiudad'
            datos_clima_mock['pais'] = 'TC'

            servicio = ServicioClima.__new__(ServicioClima)
            ciudad, es_nueva = servicio.obtener_o_crear_ciudad(datos_clima_mock)

            assert ciudad.id is not None
            assert ciudad.nombre == 'TestCiudad'
            assert es_nueva is True

    def test_obtener_o_crear_ciudad_existente(self, app, ciudad_ejemplo):
        """Verifica que no se duplica una ciudad que ya existe."""
        with app.app_context():
            from app.services import ServicioClima
            from app import db

            ciudad_bd = db.session.merge(ciudad_ejemplo)
            datos = {'ciudad': ciudad_bd.nombre, 'pais': ciudad_bd.pais, 'latitud': None, 'longitud': None}

            servicio = ServicioClima.__new__(ServicioClima)
            ciudad1, es_nueva_1 = servicio.obtener_o_crear_ciudad(datos)
            ciudad2, es_nueva_2 = servicio.obtener_o_crear_ciudad(datos)

            assert ciudad1.id == ciudad2.id
            # Primera llamada: ciudad existe (por fixture), así que es_nueva=False
            assert es_nueva_1 is False
            # Segunda llamada: sigue siendo False (idempotencia)
            assert es_nueva_2 is False
    def test_generar_historico_inicial_crea_siete_registros(self, app, datos_clima_mock):
        """Verifica que generar_historico_inicial crea 7 registros con variaciones."""
        with app.app_context():
            from app.services import ServicioClima
            from app.models import Ciudad, RegistroClima
            from app import db

            # Crear una ciudad
            ciudad = Ciudad(nombre='TestCity', pais='TC', latitud=0, longitud=0)
            db.session.add(ciudad)
            db.session.commit()

            # Generar histórico
            servicio = ServicioClima.__new__(ServicioClima)
            servicio.generar_historico_inicial(ciudad.id, datos_clima_mock)

            # Verificar que se crearon 7 registros
            registros = RegistroClima.query.filter_by(ciudad_id=ciudad.id).all()
            assert len(registros) == 7

            # Verificar que tienen temperaturas variadas
            temperatures = [r.temperatura for r in registros]
            assert len(set(temperatures)) > 1  # Debe haber variación de temperaturas

            # Verificar que todos tienen timestamps en el pasado cercano
            from datetime import datetime, timedelta
            ahora = datetime.utcnow()
            for registro in registros:
                tiempo_pasado = ahora - registro.registrado_en
                # Debe estar en los últimos ~350 horas (7 días + algunos minutos)
                assert tiempo_pasado < timedelta(hours=400)
                assert tiempo_pasado > timedelta(hours=0)
