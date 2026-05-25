const API_URL = 'http://localhost:8000/api';

const chatMessages = document.getElementById('chat-messages');
const chatForm = document.getElementById('chat-form');
const messageInput = document.getElementById('message-input');
const sendBtn = document.getElementById('send-btn');
const newChatBtn = document.getElementById('new-chat-btn');

let sessionId = localStorage.getItem('sessionId') || generateSessionId();
localStorage.setItem('sessionId', sessionId);

function generateSessionId() {
    return 'session_' + Math.random().toString(36).substring(2, 15);
}

function addMessage(content, sender, meta = null) {
    const msgDiv = document.createElement('div');
    msgDiv.classList.add('message', sender);
    
    const textNode = document.createElement('div');
    textNode.innerText = content;
    msgDiv.appendChild(textNode);
    
    if (meta) {
        const metaDiv = document.createElement('div');
        metaDiv.classList.add('meta-info');
        metaDiv.innerText = `Tokens: ${meta.tokensUsed} | Chunks: ${meta.retrievedChunks}`;
        msgDiv.appendChild(metaDiv);
    }
    
    const timeDiv = document.createElement('div');
    timeDiv.classList.add('meta-info');
    const now = new Date();
    timeDiv.innerText = `${now.getHours()}:${now.getMinutes().toString().padStart(2, '0')}`;
    msgDiv.appendChild(timeDiv);

    chatMessages.appendChild(msgDiv);
    scrollToBottom();
}

function addLoading() {
    const loadingDiv = document.createElement('div');
    loadingDiv.classList.add('message', 'assistant', 'loading-msg');
    loadingDiv.innerHTML = `
        <div class="loading">
            <div class="dot"></div>
            <div class="dot"></div>
            <div class="dot"></div>
        </div>
    `;
    chatMessages.appendChild(loadingDiv);
    scrollToBottom();
    return loadingDiv;
}

function scrollToBottom() {
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

chatForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const message = messageInput.value.trim();
    if (!message) return;

    addMessage(message, 'user');
    messageInput.value = '';
    sendBtn.disabled = true;
    
    const loadingElement = addLoading();

    try {
        const response = await fetch(`${API_URL}/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                sessionId: sessionId,
                message: message
            })
        });

        const data = await response.json();
        loadingElement.remove();

        if (response.ok) {
            addMessage(data.reply, 'assistant', {
                tokensUsed: data.tokensUsed,
                retrievedChunks: data.retrievedChunks
            });
        } else {
            addMessage("Sorry, I encountered an error. Please try again.", 'assistant');
        }
    } catch (error) {
        loadingElement.remove();
        addMessage("Failed to connect to the server.", 'assistant');
    } finally {
        sendBtn.disabled = false;
        messageInput.focus();
    }
});

newChatBtn.addEventListener('click', () => {
    sessionId = generateSessionId();
    localStorage.setItem('sessionId', sessionId);
    chatMessages.innerHTML = '';
    addMessage("Hello! I'm your AI support assistant. How can I help you today?", 'assistant');
});

// Initial greeting
if (chatMessages.children.length === 0) {
    addMessage("Hello! I'm your AI support assistant. How can I help you today?", 'assistant');
}
