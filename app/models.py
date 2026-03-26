from datetime import datetime
from app import db


class Ciudad(db.Model):
    __tablename__ = 'ciudades'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    pais = db.Column(db.String(10), nullable=False)
    latitud = db.Column(db.Float, nullable=True)
    longitud = db.Column(db.Float, nullable=True)
    creado_en = db.Column(db.DateTime, default=datetime.utcnow)

    registros = db.relationship('RegistroClima', backref='ciudad', lazy=True, cascade='all, delete-orphan')
    alertas = db.relationship('ConfigAlerta', backref='ciudad', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Ciudad {self.nombre}, {self.pais}>'

    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'pais': self.pais,
            'latitud': self.latitud,
            'longitud': self.longitud,
            'creado_en': self.creado_en.isoformat()
        }


class RegistroClima(db.Model):
    __tablename__ = 'registros_clima'

    id = db.Column(db.Integer, primary_key=True)
    ciudad_id = db.Column(db.Integer, db.ForeignKey('ciudades.id'), nullable=False)
    temperatura = db.Column(db.Float, nullable=False)
    sensacion_termica = db.Column(db.Float, nullable=True)
    temp_min = db.Column(db.Float, nullable=True)
    temp_max = db.Column(db.Float, nullable=True)
    humedad = db.Column(db.Integer, nullable=True)
    presion = db.Column(db.Float, nullable=True)
    velocidad_viento = db.Column(db.Float, nullable=True)
    direccion_viento = db.Column(db.Integer, nullable=True)
    codigo_wmo = db.Column(db.Integer, nullable=True)
    descripcion = db.Column(db.String(200), nullable=True)
    icono = db.Column(db.String(20), nullable=True)
    nubosidad = db.Column(db.Integer, nullable=True)
    visibilidad = db.Column(db.Integer, nullable=True)
    registrado_en = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<RegistroClima ciudad_id={self.ciudad_id} temp={self.temperatura}>'

    def to_dict(self):
        return {
            'id': self.id,
            'ciudad_id': self.ciudad_id,
            'temperatura': self.temperatura,
            'sensacion_termica': self.sensacion_termica,
            'temp_min': self.temp_min,
            'temp_max': self.temp_max,
            'humedad': self.humedad,
            'presion': self.presion,
            'velocidad_viento': self.velocidad_viento,
            'codigo_wmo': self.codigo_wmo,
            'descripcion': self.descripcion,
            'icono': self.icono,
            'nubosidad': self.nubosidad,
            'visibilidad': self.visibilidad,
            'registrado_en': self.registrado_en.isoformat()
        }


class ConfigAlerta(db.Model):
    __tablename__ = 'config_alertas'

    id = db.Column(db.Integer, primary_key=True)
    ciudad_id = db.Column(db.Integer, db.ForeignKey('ciudades.id'), nullable=False)
    tipo = db.Column(db.String(50), nullable=False)  # temp_min, temp_max, viento, humedad
    umbral = db.Column(db.Float, nullable=False)
    activa = db.Column(db.Boolean, default=True)
    creado_en = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<ConfigAlerta {self.tipo} umbral={self.umbral}>'

    def to_dict(self):
        return {
            'id': self.id,
            'ciudad_id': self.ciudad_id,
            'tipo': self.tipo,
            'umbral': self.umbral,
            'activa': self.activa,
            'creado_en': self.creado_en.isoformat()
        }


class HistorialAlerta(db.Model):
    __tablename__ = 'historial_alertas'

    id = db.Column(db.Integer, primary_key=True)
    config_alerta_id = db.Column(db.Integer, db.ForeignKey('config_alertas.id'), nullable=True)
    ciudad_id = db.Column(db.Integer, db.ForeignKey('ciudades.id'), nullable=False)
    tipo = db.Column(db.String(50), nullable=False)
    mensaje = db.Column(db.String(500), nullable=False)
    valor_actual = db.Column(db.Float, nullable=True)
    umbral = db.Column(db.Float, nullable=True)
    disparado_en = db.Column(db.DateTime, default=datetime.utcnow)
    leida = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f'<HistorialAlerta {self.tipo} ciudad_id={self.ciudad_id}>'

    def to_dict(self):
        return {
            'id': self.id,
            'ciudad_id': self.ciudad_id,
            'tipo': self.tipo,
            'mensaje': self.mensaje,
            'valor_actual': self.valor_actual,
            'umbral': self.umbral,
            'disparado_en': self.disparado_en.isoformat(),
            'leida': self.leida
        }
