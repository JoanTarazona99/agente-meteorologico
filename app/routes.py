from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from app import db
from app.models import Ciudad, RegistroClima, ConfigAlerta, HistorialAlerta
from app.services import ServicioClima
from app.alerts import SistemaAlertas

bp = Blueprint('main', __name__)


# ─── Cambio de idioma ────────────────────────────────────────────────────────

@bp.route('/set-lang/<lang>')
def set_lang(lang):
    from flask import current_app
    idiomas = current_app.config.get('LANGUAGES', ['es', 'ru'])
    if lang in idiomas:
        session['lang'] = lang
    return redirect(request.referrer or url_for('main.index'))


# ─── Vistas HTML ────────────────────────────────────────────────────────────

@bp.route('/')
def index():
    ciudades = Ciudad.query.order_by(Ciudad.nombre).all()
    alertas_no_leidas = HistorialAlerta.query.filter_by(leida=False).count()
    return render_template('dashboard.html', ciudades=ciudades, alertas_no_leidas=alertas_no_leidas)


@bp.route('/alertas')
def alertas():
    ciudades = Ciudad.query.order_by(Ciudad.nombre).all()
    configs = ConfigAlerta.query.filter_by(activa=True).all()
    historial = HistorialAlerta.query.order_by(HistorialAlerta.disparado_en.desc()).limit(50).all()
    return render_template('alertas.html', ciudades=ciudades, configs=configs, historial=historial)


# ─── API REST: Clima ─────────────────────────────────────────────────────────

@bp.route('/api/clima/actual', methods=['GET'])
def api_clima_actual():
    ciudad_nombre = request.args.get('ciudad')
    if not ciudad_nombre:
        return jsonify({'error': 'Parámetro "ciudad" requerido'}), 400

    try:
        servicio = ServicioClima()
        datos = servicio.obtener_clima_actual(ciudad_nombre)
        ciudad = servicio.obtener_o_crear_ciudad(datos)
        registro = servicio.guardar_registro(ciudad.id, datos)

        sistema_alertas = SistemaAlertas()
        alertas = sistema_alertas.evaluar_alertas(ciudad.id, datos)

        return jsonify({
            'status': 'ok',
            'clima': datos,
            'ciudad_id': ciudad.id,
            'alertas_disparadas': len(alertas)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/api/clima/pronostico', methods=['GET'])
def api_pronostico():
    ciudad_nombre = request.args.get('ciudad')
    if not ciudad_nombre:
        return jsonify({'error': 'Parámetro "ciudad" requerido'}), 400

    try:
        servicio = ServicioClima()
        datos = servicio.obtener_pronostico(ciudad_nombre)
        return jsonify({'status': 'ok', 'pronostico': datos})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ─── API REST: Histórico ──────────────────────────────────────────────────────

@bp.route('/api/historico', methods=['GET'])
def api_historico():
    from flask_babel import get_locale
    from app.services import _wmo_desc
    
    ciudad_id = request.args.get('ciudad_id', type=int)
    limite = request.args.get('limite', 24, type=int)

    query = RegistroClima.query
    if ciudad_id:
        query = query.filter_by(ciudad_id=ciudad_id)

    registros = query.order_by(RegistroClima.registrado_en.desc()).limit(limite).all()
    
    # Traducir descripción según el idioma actual
    registros_dict = []
    for r in registros:
        reg_dict = r.to_dict()
        if r.codigo_wmo is not None:
            reg_dict['descripcion'] = _wmo_desc(r.codigo_wmo)
        registros_dict.append(reg_dict)
    
    return jsonify({'status': 'ok', 'registros': registros_dict})


# ─── API REST: Ciudades ───────────────────────────────────────────────────────

@bp.route('/api/ciudades', methods=['GET'])
def api_ciudades():
    ciudades = Ciudad.query.order_by(Ciudad.nombre).all()
    return jsonify({'status': 'ok', 'ciudades': [c.to_dict() for c in ciudades]})


@bp.route('/api/ciudades/<int:ciudad_id>', methods=['DELETE'])
def api_eliminar_ciudad(ciudad_id):
    ciudad = Ciudad.query.get_or_404(ciudad_id)
    db.session.delete(ciudad)
    db.session.commit()
    return jsonify({'status': 'ok', 'mensaje': f'Ciudad {ciudad.nombre} eliminada'})


# ─── API REST: Alertas ────────────────────────────────────────────────────────

@bp.route('/api/alertas', methods=['GET'])
def api_alertas():
    ciudad_id = request.args.get('ciudad_id', type=int)
    sistema = SistemaAlertas()
    alertas = sistema.obtener_alertas_no_leidas(ciudad_id)
    return jsonify({'status': 'ok', 'alertas': [a.to_dict() for a in alertas]})


@bp.route('/api/alertas', methods=['POST'])
def api_crear_alerta():
    datos = request.get_json()
    if not datos:
        return jsonify({'error': 'JSON requerido'}), 400

    ciudad_id = datos.get('ciudad_id')
    tipo = datos.get('tipo')
    umbral = datos.get('umbral')

    if not all([ciudad_id, tipo, umbral is not None]):
        return jsonify({'error': 'Campos requeridos: ciudad_id, tipo, umbral'}), 400

    try:
        sistema = SistemaAlertas()
        config = sistema.crear_alerta(ciudad_id, tipo, umbral)
        return jsonify({'status': 'ok', 'alerta': config.to_dict()}), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/api/alertas/<int:alerta_id>/desactivar', methods=['POST'])
def api_desactivar_alerta(alerta_id):
    try:
        sistema = SistemaAlertas()
        config = sistema.desactivar_alerta(alerta_id)
        return jsonify({'status': 'ok', 'alerta': config.to_dict()})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/api/alertas/<int:historial_id>/leer', methods=['POST'])
def api_marcar_leida(historial_id):
    try:
        sistema = SistemaAlertas()
        historial = sistema.marcar_leida(historial_id)
        return jsonify({'status': 'ok', 'historial': historial.to_dict()})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
