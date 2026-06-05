let currentYear, currentMonth;
let selectedDateStr = null;
let selectedBarberoId = null;
let selectedServiceDuration = 30; // default in minutes
let reservaTemporal = {}; // Para guardar datos entre pasos

// Helper para obtener el token CSRF desde el meta tag de HTML
function getCsrfToken() {
    const meta = document.querySelector('meta[name="csrf-token"]');
    return meta ? meta.getAttribute('content') : '';
}

// Helper para determinar si una fecha está en el pasado (comparando año, mes y día de forma segura contra DST y timezones)
function isDateInPast(year, month, day) {
    const hoy = new Date();
    const hoyYear = hoy.getFullYear();
    const hoyMonth = hoy.getMonth();
    const hoyDay = hoy.getDate();
    
    if (year < hoyYear) return true;
    if (year > hoyYear) return false;
    
    if (month < hoyMonth) return true;
    if (month > hoyMonth) return false;
    
    return day < hoyDay;
}

// Sistema de Notificaciones (Toast)
function showToast(message, type = 'error') {
    // Eliminar toast anterior si existe
    const existingToast = document.getElementById('barber-toast');
    if (existingToast) {
        existingToast.remove();
    }

    const toast = document.createElement('div');
    toast.id = 'barber-toast';
    
    // Estilos base
    toast.style.position = 'fixed';
    toast.style.top = '20px';
    toast.style.left = '50%';
    toast.style.transform = 'translateX(-50%)';
    toast.style.padding = '15px 20px';
    toast.style.borderRadius = '8px';
    toast.style.color = '#fff';
    toast.style.fontWeight = '500';
    toast.style.fontSize = '0.95rem';
    toast.style.zIndex = '10000';
    toast.style.boxShadow = '0 10px 25px rgba(0,0,0,0.2)';
    toast.style.display = 'flex';
    toast.style.alignItems = 'center';
    toast.style.gap = '15px';
    toast.style.opacity = '0';
    toast.style.transition = 'opacity 0.3s ease, top 0.3s ease';
    toast.style.width = '90%';
    toast.style.maxWidth = '500px';
    toast.style.textAlign = 'left';
    toast.style.lineHeight = '1.4';

    // Colores e iconos según el tipo
    let iconName = 'info';
    if (type === 'error') {
        toast.style.backgroundColor = '#ef4444'; // Rojo moderno
        iconName = 'error';
    } else if (type === 'success') {
        toast.style.backgroundColor = '#10b981'; // Verde moderno
        iconName = 'check_circle';
    } else if (type === 'warning') {
        toast.style.backgroundColor = '#f59e0b'; // Naranja moderno
        iconName = 'warning';
    }

    toast.innerHTML = `
        <span class="material-symbols-outlined" style="font-size: 1.2rem;">${iconName}</span>
        <span>${message}</span>
    `;

    document.body.appendChild(toast);

    // Animar entrada
    setTimeout(() => {
        toast.style.opacity = '1';
        toast.style.top = '30px';
    }, 10);

    // Ocultar y remover después de 4 segundos
    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.top = '10px';
        setTimeout(() => {
            if (document.body.contains(toast)) {
                toast.remove();
            }
        }, 300);
    }, 4000);
}

// 1. Lógica de selección de Sede y Carga de Servicios
document.getElementById('select-sede').addEventListener('change', function() {
    const sedeId = this.value;
    const stepServicios = document.getElementById('step-servicios');
    const selectServicio = document.getElementById('select-servicio');
    const stepBarberos = document.getElementById('step-barberos');
    const stepCalendario = document.getElementById('step-calendario');

    // Ocultar pasos posteriores y limpiar
    stepServicios.style.display = 'none';
    stepBarberos.style.display = 'none';
    if (stepCalendario) stepCalendario.style.display = 'none';
    selectedDateStr = null;
    selectedBarberoId = null;

    selectServicio.innerHTML = '<option value="" selected disabled>Buscando servicios...</option>';
    stepServicios.style.display = 'block';

    fetch(`/ajax/servicios/?sede_id=${sedeId}`)
        .then(response => response.json())
        .then(data => {
            selectServicio.innerHTML = '<option value="" selected disabled>Seleccionar servicio...</option>';
            if (data.length > 0) {
                data.forEach(serv => {
                    selectServicio.innerHTML += `
                        <option value="${serv.id}" data-duration="${serv.duracion}">
                            ${serv.nombre} ($${serv.precio} - ${serv.duracion} min)
                        </option>`;
                });
            } else {
                selectServicio.innerHTML = '<option value="" selected disabled>No hay servicios disponibles.</option>';
            }
        })
        .catch(err => {
            console.error("Error al cargar servicios:", err);
            selectServicio.innerHTML = '<option value="" selected disabled>Error al cargar servicios.</option>';
        });
});

