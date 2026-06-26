// ─── Asistente de voz: dictado de ciudad (solo entrada) ──────────────────────
// Usa la Web Speech API nativa del navegador (SpeechRecognition) para
// transcribir el nombre de una ciudad hablada, rellenar el campo de búsqueda
// y lanzar la consulta automáticamente. Sin síntesis de voz (TTS).
// Reutiliza buscarClima() y mostrarMensaje() de dashboard.js / main.js.

let reconocimiento = null;
let escuchando = false;

document.addEventListener('DOMContentLoaded', () => {
    const btnVoz = document.getElementById('btnVoz');
    if (!btnVoz) return;

    // Detección de soporte del navegador (Chrome/Edge/Safari).
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
        btnVoz.disabled = true;
        btnVoz.classList.add('opacity-50');
        btnVoz.title = window.I18N.vozNoSoportado;
        return;
    }

    reconocimiento = new SpeechRecognition();
    // El idioma de reconocimiento sigue el locale activo de la página.
    reconocimiento.lang = (document.documentElement.lang === 'ru') ? 'ru-RU' : 'es-ES';
    reconocimiento.interimResults = false;
    reconocimiento.maxAlternatives = 1;
    reconocimiento.continuous = false;

    reconocimiento.onresult = (evento) => {
        const texto = evento.results[0][0].transcript.trim();
        if (texto) {
            document.getElementById('inputCiudad').value = texto;
            // Búsqueda automática: equivale a escribir y pulsar Enter.
            if (typeof buscarClima === 'function') buscarClima();
        }
    };

    reconocimiento.onerror = (evento) => {
        detenerEscucha();
        // El error más común es 'not-allowed' (permiso de micrófono denegado).
        mostrarMensaje('mensajeBusqueda',
            `🎤 ${window.I18N.vozErrorMicrofono}`, 'danger');
    };

    reconocimiento.onend = () => detenerEscucha();

    btnVoz.addEventListener('click', toggleEscucha);
});

// ─── Activar / desactivar el micrófono ──────────────────────────────────────
function toggleEscucha() {
    if (!reconocimiento) return;

    if (escuchando) {
        reconocimiento.stop();
        detenerEscucha();
        return;
    }

    try {
        reconocimiento.start();
        iniciarEscucha();
    } catch (e) {
        // start() lanza si se llama dos veces seguidas; lo ignoramos con seguridad.
        detenerEscucha();
    }
}

function iniciarEscucha() {
    escuchando = true;
    const btn = document.getElementById('btnVoz');
    btn.classList.add('escuchando');
    btn.innerHTML = '<span class="spinner-border spinner-border-sm"></span>';
    btn.title = window.I18N.vozEscuchando;
    mostrarMensaje('mensajeBusqueda', `🎤 ${window.I18N.vozEscuchando}`, 'info');
}

function detenerEscucha() {
    escuchando = false;
    const btn = document.getElementById('btnVoz');
    if (!btn) return;
    btn.classList.remove('escuchando');
    btn.innerHTML = '<i class="bi bi-mic-fill"></i>';
    btn.title = window.I18N.vozHablar;
}
