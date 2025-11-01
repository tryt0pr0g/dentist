/**
 * Файл логики для страницы регистрации (reg.html).
 * Отправляет данные на Ваш серверный API для регистрации.
 */

document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('registrationForm');
    const messageContainer = document.getElementById('messageContainer');
    const registerButton = form.querySelector('button[type="submit"]');

    // Хелпер для отображения сообщений
    function displayMessage(text, type) {
        messageContainer.innerHTML = `<div class="alert alert-${type} mt-3 py-2" role="alert">${text}</div>`;
    }

    // Хелпер для сохранения токена
    function saveToken(token, rememberMe) {
        // Используем localStorage, если выбрано "Запомнить меня"
        const storage = rememberMe ? localStorage : sessionStorage;
        storage.setItem('authToken', token);
    }

    // Обработчик отправки формы
    form.addEventListener('submit', async function(e) {
        e.preventDefault();

        // Блокируем кнопку на время обработки
        registerButton.disabled = true;
        displayMessage('Обработка запроса...', 'info');

        const fullName = document.getElementById('fullName').value.trim();
        const dateOfBirth = document.getElementById('dateOfBirth').value;
        const login = document.getElementById('login').value.trim();
        const password = document.getElementById('password').value;
        const rememberMe = document.getElementById('rememberMe').checked;

        if (password.length < 6) {
            displayMessage('Пароль должен быть не менее 6 символов.', 'warning');
            registerButton.disabled = false;
            return;
        }

        // Данные для отправки на Ваш сервер
        const userData = {
            fio: fullName,
            birthday: dateOfBirth,
            login: login, // Используется как email
            password: password
        };

        try {
            // 1. Отправка данных на Ваш API
            const response = await fetch('/api/register', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(userData)
            });

            const result = await response.json();

            if (response.ok) {
                // 2. Успешная регистрация
                if (result.token) {
                    saveToken(result.token, rememberMe);
                    displayMessage('Регистрация успешна! Перенаправление на услуги...', 'success');

                    // 3. Перенаправление на страницу услуг
                    setTimeout(() => {
                        window.location.href = '/catalog';
                    }, 1500);

                } else {
                    // Сервер вернул 200, но без токена
                    displayMessage('Регистрация успешна, но токен не получен. Перенаправление.', 'success');
                    setTimeout(() => {
                        window.location.href = '/catalog';
                    }, 1500);
                }
            } else {
                // 4. Ошибка сервера (например, 400 Bad Request, 409 Conflict)
                const errorDetail = result.detail || 'Неизвестная ошибка сервера.';
                displayMessage(`Ошибка: ${errorDetail}`, 'danger');
            }

        } catch (error) {
            console.error('Network or Parse Error:', error);
            displayMessage('Ошибка сети или внутренняя ошибка приложения.', 'danger');
        } finally {
            // Разблокируем кнопку
            registerButton.disabled = false;
        }
    });
});