// 2. Lógica de selección de Servicio y Carga de Barberos
document.getElementById('select-servicio').addEventListener('change', function() {
    const sedeId = document.getElementById('select-sede').value;
    const selectedOption = this.options[this.selectedIndex];
    selectedServiceDuration = parseInt(selectedOption.getAttribute('data-duration')) || 30;

    const stepBarberos = document.getElementById('step-barberos');
    const listaBarberos = document.getElementById('lista-barberos');
    const stepCalendario = document.getElementById('step-calendario');

    // Ocultar pasos posteriores y limpiar
    stepBarberos.style.display = 'none';
    if (stepCalendario) stepCalendario.style.display = 'none';
    selectedDateStr = null;
    selectedBarberoId = null;

    listaBarberos.innerHTML = '<p class="opacity-50">Buscando barberos...</p>';
    stepBarberos.style.display = 'block';

    fetch(`/ajax/barberos/?sede_id=${sedeId}`)
        .then(response => response.json())
        .then(data => {
            listaBarberos.innerHTML = ''; 
            if (data.length > 0) {
                data.forEach(barber => {
                    listaBarberos.innerHTML += `
                        <div class="barber-card" onclick="seleccionarBarbero(${barber.id}, this)">
                            <div class="barber-avatar-container">
                                <img src="${barber.imagen_url}" alt="${barber.nombre}" class="barber-photo">
                            </div>
                            <h5>${barber.nombre}</h5>
                            <button class="btn-secondary">Seleccionar</button>
                        </div>`;
                });
            } else {
                listaBarberos.innerHTML = '<p class="text-warning small">No hay barberos disponibles.</p>';
            }
        })
        .catch(err => {
            console.error("Error al cargar barberos:", err);
            listaBarberos.innerHTML = '<p class="text-danger small">Error al cargar barberos.</p>';
        });
});

// 3. Lógica del Calendario y Selección de Barbero
function seleccionarBarbero(id, elemento) {
    // Gestión visual de la tarjeta seleccionada
    document.querySelectorAll('.barber-card').forEach(card => {
        card.classList.remove('selected');
        card.style.background = 'rgba(255, 255, 255, 0.1)';
    });
    elemento.classList.add('selected');
    elemento.style.background = 'var(--primary-gold)';
    
    selectedBarberoId = id;
    selectedDateStr = null; // Reset selection

    const calendarioSec = document.getElementById('step-calendario');
    if (calendarioSec) {
        calendarioSec.style.display = 'block';
        calendarioSec.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }

    // Inicializar mes actual
    const hoy = new Date();
    currentYear = hoy.getFullYear();
    currentMonth = hoy.getMonth();

    renderCustomCalendar(currentYear, currentMonth);

    // Reset slots message
    document.getElementById('slots-info-msg').innerText = "Selecciona un día en el calendario para ver los horarios.";
    document.getElementById('slots-wrapper').innerHTML = '';
}

// 4. Render del Calendario Personalizado
function renderCustomCalendar(year, month) {
    const meses = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'];
    document.getElementById('calendar-month-year').innerText = `${meses[month]} ${year}`;

    // Obtener primer día del mes (1 = Lunes, ..., 0 = Domingo)
    const firstDayIndex = new Date(year, month, 1).getDay();
    // Mapear Domingo (0) a 6, y Lunes (1) a 0, etc.
    const startDayIndex = firstDayIndex === 0 ? 6 : firstDayIndex - 1;

    // Total de días en el mes
    const totalDays = new Date(year, month + 1, 0).getDate();

    const calendarDaysEl = document.getElementById('calendar-days');
    calendarDaysEl.innerHTML = '';

    // Celdas vacías de relleno al inicio del mes
    for (let i = 0; i < startDayIndex; i++) {
        calendarDaysEl.innerHTML += `<div class="calendar-day empty"></div>`;
    }

    const hoyDate = new Date();
    hoyDate.setHours(0,0,0,0);

    // Generar días del mes
    for (let day = 1; day <= totalDays; day++) {
        const dateStr = `${year}-${(month + 1).toString().padStart(2, '0')}-${day.toString().padStart(2, '0')}`;
        
        let classes = 'calendar-day';
        const isPast = isDateInPast(year, month, day);
        let titleAttr = '';

        if (isPast) {
            classes += ' disabled';
            titleAttr = 'title="Este día ya no está disponible"';
        }
        if (selectedDateStr === dateStr) {
            classes += ' selected';
        }

        calendarDaysEl.innerHTML += `
            <div class="${classes}" data-date="${dateStr}" ${titleAttr} onclick="if(!this.classList.contains('disabled')) seleccionarDia('${dateStr}', this)">
                ${day}
            </div>`;
    }
}

