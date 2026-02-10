// booking.js

// --- LÓGICA PASO 1 Y 2 (SEDE Y BARBERO) ---
function seleccionarSede(sedeId) {
    const seccionBarberos = document.getElementById('seccion-barberos');
    const contenedorBarberos = document.getElementById('lista-barberos');
    const seccionCalendario = document.getElementById('seccion-calendario');

    seccionCalendario.style.display = 'none';
    contenedorBarberos.innerHTML = '<p style="color:black">Buscando barberos...</p>';
    seccionBarberos.style.display = 'block';

    fetch(`/ajax/obtener-barberos/?sede_id=${sedeId}`)
        .then(response => response.json())
        .then(data => {
            contenedorBarberos.innerHTML = '';
            if (data.length === 0) {
                contenedorBarberos.innerHTML = '<p style="color:black">No hay barberos en esta sede.</p>';
                return;
            }
            data.forEach(barbero => {
                contenedorBarberos.innerHTML += `
                    <div class="barbero-card" onclick="iniciarCalendario(${barbero.id}, '${barbero.nombre}')">
                        <img src="${barbero.url_foto}" class="barbero-foto">
                        <h3>${barbero.nombre}</h3>
                        <button class="btn-seleccionar">Seleccionar</button>
                    </div>`;
            });
        });
}

// --- LÓGICA PASO 3 (CALENDARIO) ---
function iniciarCalendario(id, nombre) {
    document.getElementById('seccion-calendario').style.display = 'block';
    document.getElementById('titulo-calendario').innerText = `Agendando con ${nombre}`;
    document.getElementById('horas-container').style.display = 'none';
    generarDias();
    document.getElementById('seccion-calendario').scrollIntoView({ behavior: 'smooth' });
}

function generarDias() {
    const grid = document.getElementById('calendar-grid');
    grid.innerHTML = '';
    const hoy = new Date();
    
    for (let i = 0; i < 30; i++) {
        let fecha = new Date();
        fecha.setDate(hoy.getDate() + i);
        
        const diaDiv = document.createElement('div');
        diaDiv.className = 'dia-item';
        const opciones = { weekday: 'short' };
        diaDiv.innerHTML = `<strong>${fecha.getDate()}</strong><br><small>${fecha.toLocaleString('es', opciones)}</small>`;
        
        diaDiv.onclick = function() {
            document.querySelectorAll('.dia-item').forEach(d => d.classList.remove('selected'));
            this.classList.add('selected');
            mostrarHoras(fecha.toLocaleDateString('es-ES', { day:'numeric', month:'long', year:'numeric' }));
        };
        grid.appendChild(diaDiv);
    }
}

function mostrarHoras(fechaTexto) {
    document.getElementById('horas-container').style.display = 'block';
    document.getElementById('fecha-seleccionada').innerText = fechaTexto;
    const lista = document.getElementById('lista-horas');
    lista.innerHTML = '';

    const horas = ["09:00", "10:00", "11:00", "12:00", "14:00", "15:00", "16:00", "17:00", "18:00", "19:00"];
    
    horas.forEach(h => {
        const btn = document.createElement('button');
        btn.className = 'hora-btn';
        btn.innerText = h;
        btn.onclick = () => abrirModal(fechaTexto, h);
        lista.appendChild(btn);
    });
}

// --- LÓGICA PASO 4 (MODAL Y WHATSAPP) ---
// booking.js

function abrirModal(fecha, hora) {
    const modal = document.getElementById('modal-reserva');
    document.getElementById('detalle-reserva-final').innerText = `${fecha} - ${hora}`;
    
    // Mostramos el modal añadiendo la clase active
    modal.classList.add('active');
}

function cerrarModal() {
    const modal = document.getElementById('modal-reserva');
    
    // Ocultamos el modal quitando la clase active
    modal.classList.remove('active');
}


function enviarConfirmacion() {
    const nombre = document.getElementById('nombre-cliente').value;
    const telefono = document.getElementById('telefono-cliente').value;

    if (!nombre || !telefono) {
        alert("Por favor completa tu nombre y teléfono");
        return;
    }

    alert(`Enviando código a ${telefono}...`);
}