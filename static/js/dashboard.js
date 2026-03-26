// ─── Dashboard: Lógica principal ───────────────────────────────────────────

let graficaTemp = null;

// ─── Eventos al cargar página ───────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('btnBuscar').addEventListener('click', buscarClima);
    document.getElementById('inputCiudad').addEventListener('keydown', (e) => {
        if (e.key === 'Enter') buscarClima();
    });

    const selectCiudad = document.getElementById('selectCiudad');
    if (selectCiudad) {
        selectCiudad.addEventListener('change', () => {
            if (selectCiudad.value) {
                document.getElementById('inputCiudad').value = selectCiudad.value;
                buscarClima();
            }
        });
    }

    const selectHistorico = document.getElementById('selectCiudadHistorico');
    if (selectHistorico) {
        selectHistorico.addEventListener('change', () => cargarHistorico(selectHistorico.value));
        cargarHistorico('');
    }
});

// ─── Buscar clima actual ────────────────────────────────────────────────────
async function buscarClima() {
    const ciudad = document.getElementById('inputCiudad').value.trim();
    if (!ciudad) {
        mostrarMensaje('mensajeBusqueda', window.I18N.ingresaCiudad, 'warning');
        return;
    }

    const btn = document.getElementById('btnBuscar');
    btn.disabled = true;
    btn.innerHTML = `<span class="spinner-border spinner-border-sm me-1"></span>${window.I18N.cargando}`;
    mostrarMensaje('mensajeBusqueda', window.I18N.obteniendo, 'info');

    try {
        const datos = await apiFetch(`/api/clima/actual?ciudad=${encodeURIComponent(ciudad)}`);
        mostrarClima(datos.clima);

        if (datos.alertas_disparadas > 0) {
            mostrarMensaje('mensajeBusqueda',
                window.I18N.alertasDisp.replace('{n}', datos.alertas_disparadas), 'warning');
        } else {
            mostrarMensaje('mensajeBusqueda', window.I18N.datosObtenidos, 'success');
        }

        await buscarPronostico(ciudad);
        await actualizarCiudades();
        await cargarHistorico(document.getElementById('selectCiudadHistorico').value);
    } catch (error) {
        mostrarMensaje('mensajeBusqueda', `❌ Error: ${error.message}`, 'danger');
    } finally {
        btn.disabled = false;
        btn.innerHTML = `<i class="bi bi-cloud-download me-1"></i>${window.I18N.obtenerClima}`;
    }
}

// ─── Actualizar panel de ciudades guardadas ────────────────────────────────
async function actualizarCiudades() {
    try {
        const datos = await apiFetch('/api/ciudades');
        const ciudades = datos.ciudades;

        // Contador
        document.getElementById('contadorCiudades').textContent = ciudades.length;

        // Select panel superior
        const contenedor = document.getElementById('contenedorSelectCiudad');
        if (ciudades.length > 0) {
            const opciones = ciudades
                .map(c => `<option value="${c.nombre},${c.pais}">${c.nombre}, ${c.pais}</option>`)
                .join('');
            contenedor.innerHTML = `
                <select class="form-select form-select-sm" id="selectCiudad">
                    <option value="">${window.I18N.selCiudadGuard}</option>
                    ${opciones}
                </select>`;
            document.getElementById('selectCiudad').addEventListener('change', (e) => {
                if (e.target.value) {
                    document.getElementById('inputCiudad').value = e.target.value;
                    buscarClima();
                }
            });
        } else {
            contenedor.innerHTML = '';
        }

        // Select histórico: mantener selección actual
        const selectHist = document.getElementById('selectCiudadHistorico');
        const valorActual = selectHist.value;
        const opcionesHist = ciudades
            .map(c => `<option value="${c.id}">${c.nombre}</option>`)
            .join('');
        selectHist.innerHTML = `<option value="">${window.I18N.todasCiudades}</option>${opcionesHist}`;
        selectHist.value = valorActual;
    } catch (_) {}
}

