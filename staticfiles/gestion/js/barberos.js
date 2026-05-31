// Función para abrir el modal de VACACIONES
window.openVacationsModal = function(url) {
    const modal = document.getElementById('vacationsModal');
    const btn = document.getElementById('confirmVacationsBtn');
    if (modal && btn) {
        btn.href = url;
        modal.style.display = 'flex';
    }
};

// Función para abrir el modal de ELIMINAR (Inhabilitar)
window.openRealDeleteModal = function(url) {
    const modal = document.getElementById('realDeleteModal');
    const btn = document.getElementById('confirmRealDeleteBtn');
    if (modal && btn) {
        btn.href = url;
        modal.style.display = 'flex';
    }
};

// Función para CERRAR cualquier modal
window.closeModal = function(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'none';
    }
};

// Cerrar si hacen clic fuera del cuadro blanco (en la parte oscura)
window.onclick = function(event) {
    if (event.target.classList.contains('modal-overlay')) {
        event.target.style.display = 'none';
    }
};