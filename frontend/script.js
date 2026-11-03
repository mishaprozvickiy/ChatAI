const GREETING_MESSAGE = 'Привет! Чем могу помочь?';

const isLocalhost = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
let BASE_URL;

if (isLocalhost) {
    BASE_URL = 'http://localhost:8001';
} else {
    BASE_URL = `${window.location.protocol}//${window.location.hostname}:8001`;
}

const chatBox = document.getElementById('chatBox');
const input = document.getElementById('messageInput');
const sendBtn = document.getElementById('sendBtn');
const authPanel = document.getElementById('authPanel');

let isLoggedIn = false;
let username = '';
let isEditing = false;
let isProcessing = false;

const esc = t => t ? t.replace(/[&<>"']/g, m => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[m])) : '';
const scroll = () => chatBox.scrollTop = chatBox.scrollHeight;

const fmtDate = iso => {
    if (!iso) return '';
    let safeIso = iso;
    if (!iso.includes('Z') && !iso.includes('+') && !iso.includes('-', 10)) {
        safeIso = iso + 'Z';
    }
    const d = new Date(safeIso);
    if (isNaN(d.getTime())) return '';
    return d.toLocaleString('ru-RU', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    }).replace(',', '');
};

const fetchWithRetry = async (url, opts = {}) => {
    let res = await fetch(`${BASE_URL}${url}`, { credentials: 'include', ...opts });
    if (res.status === 401) {
        try {
            const refreshRes = await fetch(`${BASE_URL}/auth/refresh`, { method: 'POST', credentials: 'include' });
            if (refreshRes.ok) {
                return await fetch(`${BASE_URL}${url}`, { credentials: 'include', ...opts });
            } else {
                handleLogout(false);
                throw new Error('Сессия истекла');
            }
        } catch {
            handleLogout(false);
            throw new Error('Не авторизован');
        }
    }
    return res;
};

const apiCall = async (url, opts = {}) => {
    const res = await fetchWithRetry(url, opts);
    if (!res.ok) throw new Error((await res.json().catch(() => ({}))).detail || 'Ошибка');
    return res.json();
};

const renderAuthPanel = () => {
    if (isLoggedIn) {
        authPanel.innerHTML = `<span style="font-weight:500;margin-right:8px;">${esc(username)}</span><button id="logoutBtn" class="btn-secondary">Выйти</button>`;
        document.getElementById('logoutBtn').onclick = handleLogout;
        enableChat(true);
    } else {
        authPanel.innerHTML = `<button onclick="window.location.href='auth.html?mode=login'" class="btn-secondary">Войти</button><button onclick="window.location.href='auth.html?mode=register'" class="btn-primary">Создать аккаунт</button>`;
        enableChat(false);
    }
};

const enableChat = (on) => {
    input.disabled = !on || isEditing || isProcessing;
    sendBtn.disabled = !on || isEditing || isProcessing;
    input.placeholder = on ? 'Введите сообщение...' : 'Войдите, чтобы начать чат...';
};

const resetEditState = () => {
    isEditing = false;
    isProcessing = false;
    if (isLoggedIn) {
        input.disabled = false;
        sendBtn.disabled = false;
        input.focus();
    }
    document.querySelectorAll('.edit-controls').forEach(el => el.remove());
    setupLastUserMessageEdit();
};

const handleLogout = async (notify = true) => {
    try { await fetch(`${BASE_URL}/auth/logout`, { method: 'POST', credentials: 'include' }); } catch {}
    isLoggedIn = false;
    username = '';
    chatBox.innerHTML = '';
    renderAuthPanel();
    if (notify) alert('Вы вышли из аккаунта');
};

const checkSession = async () => {
    try {
        const data = await apiCall('/auth/me');
        isLoggedIn = true;
        username = data.username;
        loadHistory();
    } catch {
        isLoggedIn = false;
        username = '';
    }
    renderAuthPanel();
};

const appendMsg = (role, text, dateStr = null, isStreaming = false) => {
    const div = document.createElement('div');
    div.className = `message ${role}`;
    const dt = dateStr ? fmtDate(dateStr) : '';
    let html = isStreaming && !text ? `<div class="typing-indicator"><div class="typing-dot"></div><div class="typing-dot"></div><div class="typing-dot"></div></div>` : esc(text);
    div.innerHTML = `<div class="meta"><span>${role==='user'?'Вы':'ChatAI'}</span>${dt ? `<span class="datetime">${dt}</span>` : ''}</div><div class="content">${html}</div>`;
    chatBox.appendChild(div);
    scroll();
    return div.querySelector('.content');
};

const loadHistory = async () => {
    try {
        const res = await fetch(`${BASE_URL}/api/history`, { credentials: 'include' });
        if (!res.ok) throw new Error();
        const hist = await res.json();
        chatBox.innerHTML = '';
        appendMsg('assistant', GREETING_MESSAGE, null);
        hist.forEach(m => appendMsg(m.role, m.content, m.date));
        setupLastUserMessageEdit();
    } catch {
        chatBox.innerHTML = '';
        appendMsg('assistant', GREETING_MESSAGE, null);
    }
};

const sendMessage = async () => {
    if (!isLoggedIn || isEditing || isProcessing) return;
    isProcessing = true;
    document.querySelectorAll('.edit-btn').forEach(btn => btn.remove());
    enableChat(false);

    const text = input.value.trim();
    if (!text) {
        isProcessing = false;
        enableChat(true);
        return;
    }

    input.value = '';
    appendMsg('user', text, new Date().toISOString());

    const aiEl = appendMsg('assistant', '', null, true);
    let full = '', msgDate = null, first = true;

    try {
        let res = await fetch(`${BASE_URL}/api/chat`, {
            credentials: 'include', method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ content: text })
        });

        if (res.status === 401) {
            await fetchWithRetry('/auth/refresh', { method: 'POST' });
            return sendMessage();
        }
        if (!res.ok) throw new Error((await res.json().catch(() => ({}))).detail || 'Network error');

        const reader = res.body.getReader();
        const dec = new TextDecoder();
        while (true) {
            const { done, value } = await reader.read();
            if (done) break;
            const chunk = dec.decode(value, { stream: true });
            const m = chunk.match(/\[DATE:(.+?)\]/);
            let txt = chunk;
            if (m) { msgDate = m[1]; txt = chunk.replace(/\[DATE:.+?\]/, ''); }
            if (txt) {
                if (first) { aiEl.innerHTML = ''; first = false; }
                full += txt;
                aiEl.textContent = full;
                scroll();
            }
        }
        if (msgDate) {
            const last = chatBox.querySelector('.message.assistant:last-child');
            if (last && !last.querySelector('.datetime')) {
                const s = document.createElement('span');
                s.className = 'datetime'; s.textContent = fmtDate(msgDate);
                last.querySelector('.meta').appendChild(s);
            }
        }
    } catch (e) {
        aiEl.innerHTML = `<span style="color:#dc2626">Ошибка: ${e.message}</span>`;
    } finally {
        resetEditState();
    }
};

