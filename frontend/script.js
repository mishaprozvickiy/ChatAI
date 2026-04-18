const API_BASE = 'http://localhost:8001/api';

const chatBox = document.getElementById('chatBox');
const input = document.getElementById('messageInput');
const sendBtn = document.getElementById('sendBtn');
const clearBtn = document.getElementById('clearBtn');

const escapeHtml = (text) => {
    if (!text) return '';
    return text.replace(/[&<>"']/g, m => ({
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#39;'
    }[m]));
};

const scrollToBottom = () => {
    chatBox.scrollTop = chatBox.scrollHeight;
};

const formatDateTime = (isoString) => {
    if (!isoString) return '';
    const d = new Date(isoString);
    if (isNaN(d.getTime())) return '';

    const day = String(d.getDate()).padStart(2, '0');
    const month = String(d.getMonth() + 1).padStart(2, '0');
    const year = d.getFullYear();
    const hours = String(d.getHours()).padStart(2, '0');
    const minutes = String(d.getMinutes()).padStart(2, '0');

    return `${day}.${month}.${year} ${hours}:${minutes}`;
};

const appendMessage = (role, text, dateStr = null, isStreaming = false) => {
    const div = document.createElement('div');
    div.className = `message ${role}`;

    const formattedDate = dateStr ? formatDateTime(dateStr) : '';

    div.innerHTML = `
        <div class="meta">
            <span class="role-name">${role === 'user' ? 'Вы' : 'ChatAI'}</span>
            ${formattedDate ? `<span class="datetime">${formattedDate}</span>` : ''}
        </div>
        <div class="content${isStreaming ? ' typing' : ''}">${escapeHtml(text)}</div>
    `;

    if (isStreaming) div.querySelector('.content').classList.add('typing');
    chatBox.appendChild(div);
    scrollToBottom();
    return div.querySelector('.content');
};

const loadHistory = async () => {
    try {
        const res = await fetch(`${API_BASE}/history`);
        if (!res.ok) throw new Error();
        const history = await res.json();
        chatBox.innerHTML = '';
        history.forEach(msg => {
            appendMessage(msg.role, msg.message, msg.date);
        });
    } catch {
        chatBox.innerHTML = '';
        const now = new Date().toISOString();
        appendMessage('assistant', 'Ошибка загрузки истории. Попробуйте обновить страницу.', now);
    }
};

const sendMessage = async () => {
    const text = input.value.trim();
    if (!text) return;

    input.value = '';

    const now = new Date().toISOString();
    appendMessage('user', text, now);

    input.disabled = true;
    sendBtn.disabled = true;

    const aiContent = appendMessage('assistant', '', null, true);
    let fullReply = '';
    let messageDate = null;

    try {
        const res = await fetch(`${API_BASE}/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: text })
        });

        if (!res.ok) {
            const err = await res.json().catch(() => ({ error: 'Ошибка сервера' }));
            throw new Error(err.error || 'Network error');
        }

        const reader = res.body.getReader();
        const decoder = new TextDecoder();

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            const chunk = decoder.decode(value, { stream: true });

            const dateMatch = chunk.match(/\[DATE:(.+?)\]/);
            if (dateMatch) {
                messageDate = dateMatch[1];
                const cleanChunk = chunk.replace(/\[DATE:.+?\]/, '');
                fullReply += cleanChunk;
                aiContent.textContent = fullReply;
            } else {
                fullReply += chunk;
                aiContent.textContent = fullReply;
            }

            scrollToBottom();
        }

        if (messageDate) {
            const formattedDate = formatDateTime(messageDate);
            const lastAiMessage = chatBox.querySelector('.message.assistant:last-child');
            if (lastAiMessage) {
                const metaDiv = lastAiMessage.querySelector('.meta');
                if (metaDiv && !metaDiv.querySelector('.datetime')) {
                    const timeSpan = document.createElement('span');
                    timeSpan.className = 'datetime';
                    timeSpan.textContent = formattedDate;
                    metaDiv.appendChild(timeSpan);
                }
            }
        }

        aiContent.classList.remove('typing');

    } catch (err) {
        aiContent.textContent = `Ошибка: ${err.message}`;
        aiContent.style.color = '#dc2626';
    } finally {
        input.disabled = false;
        sendBtn.disabled = false;
        input.focus();
    }
};

const clearHistory = async () => {
    if (!confirm('Удалить историю диалога?')) return;
    try {
        await fetch(`${API_BASE}/clear`, { method: 'DELETE' });
        chatBox.innerHTML = '';
        await loadHistory();
    } catch {
        alert('Не удалось очистить историю');
    }
};

sendBtn.addEventListener('click', sendMessage);
clearBtn.addEventListener('click', clearHistory);
input.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

window.addEventListener('DOMContentLoaded', loadHistory);