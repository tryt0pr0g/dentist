document.addEventListener('DOMContentLoaded', () => {
    const dateInput = document.getElementById('date-input');
    const timeInput = document.getElementById('time-input');
    const form = document.getElementById('appointmentForm');
    const messageElement = document.getElementById('message');
    const serviceIdInput = document.getElementById('service-id-input');

    // --- 1. Ограничения Даты (Со следующего дня) ---
    function setDateLimits() {
        const today = new Date();
        const tomorrow = new Date(today);
        tomorrow.setDate(today.getDate() + 1);

        const yyyy = tomorrow.getFullYear();
        const mm = String(tomorrow.getMonth() + 1).padStart(2, '0');
        const dd = String(tomorrow.getDate()).padStart(2, '0');

        const minDate = `${yyyy}-${mm}-${dd}`;
        dateInput.setAttribute('min', minDate);
    }

    // --- 2. Ограничения Времени (с 9:00 до 17:00) ---
    timeInput.setAttribute('min', '09:00');
    timeInput.setAttribute('max', '17:00');

    // --- ДОБАВЛЕНО: Принудительное обнуление минут при изменении ---
    timeInput.addEventListener('change', () => {
        const selectedTimeStr = timeInput.value;
        if (selectedTimeStr) {
            // Разделяем строку на часы и минуты
            const parts = selectedTimeStr.split(':');
            let hour = parts[0];

            // Если формат правильный (ЧЧ:ММ), принудительно устанавливаем минуты в '00'
            if (parts.length === 2) {
                // Дополнительная проверка на диапазон часов
                const hourNum = parseInt(hour);

                if (hourNum < 9) {
                    hour = '09';
                } else if (hourNum > 17) {
                    hour = '17';
                } else {
                    // Убеждаемся, что час имеет две цифры
                    hour = String(hourNum).padStart(2, '0');
                }

                timeInput.value = `${hour}:00`;
            } else {
                // Если формат невалиден, сбрасываем или устанавливаем на минимальное значение
                timeInput.value = '09:00';
            }
        }
    });
    // -----------------------------------------------------------------


    // --- 3. Отправка формы ---
    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        // Сброс сообщений
        messageElement.textContent = '';

        // 3.1. КЛИЕНТСКАЯ ВАЛИДАЦИЯ ВРЕМЕНИ И ДИАПАЗОНА
        const selectedTimeStr = timeInput.value;

        // Проверка формата времени (ЧЧ:ММ)
        if (!/^\d{2}:\d{2}$/.test(selectedTimeStr)) {
            messageElement.textContent = 'Ошибка времени: Неверный формат (ожидается ЧЧ:ММ).';
            messageElement.style.color = 'red';
            return;
        }

        const [hour, minute] = selectedTimeStr.split(':').map(Number);

        // Проверка на целые часы
        if (minute !== 0) {
            messageElement.textContent = 'Ошибка времени: Выбирайте только целые часы (например, 10:00, 15:00).';
            messageElement.style.color = 'red';
            return;
        }

        // Проверка диапазона (с 9 до 17 включительно)
        if (hour < 9 || hour > 17) {
            messageElement.textContent = 'Ошибка времени: Прием ведется с 9:00 до 17:00.';
            messageElement.style.color = 'red';
            return;
        }

        // 3.2. УЛУЧШЕННАЯ ПРОВЕРКА service_id (Для предотвращения ошибок внешнего ключа)
        const serviceId = parseInt(serviceIdInput.value);
        if (isNaN(serviceId) || serviceId <= 0) {
            messageElement.textContent = 'Ошибка: Не удалось определить выбранную услугу. Пожалуйста, вернитесь в каталог.';
            messageElement.style.color = 'red';
            console.error('Ошибка Service ID:', serviceIdInput.value);
            return;
        }

        // Если все проверки пройдены:
        messageElement.textContent = 'Отправка данных...';
        messageElement.style.color = 'gray';

        const appointmentData = {
            selected_date: dateInput.value,
            selected_time: selectedTimeStr + ':00', // Добавляем секунды для соответствия Pydantic
            service_id: serviceId // Используем проверенное числовое значение
        };

        try {
            const response = await fetch('/api/appointment', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(appointmentData)
            });

            const result = await response.json();

            if (response.ok) {
                messageElement.textContent = `Запись успешно создана! ID: ${result.appointment_id}.`;
                messageElement.style.color = 'green';
                form.reset();
            } else {
                // Серверная ошибка (500, 400 и т.д.)
                console.error('Сервер ответил ошибкой:', response.status, result);
                messageElement.textContent = `Ошибка сервера (${response.status}): ${result.detail || 'Внутренняя ошибка сервера. Проверьте консоль.'}`;
                messageElement.style.color = 'red';
            }
        } catch (error) {
            console.error('Сетевая ошибка:', error);
            messageElement.textContent = 'Сетевая ошибка. Попробуйте снова.';
            messageElement.style.color = 'red';
        }
    });

    setDateLimits();
});
