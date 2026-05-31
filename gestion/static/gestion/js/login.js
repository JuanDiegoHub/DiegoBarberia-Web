// gestion/static/gestion/js/login.js

const togglePassword = document.querySelector('.toggle-password');
const passwordInput = document.querySelector('#password');

togglePassword.addEventListener('click', function () {
    if (passwordInput.type === 'password') {
        passwordInput.type = 'text';
        this.textContent = 'visibility_off';
    } else {
        passwordInput.type = 'password';
        this.textContent = 'visibility';
    }
});