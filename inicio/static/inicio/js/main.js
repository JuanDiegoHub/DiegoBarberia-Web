function saludar() {
    alert("¡Gracias por visitar DiegoBarberia! Pronto podrás agendar tu cita.");
}
// Carrusel de barberos
const track = document.querySelector('.carousel-track');
const container = document.querySelector('.carousel-container');
let cards = document.querySelectorAll('.barbero-card');

// 1. CLONACIÓN DINÁMICA: Clonamos varios para cubrir pantallas anchas
// Clonamos los primeros 4 al final y los últimos 4 al principio
const numClones = 4; 
for(let i = 0; i < numClones; i++) {
    const startClone = cards[i].cloneNode(true);
    const endClone = cards[cards.length - 1 - i].cloneNode(true);
    track.appendChild(startClone);
    track.insertBefore(endClone, track.firstChild);
}

// Actualizamos la lista tras clonar
cards = document.querySelectorAll('.barbero-card');
let currentIndex = numClones; // Empezamos en el primer barbero real
let isTransitioning = false;

function updateCarousel(instant = false) {
    // 1. Detectamos el estilo computado para obtener el margen exacto
    const style = window.getComputedStyle(cards[0]);
    const marginRight = parseFloat(style.marginRight);
    const marginLeft = parseFloat(style.marginLeft);
    
    // 2. Sumamos el ancho de la tarjeta + sus márgenes reales
    const cardWidth = cards[0].offsetWidth + marginRight + marginLeft;
    
    // 3. El resto del cálculo se mantiene igual y será exacto
    const centerOffset = (window.innerWidth / 2) - (cardWidth / 2);
    const position = centerOffset - (currentIndex * cardWidth);

    track.style.transition = instant ? 'none' : 'transform 0.6s cubic-bezier(0.23, 1, 0.32, 1)';
    track.style.transform = `translateX(${position}px)`;

    cards.forEach((card, i) => {
        card.classList.toggle('active', i === currentIndex);
    });
}

// Función para mover al siguiente
function nextSlide() {
    if (isTransitioning) return;
    isTransitioning = true;
    currentIndex++;
    updateCarousel();
}

// Escuchar cuando termina la animación para el salto infinito invisible
track.addEventListener('transitionend', () => {
    isTransitioning = false;
    const totalOriginals = cards.length - (numClones * 2);

    if (currentIndex >= cards.length - numClones) {
        currentIndex = numClones; // Salto al inicio real
        updateCarousel(true);
    }
    if (currentIndex < numClones) {
        currentIndex = cards.length - numClones - 1; // Salto al final real
        updateCarousel(true);
    }
});

// Auto-reproducción
let scrollInterval = setInterval(nextSlide, 3000);

// Pausa en hover
container.addEventListener('mouseenter', () => clearInterval(scrollInterval));
container.addEventListener('mouseleave', () => scrollInterval = setInterval(nextSlide, 3000));

// Ajuste si cambian el tamaño de la ventana (Resposive dinámico)
window.addEventListener('resize', () => updateCarousel(true));

// Inicio
updateCarousel(true);