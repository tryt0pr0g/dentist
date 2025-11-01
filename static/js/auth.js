/**
 * Handles the authentication form submission, sends credentials to the server,
 * sets the 'user_login' cookie upon success, and redirects the user.
 */

document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('authForm');
    const loginInput = document.getElementById('loginInput');
    const passwordInput = document.getElementById('passwordInput');
    const messageElement = document.getElementById('message');

    /**
     * Sets a cookie with the specified name, value, and expiration days.
     * @param {string} name - The name of the cookie.
     * @param {string} value - The value to store.
     * @param {number} days - Number of days until expiration.
     */
    function setCookie(name, value, days) {
        let expires = "";
        if (days) {
            const date = new Date();
            date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
            expires = "; expires=" + date.toUTCString();
        }
        document.cookie = name + "=" + (value || "")  + expires + "; path=/";
    }

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        messageElement.textContent = '';

        const login = loginInput.value.trim();
        const password = passwordInput.value;

        if (!login || !password) {
            messageElement.textContent = 'Заполните все поля.';
            messageElement.style.color = 'red';
            return;
        }

        const authData = {
            login: login,
            password: password
        };

        try {
            messageElement.textContent = 'Выполняется вход...';
            messageElement.style.color = 'gray';

            // Предполагаем, что API для авторизации находится по адресу /api/auth
            const response = await fetch('/api/auth', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(authData)
            });

            const result = await response.json();

            if (response.ok) {
                // Успешная авторизация. Устанавливаем куку с логином.
                // Кука будет храниться 7 дней.
                setCookie('user_login', login, 7);

                messageElement.textContent = 'Вход выполнен успешно! Перенаправление...';
                messageElement.style.color = 'green';

                // Перенаправление на главную страницу
                window.location.href = '/';
            } else {
                // Ошибка авторизации (401 Unauthorized, 400 Bad Request)
                const errorMessage = result.detail || 'Неизвестная ошибка авторизации.';
                messageElement.textContent = `Ошибка: ${errorMessage}`;
                messageElement.style.color = 'red';
                console.error('Ошибка сервера:', response.status, result);
            }

        } catch (error) {
            messageElement.textContent = 'Сетевая ошибка. Проверьте соединение.';
            messageElement.style.color = 'red';
            console.error('Сетевая ошибка:', error);
        }
    });
});
