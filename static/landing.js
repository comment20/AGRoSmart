document.addEventListener('DOMContentLoaded', () => {
    const slides = document.querySelectorAll('.slide');
    const dots = document.querySelectorAll('.nav-dot');
    let currentSlide = 0;
    let slideInterval;

    function showSlide(index) {
        // Cacher toutes les diapositives
        slides.forEach(slide => {
            slide.classList.remove('active');
        });

        // Désactiver tous les points
        dots.forEach(dot => {
            dot.classList.remove('active');
        });

        // Afficher la diapositive sélectionnée et activer le point correspondant
        slides[index].classList.add('active');
        dots[index].classList.add('active');
    }

    function nextSlide() {
        currentSlide = (currentSlide + 1) % slides.length;
        showSlide(currentSlide);
    }

    function startSlideShow() {
        // Changer de diapositive toutes les 5 secondes
        slideInterval = setInterval(nextSlide, 5000);
    }

    function stopSlideShow() {
        clearInterval(slideInterval);
    }

    // Ajouter un événement de clic aux points
    dots.forEach(dot => {
        dot.addEventListener('click', () => {
            stopSlideShow(); // Arrêter le défilement auto en cas de navigation manuelle
            currentSlide = parseInt(dot.dataset.slide);
            showSlide(currentSlide);
            startSlideShow(); // Redémarrer le défilement auto
        });
    });

    // Initialisation
    showSlide(currentSlide);
    startSlideShow();
});