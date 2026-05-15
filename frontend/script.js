const API = 'http://localhost:8001';
const chatBox = document.getElementById('chatBox');
const input = document.getElementById('messageInput');
const sendBtn = document.getElementById('sendBtn');
const authPanel = document.getElementById('authPanel');

let isLoggedIn = false;
let username = '';

const esc = t => t ? t.replace(/[&<>"']/g, m => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[m])) : '';
const scroll = () => chatBox.scrollTop = chatBox.scrollHeight;
const fmtDate = iso => {
    if (!iso) return '';
    const d = new Date(iso);
    return isNaN(d) ? '' : `${String(d.getDate()).padStart(2,'0')}.${String(d.getMonth()+1).padStart(2,'0')}.${d.getFullYear()} ${String(d.getHours()).padStart(2,'0')}:${String(d.getMinutes()).padStart(2,'0')}`;
};

const fetchWithRetry = async (url, opts = {}) => {
    let res = await fetch(`${API}${url}`, { credentials: 'include', ...opts });

    if (res.status === 401) {
        try {
            const refreshRes = await fetch(`${API}/auth/refresh`, { method: 'POST', credentials: 'include' });
            if (refreshRes.ok) {
                return await fetch(`${API}${url}`, { credentials: 'include', ...opts });
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
        authPanel.innerHTML = `
            <span style="font-weight:500;margin-right:8px;">${esc(username)}</span>
            <button id="logoutBtn" class="btn-secondary">Выйти</button>
        `;
        document.getElementById('logoutBtn').onclick = handleLogout;
        enableChat(true);
    } else {
        authPanel.innerHTML = `
            <button onclick="window.location.href='auth.html?mode=login'" class="btn-secondary">Войти</button>
            <button onclick="window.location.href='auth.html?mode=register'" class="btn-primary">Создать аккаунт</button>
        `;
        enableChat(false);
    }
};

const enableChat = (on) => {
    input.disabled = !on;
    sendBtn.disabled = !on;
    input.placeholder = on ? 'Введите сообщение...' : 'Войдите, чтобы начать чат...';
};

const handleLogout = async (notify = true) => {
    try { await fetch(`${API}/auth/logout`, { method: 'POST', credentials: 'include' }); } catch {}
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
    let html = '';
    if (isStreaming && !text) {
        html = `<div class="typing-indicator"><div class="typing-dot"></div><div class="typing-dot"></div><div class="typing-dot"></div></div>`;
    } else {
        html = esc(text);
    }
    div.innerHTML = `<div class="meta"><span>${role==='user'?'Вы':'ChatAI'}</span>${dt?`<span class="datetime">${dt}</span>`:''}</div><div class="content">${html}</div>`;
    chatBox.appendChild(div);
    scroll();
    return div.querySelector('.content');
};

const loadHistory = async () => {
    try {
        const hist = await apiCall('/api/history');
        chatBox.innerHTML = '';
        hist.forEach(m => appendMsg(m.role, m.message, m.date));
    } catch {
        chatBox.innerHTML = '';
        appendMsg('assistant', 'Не удалось загрузить историю.', new Date().toISOString());
    }
};

const sendMessage = async () => {
    if (!isLoggedIn) return;
    const text = input.value.trim();
    if (!text) return;

    input.value = '';
    appendMsg('user', text, new Date().toISOString());
    input.disabled = true; sendBtn.disabled = true;

    const aiEl = appendMsg('assistant', '', null, true);
    let full = '', msgDate = null, first = true;

    try {
        let res = await fetch(`${API}/api/chat`, {
            credentials: 'include', method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: text })
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
        input.disabled = false; sendBtn.disabled = false; input.focus();
    }
};

sendBtn.onclick = sendMessage;
input.onkeydown = e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(); } };

checkSession();