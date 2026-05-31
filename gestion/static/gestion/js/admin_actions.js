function confirmarQuitarAdmin(sedeId, adminUser, sedeNombre) {
    Swal.fire({
        title: '¿Desvincular Administrador?',
        html: `El administrador <b>${adminUser}</b> ya no estará a cargo de la sede <b>${sedeNombre}</b>.<br><small class="text-muted">Sus datos permanecerán en el sistema.</small>`,
        icon: 'warning', // Cambiado a amarillo de advertencia
        iconColor: '#f39c12', // Un naranja/amarillo más elegante
        showCancelButton: true,
        confirmButtonColor: '#f39c12', // Botón a juego con el icono
        cancelButtonColor: '#dcdde1',
        confirmButtonText: 'Sí, desvincular',
        cancelButtonText: 'Cancelar',
        customClass: {
            confirmButton: 'btn-confirm-swal',
            cancelButton: 'btn-cancel-swal',
            popup: 'swal-custom-radius'
        },
        reverseButtons: true,
    }).then((result) => {
        if (result.isConfirmed) {
            window.location.href = `/admins/eliminar/${sedeId}/`;
        }
    })
}

function confirmarEliminarTotal(sedeId, username) {
    Swal.fire({
        title: '¿Eliminar de BarberApp?',
        text: `El usuario "${username}" será deshabilitado permanentemente. Esta acción no se puede deshacer.`,
        icon: 'error', // Aquí sí dejamos la X roja porque es una eliminación total
        showCancelButton: true,
        confirmButtonColor: '#d33',
        cancelButtonColor: '#3085d6',
        confirmButtonText: 'Eliminar permanentemente',
        cancelButtonText: 'Cancelar',
        reverseButtons: true
    }).then((result) => {
        if (result.isConfirmed) {
            window.location.href = `/admins/eliminar-total/${sedeId}/`;
        }
    });
}