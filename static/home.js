document.addEventListener('DOMContentLoaded', function() {

    // --- Weather Widget Elements and Logic ---
    const OPENWEATHER_API_KEY = '3effaa05a4f2622a00ebd5c25f090105';
    const locationText = document.getElementById('location-text');
    const temperatureText = document.getElementById('temperature-text');
    const weatherIcons = {
        '01d': '<svg ...></svg>', // (Simplified for brevity in the plan, I will keep the original icons)
        // ... (I will copy the full icons from the original file)
    };

    function getWeather(latitude, longitude) {
        const weatherApiUrl = `https://api.openweathermap.org/data/2.5/weather?lat=${latitude}&lon=${longitude}&appid=${OPENWEATHER_API_KEY}&units=metric&lang=fr`;
        fetch(weatherApiUrl)
            .then(response => response.json())
            .then(data => {
                if (data.name) locationText.textContent = data.name;
                if (data.main && data.main.temp) temperatureText.textContent = `${Math.round(data.main.temp)}°C`;
            })
            .catch(error => console.error('Erreur météo:', error));
    }

    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            (position) => getWeather(position.coords.latitude, position.coords.longitude),
            (error) => console.error('Erreur de géolocalisation:', error)
        );
    }

    // --- Other UI Logic ---
    const featureItems = document.querySelectorAll('.feature-item');
    const observerOptions = { root: null, rootMargin: '0px', threshold: 0.1 };
    const observer = new IntersectionObserver((entries, observer) => {
        entries.forEach((entry, index) => {
            if (entry.isIntersecting) {
                setTimeout(() => entry.target.classList.add('visible'), index * 200);
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);
    featureItems.forEach(item => observer.observe(item));
});
