const API_BASE = 'http://localhost:8001/api';

const chatBox = document.getElementById('chatBox');
const input = document.getElementById('messageInput');
const sendBtn = document.getElementById('sendBtn');
const clearBtn = document.getElementById('clearBtn');

const escapeHtml = (text) =>
    text.replace(/[&<>"']/g, m => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[m]));

const scrollToBottom = () => {
    chatBox.scrollTop = chatBox.scrollHeight;
};

const appendMessage = (role, text, isStreaming = false) => {
    const div = document.createElement('div');
    div.className = `message ${role}`;
    div.innerHTML = `
        <div class="meta">${role === 'user' ? 'Вы' : 'ChatAI'}</div>
        <div class="content${isStreaming ? ' typing' : ''}">${escapeHtml(text)}</div>
    `;
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
        if (history.length === 0) {
            appendMessage('ai', 'Здравствуйте. Я готов к работе.');
        } else {
            history.forEach(msg => appendMessage(msg.role, msg.message));
        }
    } catch {
        chatBox.innerHTML = '';
        appendMessage('ai', 'Здравствуйте. Я готов к работе.');
    }
};

const sendMessage = async () => {
    const text = input.value.trim();
    if (!text) return;

    input.value = '';
    appendMessage('user', text);
    input.disabled = true;
    sendBtn.disabled = true;

    const aiContent = appendMessage('ai', '', true);
    let fullReply = '';

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
            fullReply += chunk;
            aiContent.textContent = fullReply;
            scrollToBottom();
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
        appendMessage('ai', 'Здравствуйте. Я готов к работе.');
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