// Configuración de los botones del mes en el calendario
document.getElementById('prev-month').onclick = () => {
    currentMonth--;
    if (currentMonth < 0) {
        currentMonth = 11;
        currentYear--;
    }
    renderCustomCalendar(currentYear, currentMonth);
};
document.getElementById('next-month').onclick = () => {
    currentMonth++;
    if (currentMonth > 11) {
        currentMonth = 0;
        currentYear++;
    }
    renderCustomCalendar(currentYear, currentMonth);
};

// 5. Manejar click en un día
function seleccionarDia(dateStr, elemento) {
    document.querySelectorAll('.calendar-day').forEach(el => el.classList.remove('selected'));
    elemento.classList.add('selected');
    selectedDateStr = dateStr;

    cargarSlots(selectedBarberoId, dateStr);
}

// 6. Cargar pastillas de horarios vía AJAX
function cargarSlots(barberoId, dateStr) {
    const slotsWrapper = document.getElementById('slots-wrapper');
    const servicioId = document.getElementById('select-servicio').value;
    
    // Formatear fecha para el mensaje de cabecera
    const partesFecha = dateStr.split('-');
    const dateFormatted = new Date(partesFecha[0], partesFecha[1] - 1, partesFecha[2]).toLocaleDateString('es-CO', {day: 'numeric', month: 'long'});
    document.getElementById('slots-info-msg').innerText = `Horarios para el ${dateFormatted}:`;

    slotsWrapper.innerHTML = '<p class="opacity-50 small">Buscando horarios...</p>';

    fetch(`/ajax/horarios-dia/?barbero_id=${barberoId}&fecha=${dateStr}&servicio_id=${servicioId}`)
        .then(res => res.json())
        .then(data => {
            slotsWrapper.innerHTML = '';
            if (data.mensaje) {
                slotsWrapper.innerHTML = `<p class="text-warning small">${data.mensaje}</p>`;
                return;
            }
            if (data.slots && data.slots.length > 0) {
                data.slots.forEach(slot => {
                    let badge = '';
                    let extraClass = '';
                    let clickHandler = `onclick="seleccionarSlot('${slot.hora}', '${slot.hora_formateada}', this)"`;
                    
                    if (slot.estado === 'Ocupado') {
                        extraClass = ' occupied';
                        clickHandler = '';
                        badge = '<span style="font-size: 8px; opacity: 0.6; text-transform: uppercase;">Ocupado</span>';
                    } else if (slot.estado === 'Pasado') {
                        extraClass = ' occupied';
                        clickHandler = '';
                        badge = '<span style="font-size: 8px; opacity: 0.6; text-transform: uppercase;">Pasado</span>';
                    } else if (slot.estado === 'Pendiente') {
                        extraClass = ' pending';
                        clickHandler = '';
                        badge = '<span style="font-size: 8px; opacity: 0.6; text-transform: uppercase;">En proceso</span>';
                    }
                    
                    slotsWrapper.innerHTML += `
                        <button class="time-slot${extraClass}" ${clickHandler}>
                            <span style="font-size: 1rem;">${slot.hora_formateada.split(' ')[0]}</span>
                            <span style="font-size: 0.7rem; text-transform: uppercase;">${slot.hora_formateada.split(' ')[1] || ''}</span>
                            ${badge}
                        </button>`;
                });
            } else {
                slotsWrapper.innerHTML = '<p class="opacity-50 small">No hay horarios de atención disponibles para este día.</p>';
            }
        })
        .catch(err => {
            console.error("Error al cargar horarios del día:", err);
            slotsWrapper.innerHTML = '<p class="text-danger small">Error al cargar horarios.</p>';
        });
}

