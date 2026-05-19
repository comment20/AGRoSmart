document.addEventListener('DOMContentLoaded', function() {

    // --- Weather Widget Elements and Logic ---
    const OPENWEATHER_API_KEY = '3effaa05a4f2622a00ebd5c25f090105';
    const locationText = document.getElementById('location-text');
    const temperatureText = document.getElementById('temperature-text');
    const weatherIcons = { /* Weather icons mapping... */ };

    function getWeather(latitude, longitude) {
        const weatherApiUrl = `https://api.openweathermap.org/data/2.5/weather?lat=${latitude}&lon=${longitude}&appid=${OPENWEATHER_API_KEY}&units=metric&lang=fr`;
        fetch(weatherApiUrl)
            .then(response => response.json())
            .then(data => {
                if (data.name) locationText.textContent = data.name;
                if (data.main && data.main.temp) temperatureText.textContent = `${Math.round(data.main.temp)}°C`;
                const weatherIconSpan = document.querySelector('.temperature-icon');
                if (data.weather && data.weather.length > 0 && weatherIcons[data.weather[0].icon]) {
                    weatherIconSpan.innerHTML = weatherIcons[data.weather[0].icon];
                }
            })
            .catch(error => console.error('Erreur météo:', error));
    }

    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            (position) => getWeather(position.coords.latitude, position.coords.longitude),
            (error) => console.error('Erreur de géolocalisation:', error)
        );
    }

    // --- Chatbot Elements ---
    const chatbotIcon = document.getElementById('chatbot-icon');
    const chatbotWindow = document.getElementById('chatbot-window');
    const closeChatbotBtn = document.getElementById('close-chatbot-btn');
    const clearChatBtn = document.getElementById('clear-chat-btn');
    const chatbotMessages = document.getElementById('chatbot-messages');
    const chatbotInputField = document.getElementById('chatbot-input-field');
    const sendMessageBtn = document.getElementById('send-message-btn');

    // --- Chatbot Core Functions ---
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    function toggleChatbot() {
        chatbotWindow.classList.toggle('open');
        if (chatbotWindow.classList.contains('open')) {
            loadChatHistory();
        }
    }

    function addMessage(msg) {
        const messageBubble = document.createElement('div');
        messageBubble.classList.add('message-bubble');

        if (msg.is_from_user) {
            messageBubble.classList.add('message-user');
            const messageText = document.createElement('span');
            messageText.textContent = msg.message;
            messageBubble.appendChild(messageText);
        } else {
            messageBubble.classList.add('message-bot');
            const botContent = document.createElement('div');
            
            // Nettoyage complet et formatage structuré
            let text = msg.message;
            
            // 1. Gérer les titres (supprimer les # et mettre en gras/grand)
            text = text.replace(/^### (.*$)/gim, '<div style="font-weight: bold; font-size: 1.1em; margin-top: 10px; color: #2c5e3f;">$1</div>');
            text = text.replace(/^## (.*$)/gim, '<div style="font-weight: bold; font-size: 1.2em; margin-top: 12px; color: #2c5e3f; border-bottom: 1px solid #e2e8f0;">$1</div>');
            text = text.replace(/^# (.*$)/gim, '<div style="font-weight: 800; font-size: 1.3em; color: #2c5e3f;">$1</div>');

            // 2. Gérer le gras et italique (enlève les ** et *)
            text = text.replace(/\*\*\*(.*?)\*\*\*/g, '<strong><em>$1</em></strong>');
            text = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
            text = text.replace(/\*(.*?)\*/g, '<em>$1</em>');

            // 3. Gérer les listes (tirets et points)
            text = text.replace(/^\s*[\-\•]\s+(.*)/gim, '<li style="margin-left: 15px; margin-bottom: 5px;">$1</li>');
            
            // 4. Transformer les blocs de texte en paragraphes (doubles retours à la ligne)
            let paragraphs = text.split(/\n\n+/);
            let formattedHtml = paragraphs.map(p => {
                if (p.includes('<li') || p.includes('<div')) return p; // Ne pas entourer de <p> si c'est déjà structuré
                return `<p style="margin-bottom: 10px;">${p.replace(/\n/g, '<br>')}</p>`;
            }).join('');
            
            botContent.innerHTML = formattedHtml;
            messageBubble.appendChild(botContent);
        }

        if (msg.id) {
            messageBubble.dataset.messageId = msg.id;
            const optionsDiv = document.createElement('div');
            optionsDiv.classList.add('message-options');
            const optionsBtn = document.createElement('button');
            optionsBtn.classList.add('options-btn');
            optionsBtn.innerHTML = '&#8942;';
            const optionsMenu = document.createElement('div');
            optionsMenu.classList.add('options-menu');
            const deleteLink = document.createElement('a');
            deleteLink.href = '#';
            deleteLink.classList.add('delete-link');
            deleteLink.textContent = 'Supprimer';
            optionsMenu.appendChild(deleteLink);
            optionsDiv.appendChild(optionsBtn);
            optionsDiv.appendChild(optionsMenu);
            messageBubble.appendChild(optionsDiv);
        }

        chatbotMessages.appendChild(messageBubble);
        chatbotMessages.scrollTop = chatbotMessages.scrollHeight;
    }

    async function sendMessage() {
        const messageText = chatbotInputField.value.trim();
        if (messageText === '') return;
        addMessage({ message: messageText, is_from_user: true });
        chatbotInputField.value = '';
        try {
            const response = await fetch('/chatbot/send_message/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCookie('csrftoken') },
                body: JSON.stringify({ message: messageText })
            });
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            const data = await response.json();
            addMessage({ message: data.message, is_from_user: false });
        } catch (error) {
            console.error('Error sending message:', error);
            addMessage({ message: 'Désolé, une erreur est survenue.', is_from_user: false });
        }
    }

    async function deleteMessage(messageId, element) {
        try {
            const response = await fetch('/chatbot/delete_message/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCookie('csrftoken') },
                body: JSON.stringify({ message_id: messageId })
            });
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Failed to delete message');
            }
            const data = await response.json();
            if (data.status === 'success') {
                element.remove();
            } else {
                alert('Erreur: ' + data.error);
            }
        } catch (error) {
            console.error('Error deleting message:', error);
            alert('Une erreur est survenue lors de la suppression.');
        }
    }

    async function loadChatHistory() {
        chatbotMessages.innerHTML = '';
        try {
            const response = await fetch('/chatbot/history/');
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            const data = await response.json();
            data.forEach(msg => addMessage(msg));
        } catch (error) {
            console.error('Error loading chat history:', error);
            addMessage({ message: 'Impossible de charger l\'historique.', is_from_user: false });
        }
    }

    async function clearChatHistory() {
        if (!confirm('Êtes-vous sûr de vouloir effacer toute la conversation ?')) return;
        try {
            const response = await fetch('/chatbot/clear_history/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCookie('csrftoken') }
            });
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Failed to clear history');
            }
            chatbotMessages.innerHTML = '';
            addMessage({ message: 'Historique effacé.', is_from_user: false });
        } catch (error) {
            console.error('Error clearing chat history:', error);
            alert('Une erreur est survenue lors de l\'effacement de l\'historique.');
        }
    }

    // --- Event Listeners ---
    if(chatbotIcon) chatbotIcon.addEventListener('click', toggleChatbot);
    if(closeChatbotBtn) closeChatbotBtn.addEventListener('click', toggleChatbot);
    if(clearChatBtn) clearChatBtn.addEventListener('click', clearChatHistory);
    if(sendMessageBtn) sendMessageBtn.addEventListener('click', sendMessage);
    if(chatbotInputField) chatbotInputField.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendMessage();
    });

    if(chatbotMessages) chatbotMessages.addEventListener('click', function(e) {
        const optionsBtn = e.target.closest('.options-btn');
        const deleteLink = e.target.closest('.delete-link');

        if (optionsBtn) {
            const menu = optionsBtn.nextElementSibling;
            document.querySelectorAll('.options-menu').forEach(m => {
                if (m !== menu) m.style.display = 'none';
            });
            menu.style.display = menu.style.display === 'block' ? 'none' : 'block';
            return;
        }

        if (deleteLink) {
            e.preventDefault();
            const messageBubble = e.target.closest('.message-bubble');
            const messageId = messageBubble.dataset.messageId;
            if (confirm('Êtes-vous sûr de vouloir supprimer ce message ?')) {
                deleteMessage(messageId, messageBubble);
            }
        }
    });

    document.addEventListener('click', function(e) {
        if (!e.target.closest('.message-options')) {
            document.querySelectorAll('.options-menu').forEach(m => m.style.display = 'none');
        }
    });

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