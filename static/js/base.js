/**
 * Global JavaScript file for base.html.
 * Handles primary functionalities like active navigation link highlighting and authentication state.
 */

// Normalizes the path by ensuring it's either '/' or '/path' without a trailing slash.
function normalizePath(path) {
    if (path === '/') {
        return '/';
    }
    // Remove trailing slash if present
    const cleanPath = path.replace(/\/+$/, '');
    // If cleaning results in an empty string (e.g., if path was just '/'), return '/'
    return cleanPath === '' ? '/' : cleanPath;
}

// Function to correctly determine the active link in the navigation menu.
function highlightActiveLink() {
    // Get and normalize the current browser path
    const currentPath = normalizePath(window.location.pathname);
    const navLinks = document.querySelectorAll('header .nav-link');

    navLinks.forEach(link => {
        // Get and normalize the link path from the href attribute
        const linkPath = normalizePath(link.getAttribute('href'));

        // Remove active class from all links first
        link.classList.remove('nav-link-active');

        // Check for direct path match
        if (linkPath === currentPath) {
            link.classList.add('nav-link-active');
        }
        // Handle special cases where sub-pages should highlight a parent link
        else if (currentPath.startsWith('/appointment') && linkPath === '/catalog') {
            // Appointment page should highlight "Services" (/catalog)
            link.classList.add('nav-link-active');
        }
        else if ((currentPath.startsWith('/reg') || currentPath.startsWith('/auth') || currentPath.startsWith('/profile')) && linkPath === '/profile') {
            // Registration, Authorization, and Profile pages should highlight "Profile"
            link.classList.add('nav-link-active');
        }
    });
}

// --- ФУНКЦИИ АУТЕНТИФИКАЦИИ ---

// Читает значение куки по имени
function getCookie(name) {
    const nameEQ = name + "=";
    const ca = document.cookie.split(';');
    for(let i = 0; i < ca.length; i++) {
        let c = ca[i];
        while (c.charAt(0) === ' ') c = c.substring(1, c.length);
        if (c.indexOf(nameEQ) === 0) return c.substring(nameEQ.length, c.length);
    }
    return null;
}

// Удаляет куку (устанавливает срок годности в прошлом)
function deleteCookie(name) {
    document.cookie = name + '=; Max-Age=-99999999; path=/;';
}

// Управляет видимостью кнопок Войти/Регистрация/Выйти
function updateAuthButtons() {
    const login = getCookie('user_login');
    const authButtons = document.getElementById('auth-buttons');
    const logoutButtonContainer = document.getElementById('logout-button');
    const profileLink = document.getElementById('nav-profile-link');

    if (login) {
        // Пользователь авторизован
        if (authButtons) authButtons.classList.add('d-none');
        if (logoutButtonContainer) logoutButtonContainer.classList.remove('d-none');
        if (profileLink) profileLink.classList.remove('d-none'); // Показываем "Профиль"
    } else {
        // Пользователь не авторизован
        if (authButtons) authButtons.classList.remove('d-none');
        if (logoutButtonContainer) logoutButtonContainer.classList.add('d-none');
        if (profileLink) profileLink.classList.add('d-none'); // Скрываем "Профиль"
    }
}

// Обработчик выхода
function handleLogout() {
    const logoutBtn = document.getElementById('logout-btn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', () => {
            // Удаляем куку авторизации
            deleteCookie('user_login');
            // Перенаправляем на главную страницу
            window.location.href = '/';
        });
    }
}

document.addEventListener('DOMContentLoaded', function() {
    highlightActiveLink();
    updateAuthButtons(); // Проверяем состояние авторизации при загрузке
    handleLogout();      // Устанавливаем обработчик для кнопки "Выйти"
});
