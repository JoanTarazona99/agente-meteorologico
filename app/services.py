import requests
from datetime import datetime
from app import db
from app.models import Ciudad, RegistroClima

# ─── URLs de Open-Meteo (sin API key, sin registro) ──────────────────────────
_GEO_URL = 'https://geocoding-api.open-meteo.com/v1/search'
_WEATHER_URL = 'https://api.open-meteo.com/v1/forecast'

# Parámetros actuales y diarios que pedimos en cada llamada
_CURRENT_PARAMS = (
    'temperature_2m,relative_humidity_2m,apparent_temperature,'
    'precipitation,weather_code,surface_pressure,'
    'wind_speed_10m,wind_direction_10m,cloud_cover,visibility'
)
_DAILY_PARAMS = (
    'weather_code,temperature_2m_max,temperature_2m_min,'
    'precipitation_sum,wind_speed_10m_max'
)

# Códigos WMO → descripción en español
_WMO_DESC_ES = {
    0: 'cielo despejado',
    1: 'principalmente despejado', 2: 'parcialmente nublado', 3: 'nublado',
    45: 'niebla', 48: 'niebla con escarcha',
    51: 'llovizna ligera', 53: 'llovizna moderada', 55: 'llovizna densa',
    61: 'lluvia ligera', 63: 'lluvia moderada', 65: 'lluvia intensa',
    71: 'nieve ligera', 73: 'nieve moderada', 75: 'nieve intensa',
    77: 'granizo fino',
    80: 'chubascos ligeros', 81: 'chubascos moderados', 82: 'chubascos intensos',
    85: 'chubascos de nieve ligeros', 86: 'chubascos de nieve intensos',
    95: 'tormenta', 96: 'tormenta con granizo', 99: 'tormenta con granizo intenso',
}

# Códigos WMO → descripción en ruso
_WMO_DESC_RU = {
    0: 'ясное небо',
    1: 'преимущественно ясно', 2: 'переменная облачность', 3: 'облачно',
    45: 'туман', 48: 'туман с инеем',
    51: 'морось слабая', 53: 'морось умеренная', 55: 'морось сильная',
    61: 'слабый дождь', 63: 'умеренный дождь', 65: 'сильный дождь',
    71: 'слабый снег', 73: 'умеренный снег', 75: 'сильный снег',
    77: 'снежная крупа',
    80: 'слабые ливни', 81: 'умеренные ливни', 82: 'сильные ливни',
    85: 'слабые снеговые ливни', 86: 'сильные снеговые ливни',
    95: 'гроза', 96: 'гроза с градом', 99: 'гроза с сильным градом',
}

# Códigos WMO → icono Bootstrap Icons
_WMO_ICONO = {
    0: 'sun', 1: 'sun', 2: 'cloud-sun', 3: 'clouds',
    45: 'cloud-fog', 48: 'cloud-fog',
    51: 'cloud-drizzle', 53: 'cloud-drizzle', 55: 'cloud-drizzle',
    61: 'cloud-rain', 63: 'cloud-rain', 65: 'cloud-rain-heavy',
    71: 'cloud-snow', 73: 'cloud-snow', 75: 'cloud-snow',
    77: 'cloud-hail', 80: 'cloud-rain', 81: 'cloud-rain', 82: 'cloud-rain-heavy',
    85: 'cloud-snow', 86: 'cloud-snow',
    95: 'cloud-lightning', 96: 'cloud-lightning-rain', 99: 'cloud-lightning-rain',
}


def _wmo_desc(code):
    try:
        from flask_babel import get_locale
        locale = str(get_locale())
    except Exception:
        locale = 'es'
    tabla = _WMO_DESC_RU if locale == 'ru' else _WMO_DESC_ES
    return tabla.get(code, f'código {code}')


def _wmo_icono(code):
    return _WMO_ICONO.get(code, 'cloud')


