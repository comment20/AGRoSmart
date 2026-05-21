document.addEventListener('DOMContentLoaded', () => {
    const toSignup = document.getElementById('to-signup');
    const toLogin = document.getElementById('to-login');
    const loginContainer = document.getElementById('login-container');
    const signupContainer = document.getElementById('signup-container');

    // Vérifier s'il y a des erreurs dans le formulaire d'inscription pour l'afficher par défaut
    const signupHasErrors = signupContainer.querySelector('.error-text, .form-errors');
    if (signupHasErrors) {
        showSignup();
    }

    toSignup.addEventListener('click', (e) => {
        e.preventDefault();
        showSignup();
    });

    toLogin.addEventListener('click', (e) => {
        e.preventDefault();
        showLogin();
    });

    function showSignup() {
        loginContainer.classList.remove('active');
        setTimeout(() => {
            signupContainer.classList.add('active');
        }, 50);
    }

    function showLogin() {
        signupContainer.classList.remove('active');
        setTimeout(() => {
            loginContainer.classList.add('active');
        }, 50);
    }

    // --- Fonctionnalité Afficher/Masquer le mot de passe ---
    function setupPasswordToggle(toggleId, inputSelector) {
        const toggle = document.getElementById(toggleId);
        if (toggle) {
            toggle.addEventListener('click', function() {
                const input = toggle.parentElement.querySelector('input');
                const type = input.getAttribute('type') === 'password' ? 'text' : 'password';
                input.setAttribute('type', type);

                // Basculer l'icône
                this.classList.toggle('fa-eye');
                this.classList.toggle('fa-eye-slash');
            });
        }
    }

    setupPasswordToggle('toggleLoginPassword');
    setupPasswordToggle('toggleSignupPassword1');
    setupPasswordToggle('toggleSignupPassword2');
    });