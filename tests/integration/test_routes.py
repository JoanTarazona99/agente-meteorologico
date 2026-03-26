"""Pruebas de integración para las rutas de app/routes.py"""
import pytest
import json
from unittest.mock import patch, MagicMock


class TestRutaIndex:
    """Pruebas para la ruta principal /"""

    def test_index_retorna_200(self, client):
        """Verifica que el dashboard carga correctamente."""
        respuesta = client.get('/')
        assert respuesta.status_code == 200

    def test_index_contiene_html(self, client):
        """Verifica que la respuesta contiene HTML válido."""
        respuesta = client.get('/')
        assert b'<!DOCTYPE html>' in respuesta.data or b'Dashboard' in respuesta.data


class TestRutaAlertas:
    """Pruebas para la ruta /alertas"""

    def test_alertas_retorna_200(self, client):
        """Verifica que la página de alertas carga correctamente."""
        respuesta = client.get('/alertas')
        assert respuesta.status_code == 200


class TestApiClimaActual:
    """Pruebas para el endpoint GET /api/clima/actual"""

    def test_sin_parametro_ciudad_retorna_400(self, client):
        """Sin parámetro ciudad debe retornar 400."""
        respuesta = client.get('/api/clima/actual')
        assert respuesta.status_code == 400
        datos = json.loads(respuesta.data)
        assert 'error' in datos

    def test_con_ciudad_valida_retorna_200(self, client, respuesta_geo_mock, respuesta_api_mock):
        """Con una ciudad válida (mock) retorna 200 con datos del clima."""
        respuestas = [MagicMock(), MagicMock()]
        respuestas[0].json.return_value = respuesta_geo_mock
        respuestas[0].raise_for_status = MagicMock()
        respuestas[1].json.return_value = respuesta_api_mock
        respuestas[1].raise_for_status = MagicMock()

        with patch('app.services.requests.get', side_effect=respuestas):
            respuesta = client.get('/api/clima/actual?ciudad=Madrid')
            assert respuesta.status_code == 200
            datos = json.loads(respuesta.data)
            assert datos['status'] == 'ok'
            assert 'clima' in datos

    def test_respuesta_incluye_datos_clima(self, client, respuesta_geo_mock, respuesta_api_mock):
        """Verifica que la respuesta incluye los campos clave del clima."""
        respuestas = [MagicMock(), MagicMock()]
        respuestas[0].json.return_value = respuesta_geo_mock
        respuestas[0].raise_for_status = MagicMock()
        respuestas[1].json.return_value = respuesta_api_mock
        respuestas[1].raise_for_status = MagicMock()

        with patch('app.services.requests.get', side_effect=respuestas):
            respuesta = client.get('/api/clima/actual?ciudad=Madrid')
            datos = json.loads(respuesta.data)

            clima = datos['clima']
            assert clima['ciudad'] == 'Madrid'
            assert clima['temperatura'] == 22.5
            assert clima['humedad'] == 65


class TestApiPronostico:
    """Pruebas para el endpoint GET /api/clima/pronostico"""

    def test_sin_parametro_retorna_400(self, client):
        """Sin parámetro ciudad debe retornar 400."""
        respuesta = client.get('/api/clima/pronostico')
        assert respuesta.status_code == 400

    def test_con_ciudad_retorna_200(self, client, respuesta_geo_mock, respuesta_pronostico_mock):
        """Con ciudad válida retorna 200."""
        respuestas = [MagicMock(), MagicMock()]
        respuestas[0].json.return_value = respuesta_geo_mock
        respuestas[0].raise_for_status = MagicMock()
        respuestas[1].json.return_value = respuesta_pronostico_mock
        respuestas[1].raise_for_status = MagicMock()

        with patch('app.services.requests.get', side_effect=respuestas):
            respuesta = client.get('/api/clima/pronostico?ciudad=Madrid')
            assert respuesta.status_code == 200


class TestApiHistorico:
    """Pruebas para el endpoint GET /api/historico"""

    def test_historico_retorna_200(self, client):
        """El endpoint de histórico retorna 200."""
        respuesta = client.get('/api/historico')
        assert respuesta.status_code == 200

    def test_historico_retorna_lista(self, client):
        """El histórico retorna una lista de registros."""
        respuesta = client.get('/api/historico')
        datos = json.loads(respuesta.data)
        assert datos['status'] == 'ok'
        assert isinstance(datos['registros'], list)


class TestApiCiudades:
    """Pruebas para los endpoints de ciudades."""

    def test_listar_ciudades_retorna_200(self, client):
        """Listar ciudades retorna 200."""
        respuesta = client.get('/api/ciudades')
        assert respuesta.status_code == 200

    def test_eliminar_ciudad_inexistente_retorna_404(self, client):
        """Eliminar una ciudad que no existe retorna 404."""
        respuesta = client.delete('/api/ciudades/99999')
        assert respuesta.status_code == 404


class TestApiAlertas:
    """Pruebas para los endpoints de alertas."""

    def test_obtener_alertas_retorna_200(self, client):
        """Obtener alertas retorna 200."""
        respuesta = client.get('/api/alertas')
        assert respuesta.status_code == 200

    def test_crear_alerta_sin_json_retorna_error(self, client):
        """Crear alerta sin JSON retorna 400 o 415 (Unsupported Media Type)."""
        respuesta = client.post('/api/alertas', data='no es json',
                                content_type='text/plain')
        assert respuesta.status_code in (400, 415)

    def test_crear_alerta_campos_faltantes_retorna_400(self, client):
        """Crear alerta con campos faltantes retorna 400."""
        respuesta = client.post('/api/alertas',
                                data=json.dumps({'ciudad_id': 1}),
                                content_type='application/json')
        assert respuesta.status_code == 400

    def test_crear_alerta_tipo_invalido_retorna_400(self, client, respuesta_api_mock):
        """Crear alerta con tipo inválido retorna 400."""
        with patch('app.services.requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.json.return_value = respuesta_api_mock
            mock_response.raise_for_status = MagicMock()
            mock_get.return_value = mock_response

            # Primero crear una ciudad
            client.get('/api/clima/actual?ciudad=Madrid')

            respuesta = client.post('/api/alertas',
                                    data=json.dumps({'ciudad_id': 1, 'tipo': 'invalido', 'umbral': 30}),
                                    content_type='application/json')
            assert respuesta.status_code == 400