class ServicioClima:
    """
    Cliente para Open-Meteo.
    No requiere API key ni registro.
    Documentación: https://open-meteo.com/en/docs
    """

    # ─── Geocodificación ────────────────────────────────────────────────────

    def geocodificar(self, nombre_ciudad):
        """Convierte nombre de ciudad a (lat, lon, nombre, pais)."""
        # Acepta formato "Ciudad, ES" o solo "Ciudad"
        nombre = nombre_ciudad.split(',')[0].strip()
        respuesta = requests.get(_GEO_URL, params={
            'name': nombre,
            'count': 1,
            'language': 'es',
            'format': 'json'
        }, timeout=10)
        respuesta.raise_for_status()
        datos = respuesta.json()
        resultados = datos.get('results', [])
        if not resultados:
            raise ValueError(f'Ciudad no encontrada: {nombre_ciudad}')
        r = resultados[0]
        return r['latitude'], r['longitude'], r.get('name', nombre), r.get('country_code', '??')

    # ─── Clima actual ───────────────────────────────────────────────────────

    def obtener_clima_actual(self, ciudad):
        """Obtiene el clima actual geocodificando primero la ciudad."""
        lat, lon, nombre, pais = self.geocodificar(ciudad)
        return self.obtener_clima_por_coordenadas(lat, lon, nombre, pais)

    def obtener_clima_por_coordenadas(self, lat, lon, nombre='', pais=''):
        """Obtiene el clima actual + min/max diarios directamente por coordenadas."""
        respuesta = requests.get(_WEATHER_URL, params={
            'latitude': lat,
            'longitude': lon,
            'current': _CURRENT_PARAMS,
            'daily': 'temperature_2m_max,temperature_2m_min',
            'forecast_days': 1,
            'timezone': 'auto',
        }, timeout=10)
        respuesta.raise_for_status()
        datos = respuesta.json()
        return self._parsear_clima_actual(datos, nombre, pais, lat, lon)

    def _parsear_clima_actual(self, datos, nombre, pais, lat, lon):
        c = datos.get('current', {})
        code = c.get('weather_code', 0)
        daily = datos.get('daily', {})
        temp_min = (daily.get('temperature_2m_min') or [None])[0]
        temp_max = (daily.get('temperature_2m_max') or [None])[0]
        return {
            'ciudad': nombre,
            'pais': pais,
            'latitud': lat,
            'longitud': lon,
            'temperatura': c.get('temperature_2m'),
            'sensacion_termica': c.get('apparent_temperature'),
            'temp_min': temp_min,
            'temp_max': temp_max,
            'humedad': c.get('relative_humidity_2m'),
            'presion': c.get('surface_pressure'),
            'velocidad_viento': c.get('wind_speed_10m'),
            'direccion_viento': c.get('wind_direction_10m'),
            'descripcion': _wmo_desc(code),
            'icono': _wmo_icono(code),
            'nubosidad': c.get('cloud_cover'),
            'visibilidad': c.get('visibility'),
            'precipitacion': c.get('precipitation'),
            'timestamp': c.get('time'),
        }

    # ─── Pronóstico ─────────────────────────────────────────────────────────

    def obtener_pronostico(self, ciudad):
        """Obtiene el pronóstico de 7 días geocodificando primero la ciudad."""
        lat, lon, nombre, pais = self.geocodificar(ciudad)
        return self.obtener_pronostico_por_coordenadas(lat, lon, nombre, pais)

    def obtener_pronostico_por_coordenadas(self, lat, lon, nombre='', pais=''):
        """Obtiene pronóstico de 7 días + min/max del día actual por coordenadas."""
        respuesta = requests.get(_WEATHER_URL, params={
            'latitude': lat,
            'longitude': lon,
            'daily': _DAILY_PARAMS,
            'timezone': 'auto',
            'forecast_days': 7,
        }, timeout=10)
        respuesta.raise_for_status()
        datos = respuesta.json()
        return self._parsear_pronostico(datos, nombre, pais)

    def _parsear_pronostico(self, datos, nombre, pais):
        daily = datos.get('daily', {})
        fechas = daily.get('time', [])
        codes = daily.get('weather_code', [])
        t_max = daily.get('temperature_2m_max', [])
        t_min = daily.get('temperature_2m_min', [])
        prec = daily.get('precipitation_sum', [])
        viento = daily.get('wind_speed_10m_max', [])

        items = []
        for i, fecha in enumerate(fechas):
            code = codes[i] if i < len(codes) else 0
            items.append({
                'fecha': fecha,
                'temp_min': t_min[i] if i < len(t_min) else None,
                'temp_max': t_max[i] if i < len(t_max) else None,
                'humedad': None,  # No disponible en daily básico
                'descripcion': _wmo_desc(code),
                'icono': _wmo_icono(code),
                'velocidad_viento': viento[i] if i < len(viento) else None,
                'precipitacion': prec[i] if i < len(prec) else None,
            })
        return {'ciudad': nombre, 'pais': pais, 'pronostico': items}

    def guardar_registro(self, ciudad_id, datos_clima):
        """Guarda un registro de clima en la base de datos."""
        registro = RegistroClima(
            ciudad_id=ciudad_id,
            temperatura=datos_clima.get('temperatura'),
            sensacion_termica=datos_clima.get('sensacion_termica'),
            temp_min=datos_clima.get('temp_min'),
            temp_max=datos_clima.get('temp_max'),
            humedad=datos_clima.get('humedad'),
            presion=datos_clima.get('presion'),
            velocidad_viento=datos_clima.get('velocidad_viento'),
            direccion_viento=datos_clima.get('direccion_viento'),
            descripcion=datos_clima.get('descripcion'),
            icono=datos_clima.get('icono'),
            nubosidad=datos_clima.get('nubosidad'),
            visibilidad=datos_clima.get('visibilidad'),
            registrado_en=datetime.utcnow()
        )
        db.session.add(registro)
        db.session.commit()
        return registro

    def obtener_o_crear_ciudad(self, datos_clima):
        """Busca o crea una ciudad en la BD a partir de los datos de clima."""
        ciudad = Ciudad.query.filter_by(
            nombre=datos_clima['ciudad'],
            pais=datos_clima['pais']
        ).first()

        if not ciudad:
            ciudad = Ciudad(
                nombre=datos_clima['ciudad'],
                pais=datos_clima['pais'],
                latitud=datos_clima.get('latitud'),
                longitud=datos_clima.get('longitud')
            )
            db.session.add(ciudad)
            db.session.commit()

        return ciudad