const setupLastUserMessageEdit = () => {
    if (isProcessing) return;

    document.querySelectorAll('.edit-btn').forEach(btn => btn.remove());
    document.querySelectorAll('.edit-controls').forEach(el => el.remove());

    const userMessages = chatBox.querySelectorAll('.message.user');
    if (userMessages.length === 0) return;

    const lastUserMsg = userMessages[userMessages.length - 1];

    const editBtn = document.createElement('div');
    editBtn.className = 'edit-btn';
    editBtn.title = 'Редактировать';
    editBtn.onclick = () => enableInlineEdit(lastUserMsg);
    lastUserMsg.appendChild(editBtn);
};

const enableInlineEdit = (msgDiv) => {
    if (isEditing || isProcessing) return;

    const contentDiv = msgDiv.querySelector('.content');
    if (!contentDiv) return;

    isEditing = true;
    isProcessing = true;
    document.querySelectorAll('.edit-btn').forEach(btn => btn.remove());
    enableChat(false);

    const originalText = contentDiv.textContent;
    const editBtn = msgDiv.querySelector('.edit-btn');

    msgDiv.dataset.originalText = originalText;
    contentDiv.innerHTML = '';

    const textarea = document.createElement('textarea');
    textarea.className = 'inline-textarea';
    textarea.value = originalText;
    contentDiv.appendChild(textarea);

    setTimeout(() => {
        textarea.focus();
        textarea.select();
    }, 0);

    if (editBtn) editBtn.style.display = 'none';

    const controls = document.createElement('div');
    controls.className = 'edit-controls';

    const cancelBtn = document.createElement('button');
    cancelBtn.className = 'btn-cancel';
    cancelBtn.textContent = 'Отменить';
    cancelBtn.onclick = () => {
        contentDiv.textContent = originalText;
        controls.remove();
        if (editBtn) editBtn.style.display = 'block';
        delete msgDiv.dataset.originalText;
        resetEditState();
    };

    const sendEditBtn = document.createElement('button');
    sendEditBtn.className = 'btn-primary';
    sendEditBtn.textContent = 'Отправить';
    sendEditBtn.onclick = () => {
        submitEdit(msgDiv, textarea.value, originalText);
    };

    controls.appendChild(cancelBtn);
    controls.appendChild(sendEditBtn);
    msgDiv.appendChild(controls);
};

const submitEdit = async (msgDiv, newText, originalText) => {
    if (!newText.trim()) return;

    const contentDiv = msgDiv.querySelector('.content');
    const controls = msgDiv.querySelector('.edit-controls');

    if (controls) {
        controls.remove();
    }

    try {
        const res = await fetch(`${BASE_URL}/api/update`, {
            credentials: 'include',
            method: 'PATCH',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ content: newText })
        });

        if (!res.ok) {
            const err = await res.json().catch(() => ({}));
            throw new Error(err.detail || 'Network error');
        }

        if (contentDiv) {
            contentDiv.textContent = newText;
        }

        let nextEl = msgDiv.nextElementSibling;
        if (nextEl && nextEl.classList.contains('message') && nextEl.classList.contains('assistant')) {
            nextEl.remove();
        }

        const aiEl = appendMsg('assistant', '', null, true);
        const reader = res.body.getReader();
        const dec = new TextDecoder();
        let full = '', msgDate = null, first = true;

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;
            const chunk = dec.decode(value, { stream: true });
            const m = chunk.match(/\[DATE:(.+?)\]/);
            let txt = chunk;
            if (m) { msgDate = m[1]; txt = chunk.replace(/\[DATE:.+?\]/, ''); }
            if (txt) {
                if (first) { aiEl.innerHTML = ''; first = false; }
                full += txt;
                aiEl.textContent = full;
                scroll();
            }
        }

        if (msgDate) {
            const last = chatBox.querySelector('.message.assistant:last-child');
            if (last && !last.querySelector('.datetime')) {
                const s = document.createElement('span');
                s.className = 'datetime';
                s.textContent = fmtDate(msgDate);
                if (last.querySelector('.meta')) {
                    last.querySelector('.meta').appendChild(s);
                }
            }
        }

        resetEditState();

    } catch (e) {
        alert('Ошибка при редактировании: ' + e.message);
        if (contentDiv) {
            contentDiv.textContent = originalText;
        }
        resetEditState();
    }
};

if (sendBtn) sendBtn.onclick = sendMessage;
if (input) {
    input.onkeydown = e => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    };
}

checkSession();