// ─── Mostrar datos del clima en pantalla ───────────────────────────────────
function mostrarClima(clima) {
    document.getElementById('tempActual').textContent = formatTemp(clima.temperatura);
    document.getElementById('ciudadNombreClima').textContent = `${clima.ciudad}, ${clima.pais}`;
    document.getElementById('descClima').textContent = clima.descripcion;
    document.getElementById('sensacion').textContent = formatTemp(clima.sensacion_termica);
    document.getElementById('humedad').textContent = `${clima.humedad}%`;
    document.getElementById('viento').textContent = `${clima.velocidad_viento} m/s`;
    document.getElementById('presion').textContent = `${clima.presion} hPa`;
    document.getElementById('tempMin').textContent = formatTemp(clima.temp_min);
    document.getElementById('tempMax').textContent = formatTemp(clima.temp_max);

    const icono = document.getElementById('iconoClima');
    if (clima.icono) {
        icono.innerHTML = iconoHtml(clima.icono);
    }

    document.getElementById('panelClima').classList.remove('d-none');
}

// ─── Pronóstico ────────────────────────────────────────────────────────────
async function buscarPronostico(ciudad) {
    try {
        const datos = await apiFetch(`/api/clima/pronostico?ciudad=${encodeURIComponent(ciudad)}`);
        mostrarPronostico(datos.pronostico.pronostico);
    } catch (_) {
        // El pronóstico es secundario, no mostramos error crítico
    }
}

function mostrarPronostico(items) {
    const panel = document.getElementById('panelPronostico');
    const lista = document.getElementById('listaPronostico');

    // Open-Meteo devuelve un item por día (ya daily)
    const porDia = items.slice(0, 7);

    lista.innerHTML = porDia.map(item => `
        <div class="col">
            <div class="card-pronostico p-2 text-center h-100">
                <div class="small text-muted">${item.fecha}</div>
                ${iconoHtml(item.icono)}
                <div class="fw-bold mt-1">${formatTemp(item.temp_max)} / ${formatTemp(item.temp_min)}</div>
                <div class="small text-capitalize text-muted">${item.descripcion}</div>
                <div class="small text-muted">💨 ${item.velocidad_viento} m/s</div>
            </div>
        </div>
    `).join('');

    panel.classList.remove('d-none');
}

// ─── Histórico y gráfica ───────────────────────────────────────────────────
async function cargarHistorico(ciudadId = '') {
    try {
        const url = ciudadId
            ? `/api/historico?ciudad_id=${ciudadId}&limite=24`
            : '/api/historico?limite=24';
        const datos = await apiFetch(url);
        renderGrafica(datos.registros);
        renderTablaHistorico(datos.registros);
    } catch (_) {}
}

function renderGrafica(registros) {
    if (graficaTemp) { graficaTemp.destroy(); graficaTemp = null; }

    const ctx = document.getElementById('graficaTemperatura').getContext('2d');

    if (!registros.length) {
        ctx.clearRect(0, 0, ctx.canvas.width, ctx.canvas.height);
        ctx.fillStyle = getComputedStyle(document.body).color || '#888';
        ctx.font = '14px sans-serif';
        ctx.textAlign = 'center';
        ctx.fillText(window.I18N.sinRegistros, ctx.canvas.width / 2, ctx.canvas.height / 2);
        return;
    }

    const etiquetas = registros.map(r => r.registrado_en.replace('T', ' ').substring(5, 16)).reverse();
    const temps = registros.map(r => r.temperatura).reverse();

    graficaTemp = new Chart(ctx, {
        type: 'line',
        data: {
            labels: etiquetas,
            datasets: [{
                label: window.I18N.tempLabel,
                data: temps,
                borderColor: '#1976d2',
                backgroundColor: 'rgba(25, 118, 210, 0.08)',
                fill: true,
                tension: 0.4,
                pointRadius: 3
            }]
        },
        options: {
            responsive: true,
            plugins: { legend: { display: false } },
            scales: {
                y: { title: { display: true, text: '°C' } }
            }
        }
    });
}

function renderTablaHistorico(registros) {
    const tabla = document.getElementById('tablaHistorico');
    if (!registros.length) {
        tabla.innerHTML = `<div class="text-center text-muted py-3 small">${window.I18N.sinRegistros}</div>`;
        return;
    }
    tabla.innerHTML = registros.slice(0, 10).map(r => `
        <div class="list-group-item">
            <div class="d-flex justify-content-between">
                <span class="fw-semibold">${formatTemp(r.temperatura)}</span>
                <small class="text-muted">${formatFecha(r.registrado_en)}</small>
            </div>
            <small class="text-muted text-capitalize">${r.descripcion || ''} • 💧${r.humedad}%</small>
        </div>
    `).join('');
}
