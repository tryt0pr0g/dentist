document.addEventListener("DOMContentLoaded", function() {

    // Функция для чтения куки (используется для проверки авторизации)
    function getCookie(name) {
        const nameEQ = name + "=";
        const ca = document.cookie.split(';');
        for(let i = 0; i < ca.length; i++) {
            let c = ca[i];
            while (c.charAt(0) === ' ') c = c.substring(1, c.length);
            // Возвращаем значение, если кука найдена
            if (c.indexOf(nameEQ) === 0) {
                // Дополнительная проверка, что значение не пустое
                const value = c.substring(nameEQ.length, c.length);
                return value.trim() !== '' ? value : null;
            }
        }
        return null;
    }

    // Проверка статуса авторизации: true, если кука 'user_login' существует и не пуста
    const userLoginCookie = getCookie('user_login');
    const isUserLoggedIn = userLoginCookie !== null;

    // --- ДЕБАГ: Проверяем статус авторизации при загрузке страницы ---
    console.log(`[Catalog] Статус авторизации: ${isUserLoggedIn}. Значение куки: ${userLoginCookie}`);
    // -----------------------------------------------------------------

    // Получаем все кнопки "Записаться"
    const bookingButtons = document.querySelectorAll('.action-booking');
    // Получаем все кнопки "Авторизоваться"
    const authButtons = document.querySelectorAll('.action-auth');

    // --- ДЕБАГ: Проверка, что элементы найдены ---
    console.log(`[Catalog] Найдено кнопок Записаться: ${bookingButtons.length}`);
    console.log(`[Catalog] Найдено кнопок Авторизоваться: ${authButtons.length}`);
    // ----------------------------------------------

    if (isUserLoggedIn) {
        // Если авторизован: показываем кнопки "Записаться", скрываем "Авторизуйтесь"
        console.log("[Catalog] Пользователь авторизован. Отображаем кнопки записи.");
        bookingButtons.forEach(button => {
            button.classList.remove('d-none'); // <--- СНИМАЕМ d-none, чтобы показать
        });
        authButtons.forEach(button => {
            button.classList.add('d-none'); // <--- СКРЫВАЕМ кнопку авторизации
        });
    } else {
        // Если не авторизован: показываем кнопки "Авторизуйтесь", скрываем "Записаться"
        console.log("[Catalog] Пользователь не авторизован. Отображаем кнопки авторизации.");
        bookingButtons.forEach(button => {
            button.classList.add('d-none'); // <--- СКРЫВАЕМ кнопку записи
        });
        authButtons.forEach(button => {
            button.classList.remove('d-none'); // <--- ПОКАЗЫВАЕМ кнопку авторизации
        });
    }
});
