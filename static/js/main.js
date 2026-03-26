// Utilidades compartidas para toda la aplicación

/**
 * Muestra un mensaje de retroalimentación en un elemento.
 * @param {string} elementId - ID del elemento destino
 * @param {string} mensaje - Texto del mensaje
 * @param {'success'|'danger'|'warning'|'info'} tipo - Tipo de alerta Bootstrap
 */
function mostrarMensaje(elementId, mensaje, tipo = 'info') {
    const el = document.getElementById(elementId);
    if (!el) return;
    el.innerHTML = `<div class="alert alert-${tipo} py-1 px-2 mb-0">${mensaje}</div>`;
    setTimeout(() => { el.innerHTML = ''; }, 4000);
}

/**
 * Realiza un fetch con manejo de errores centralizado.
 */
async function apiFetch(url, opciones = {}) {
    const respuesta = await fetch(url, {
        headers: { 'Content-Type': 'application/json' },
        ...opciones
    });
    const datos = await respuesta.json();
    if (!respuesta.ok) {
        throw new Error(datos.error || `Error HTTP ${respuesta.status}`);
    }
    return datos;
}

/**
 * Formatea una temperatura con unidades.
 */
function formatTemp(valor) {
    if (valor == null) return '—';
    return `${Math.round(valor)}°C`;
}

/**
 * Formatea una fecha ISO a formato legible.
 */
function formatFecha(isoString) {
    if (!isoString) return '—';
    const d = new Date(isoString);
    return d.toLocaleString('es-ES', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' });
}

/**
 * Genera HTML de un ícono Bootstrap Icons a partir del nombre del ícono.
 * El tamaño lo controla el CSS según el contexto (.icono-clima, .card-pronostico).
 * @param {string} nombre
 * @returns {string}
 */
function iconoHtml(nombre) {
    if (!nombre) return '';
    return `<i class="bi bi-${nombre}"></i>`;
}
