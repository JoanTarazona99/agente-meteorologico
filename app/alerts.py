from datetime import datetime
from flask_babel import lazy_gettext as _l, gettext as _
from app import db
from app.models import ConfigAlerta, HistorialAlerta

TIPOS_ALERTA = {
    'temp_max': _l('Temperatura máxima superada'),
    'temp_min': _l('Temperatura mínima alcanzada'),
    'viento':   _l('Velocidad de viento elevada'),
    'humedad':  _l('Humedad elevada'),
}


class SistemaAlertas:
    """Gestiona la evaluación y disparo de alertas meteorológicas."""

    def evaluar_alertas(self, ciudad_id, datos_clima):
        """Evalúa todas las alertas activas de una ciudad contra los datos actuales."""
        alertas_disparadas = []
        configs = ConfigAlerta.query.filter_by(ciudad_id=ciudad_id, activa=True).all()

        for config in configs:
            alerta = self._evaluar_condicion(config, datos_clima)
            if alerta:
                alertas_disparadas.append(alerta)

        return alertas_disparadas

    def _evaluar_condicion(self, config, datos_clima):
        """Evalúa una condición de alerta específica."""
        valor = None
        disparada = False

        if config.tipo == 'temp_max':
            valor = datos_clima.get('temp_max') or datos_clima.get('temperatura')
            if valor is not None and valor >= config.umbral:
                disparada = True

        elif config.tipo == 'temp_min':
            valor = datos_clima.get('temp_min') or datos_clima.get('temperatura')
            if valor is not None and valor <= config.umbral:
                disparada = True

        elif config.tipo == 'viento':
            valor = datos_clima.get('velocidad_viento')
            if valor is not None and valor >= config.umbral:
                disparada = True

        elif config.tipo == 'humedad':
            valor = datos_clima.get('humedad')
            if valor is not None and valor >= config.umbral:
                disparada = True

        if disparada:
            return self._crear_historial(config, valor, datos_clima)

        return None

    def _crear_historial(self, config, valor_actual, datos_clima):
        """Crea un registro en el historial de alertas."""
        descripcion_tipo = str(TIPOS_ALERTA.get(config.tipo, config.tipo))
        mensaje = _(
            '%(desc)s: valor actual %(val).1f, umbral configurado %(umbral).1f',
            desc=descripcion_tipo,
            val=valor_actual,
            umbral=config.umbral
        )

        historial = HistorialAlerta(
            config_alerta_id=config.id,
            ciudad_id=config.ciudad_id,
            tipo=config.tipo,
            mensaje=mensaje,
            valor_actual=valor_actual,
            umbral=config.umbral,
            disparado_en=datetime.utcnow(),
            leida=False
        )
        db.session.add(historial)
        db.session.commit()
        return historial

    def crear_alerta(self, ciudad_id, tipo, umbral):
        """Crea una nueva configuración de alerta para una ciudad."""
        if tipo not in TIPOS_ALERTA:
            raise ValueError(f"Tipo de alerta inválido: {tipo}. Válidos: {list(TIPOS_ALERTA.keys())}")

        config = ConfigAlerta(
            ciudad_id=ciudad_id,
            tipo=tipo,
            umbral=float(umbral),
            activa=True
        )
        db.session.add(config)
        db.session.commit()
        return config

    def desactivar_alerta(self, alerta_id):
        """Desactiva una configuración de alerta."""
        config = ConfigAlerta.query.get_or_404(alerta_id)
        config.activa = False
        db.session.commit()
        return config

    def marcar_leida(self, historial_id):
        """Marca una alerta del historial como leída."""
        historial = HistorialAlerta.query.get_or_404(historial_id)
        historial.leida = True
        db.session.commit()
        return historial

    def obtener_alertas_no_leidas(self, ciudad_id=None):
        """Obtiene alertas no leídas, opcionalmente filtradas por ciudad."""
        query = HistorialAlerta.query.filter_by(leida=False)
        if ciudad_id:
            query = query.filter_by(ciudad_id=ciudad_id)
        return query.order_by(HistorialAlerta.disparado_en.desc()).all()
