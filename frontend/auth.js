document.addEventListener('DOMContentLoaded', () => {
    const urlParams = new URLSearchParams(window.location.search);
    const mode = urlParams.get('mode') === 'register' ? 'register' : 'login';

    const titleEl = document.getElementById('authTitle');
    const submitBtn = document.getElementById('authSubmitBtn');
    const usernameInput = document.getElementById('usernameInput');
    const passwordInput = document.getElementById('passwordInput');
    const authMessage = document.getElementById('authMessage');

    titleEl.textContent = mode === 'login' ? 'Вход в аккаунт' : 'Создать аккаунт';
    submitBtn.textContent = mode === 'login' ? 'Войти' : 'Зарегистрироваться';

    submitBtn.addEventListener('click', async () => {
        const username = usernameInput.value.trim();
        const password = passwordInput.value;

        if (!username || !password) {
            authMessage.textContent = 'Заполните все поля';
            authMessage.style.color = '#dc2626';
            return;
        }

        authMessage.textContent = '';
        submitBtn.disabled = true;
        submitBtn.textContent = 'Загрузка...';

        try {
            const res = await fetch(`http://localhost:8001/auth/${mode}`, {
                method: 'POST',
                credentials: 'include',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, password })
            });

            if (!res.ok) {
                const err = await res.json().catch(() => ({}));
                throw new Error(err.detail || 'Ошибка сервера');
            }

            window.location.href = 'index.html';
        } catch (e) {
            authMessage.textContent = e.message;
            authMessage.style.color = '#dc2626';
            submitBtn.disabled = false;
            submitBtn.textContent = mode === 'login' ? 'Войти' : 'Зарегистрироваться';
        }
    });

    document.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !submitBtn.disabled) submitBtn.click();
    });
});