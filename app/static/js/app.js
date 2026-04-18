// Показ уведомлений
function showNotification(message, type = 'success') {
    const notification = document.getElementById('notification');
    notification.textContent = message;
    notification.className = `notification ${type} show`;
    
    setTimeout(() => {
        notification.classList.remove('show');
    }, 3000);
}

// Выход из системы
function logout() {
    localStorage.removeItem('token');
    localStorage.removeItem('user_email');
    localStorage.removeItem('user_role');
    showNotification('Вы вышли из системы', 'success');
    setTimeout(() => {
        window.location.href = '/login';
    }, 1000);
}

// Проверка токена
function getToken() {
    return localStorage.getItem('token');
}

// Проверка авторизации
function requireAuth() {
    const token = getToken();
    if (!token) {
        window.location.href = '/login';
        return false;
    }
    return true;
}

// API запрос с авторизацией
async function apiRequest(url, options = {}) {
    const token = getToken();
    
    const config = {
        ...options,
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`,
            ...options.headers
        }
    };
    
    try {
        const response = await fetch(url, config);
        
        if (response.status === 401) {
            logout();
            return null;
        }
        
        return await response.json();
    } catch (error) {
        showNotification('Ошибка подключения к серверу', 'error');
        return null;
    }
}

// Форматирование даты
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('ru-RU', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Экспорт для использования в других скриптах
window.utils = {
    showNotification,
    logout,
    getToken,
    requireAuth,
    apiRequest,
    formatDate
};