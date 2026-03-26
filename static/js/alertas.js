// ─── Alertas: Lógica de la página de alertas ──────────────────────────────

const AYUDA_TIPOS = {
    temp_max: ['°C', () => window.I18N.ayudaTempMax],
    temp_min: ['°C', () => window.I18N.ayudaTempMin],
    viento:   ['m/s', () => window.I18N.ayudaViento],
    humedad:  ['%',  () => window.I18N.ayudaHumedad]
};

// ─── Eventos al cargar página ───────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
    // Cambio de tipo de alerta → actualizar unidades y ayuda
    document.getElementById('alertaTipo').addEventListener('change', (e) => {
        const info = AYUDA_TIPOS[e.target.value] || ['', () => ''];
        document.getElementById('unidadUmbral').textContent = `(${info[0]})`;
        document.getElementById('textoAyudaUmbral').textContent = info[1]();
    });

    // Formulario nueva alerta
    document.getElementById('formNuevaAlerta').addEventListener('submit', crearAlerta);

    // Botones desactivar alertas existentes
    document.querySelectorAll('.btnDesactivar').forEach(btn => {
        btn.addEventListener('click', () => desactivarAlerta(btn.dataset.id, btn));
    });

    // Botones marcar leída
    document.querySelectorAll('.btnLeer').forEach(btn => {
        btn.addEventListener('click', () => marcarLeida(btn.dataset.id, btn));
    });

    // Marcar todas como leídas
    const btnTodas = document.getElementById('btnMarcarTodas');
    if (btnTodas) btnTodas.addEventListener('click', marcarTodas);
});

// ─── Crear nueva alerta ─────────────────────────────────────────────────────
async function crearAlerta(e) {
    e.preventDefault();
    const ciudadId = document.getElementById('alertaCiudad').value;
    const tipo = document.getElementById('alertaTipo').value;
    const umbral = document.getElementById('alertaUmbral').value;

    if (!ciudadId || !tipo || umbral === '') {
        mostrarMensaje('mensajeAlerta', window.I18N.completaCampos, 'warning');
        return;
    }

    try {
        await apiFetch('/api/alertas', {
            method: 'POST',
            body: JSON.stringify({ ciudad_id: parseInt(ciudadId), tipo, umbral: parseFloat(umbral) })
        });
        mostrarMensaje('mensajeAlerta', window.I18N.alertaCreada, 'success');
        document.getElementById('formNuevaAlerta').reset();
    } catch (error) {
        mostrarMensaje('mensajeAlerta', `❌ Error: ${error.message}`, 'danger');
    }
}

// ─── Desactivar alerta ──────────────────────────────────────────────────────
async function desactivarAlerta(id, btn) {
    if (!confirm(window.I18N.confirmarDesact)) return;
    try {
        await apiFetch(`/api/alertas/${id}/desactivar`, { method: 'POST' });
        btn.closest('li').remove();
    } catch (error) {
        alert(`Error al desactivar: ${error.message}`);
    }
}

// ─── Marcar alerta como leída ───────────────────────────────────────────────
async function marcarLeida(id, btn) {
    try {
        await apiFetch(`/api/alertas/${id}/leer`, { method: 'POST' });
        const fila = btn.closest('tr');
        fila.classList.remove('table-warning');
        btn.closest('td').innerHTML = `<span class="text-muted small"><i class="bi bi-check2-all"></i> ${window.I18N.leida}</span>`;
    } catch (error) {
        alert(`Error: ${error.message}`);
    }
}

// ─── Marcar todas como leídas ──────────────────────────────────────────────
async function marcarTodas() {
    const btns = document.querySelectorAll('.btnLeer');
    for (const btn of btns) {
        await marcarLeida(btn.dataset.id, btn);
    }
}