// 7. Seleccionar un slot e iniciar reserva
function seleccionarSlot(hora24, hora12, element) {
    document.querySelectorAll('.time-slot').forEach(el => el.classList.remove('selected'));
    element.classList.add('selected');

    const servicioId = document.getElementById('select-servicio').value;
    
    // Guardamos info para el envío final de la reserva
    reservaTemporal = {
        barbero_id: selectedBarberoId,
        servicio_id: servicioId,
        fecha: selectedDateStr,
        hora: `${hora24}:00`
    };

    // Actualizar interfaz del modal de confirmación
    const partesFecha = selectedDateStr.split('-');
    const dateFormatted = new Date(partesFecha[0], partesFecha[1] - 1, partesFecha[2]).toLocaleDateString('es-CO', {day: 'numeric', month: 'long', year: 'numeric'});
    document.getElementById('reserva-info-text').innerText = 
        `Cita para el ${dateFormatted} a las ${hora12}`;
    
    document.getElementById('modal-reserva').style.display = 'flex';
    regresarPaso1(); // Resetear vista del modal
}

function solicitarCodigo() {
    const nombre = document.getElementById('cliente-nombre').value;
    const telefono = document.getElementById('cliente-telefono').value;

    if (!nombre || !telefono) {
        showToast("Por favor completa tus datos", "warning");
        return;
    }

    reservaTemporal.nombre = nombre;
    reservaTemporal.telefono = telefono;

    // Llamada al backend para crear la cita 'Pendiente' y enviar WhatsApp con protección CSRF
    fetch('/ajax/crear-cita-pendiente/', {
        method: 'POST',
        headers: { 
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken()
        },
        body: JSON.stringify(reservaTemporal)
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            document.getElementById('paso-datos').style.display = 'none';
            document.getElementById('paso-verificacion').style.display = 'block';
            document.getElementById('modal-titulo').innerText = "Verifica tu Cita";
        } else if (data.limite_excedido) {
            document.getElementById('paso-datos').style.display = 'none';
            document.getElementById('paso-limite-excedido').style.display = 'block';
            document.getElementById('modal-titulo').innerText = "Límite Excedido";
        } else {
            showToast(data.message, "error");
            document.querySelectorAll('.time-slot').forEach(el => el.classList.remove('selected'));
        }
    })
    .catch(err => {
        console.error("Error al solicitar código:", err);
        showToast("Ocurrió un error al procesar tu solicitud.", "error");
    });
}

function confirmarCitaFinal() {
    const codigo = document.getElementById('codigo-otp').value;

    fetch('/ajax/confirmar-codigo-otp/', {
        method: 'POST',
        headers: { 
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken()
        },
        body: JSON.stringify({
            telefono: reservaTemporal.telefono,
            codigo: codigo
        })
    })
    .then(res => res.json())
    .then(data => {
        if (data.verificado) {
            showToast("¡Cita agendada con éxito! Te esperamos.", "success");
            setTimeout(() => {
                location.reload(); // Recargar para ver la cita confirmada
            }, 2000);
        } else {
            showToast("Código incorrecto o expirado. Revisa tu WhatsApp.", "error");
        }
    })
    .catch(err => {
        console.error("Error al confirmar cita:", err);
        showToast("Ocurrió un error al verificar tu código.", "error");
    });
}

function cerrarModal() {
    if (reservaTemporal && reservaTemporal.telefono) {
        console.log("Cancelando cita pendiente para:", reservaTemporal.telefono);
        
        fetch('/ajax/cancelar-reserva-pendiente/', {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken()
            },
            body: JSON.stringify({
                telefono: reservaTemporal.telefono,
                barbero_id: reservaTemporal.barbero_id,
                fecha: reservaTemporal.fecha,
                hora: reservaTemporal.hora
            })
        })
        .then(res => res.json())
        .then(data => {
            console.log("Servidor: Cita eliminada correctamente");
            reservaTemporal = {};
            if (selectedBarberoId && selectedDateStr) {
                cargarSlots(selectedBarberoId, selectedDateStr);
            }
        })
        .catch(err => console.error("Error al cancelar:", err));
    } else {
        document.querySelectorAll('.time-slot').forEach(el => el.classList.remove('selected'));
    }

    document.getElementById('modal-reserva').style.display = 'none';
}

function regresarPaso1() {
    document.getElementById('paso-datos').style.display = 'block';
    document.getElementById('paso-verificacion').style.display = 'none';
    const pasoLimite = document.getElementById('paso-limite-excedido');
    if (pasoLimite) pasoLimite.style.display = 'none';
    document.getElementById('modal-titulo').innerText = "Agendar Cita";
}