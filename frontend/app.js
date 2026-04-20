// Config
const RASA_URL = 'http://localhost:5005/webhooks/rest/webhook';
let sender_id = 'usuario_' + Math.random().toString(36).substring(7); // ID unico por sesion

// DOM Elements
const chatHistory = document.getElementById('chat-history');
const userInput = document.getElementById('user-input');
const sendBtn = document.getElementById('send-btn');
const themeToggle = document.getElementById('theme-toggle');

// Theme Management
let isLightMode = false;
themeToggle.addEventListener('click', () => {
    isLightMode = !isLightMode;
    document.body.setAttribute('data-theme', isLightMode ? 'light' : 'dark');
    themeToggle.innerHTML = isLightMode ? '<i class="uil uil-sun"></i>' : '<i class="uil uil-moon"></i>';
});

// Auto-Greeting on load
window.addEventListener('load', () => {
    sendBotRequest("hola"); // Inicia la comunicacion oculta para disparar utter_greet
});

// Sends User Message
sendBtn.addEventListener('click', handleUserMessage);
userInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') handleUserMessage();
});

function handleUserMessage() {
    const text = userInput.value.trim();
    if (text === '') return;

    appendMessage(text, 'user');
    userInput.value = '';
    
    sendBotRequest(text);
}

// Render Messages
function appendMessage(text, sender) {
    const msgDiv = document.createElement('div');
    msgDiv.classList.add('message', sender === 'user' ? 'msg-user' : 'msg-bot');
    
    const bubble = document.createElement('div');
    bubble.classList.add('msg-bubble');
    // Convert newlines to breaks
    bubble.innerHTML = text.replace(/\n/g, '<br>');
    
    msgDiv.appendChild(bubble);
    chatHistory.appendChild(msgDiv);
    
    scrollToBottom();
}

const stickyButtonsContainer = document.getElementById('sticky-buttons');

function appendButtons(buttons) {
    stickyButtonsContainer.innerHTML = ''; // Limpiamos para poner los nuevos botones
    
    buttons.forEach(btn => {
        const button = document.createElement('button');
        button.classList.add('action-btn');
        button.innerText = btn.title;
        button.addEventListener('click', () => {
            appendMessage(btn.title, 'user');
            sendBotRequest(btn.payload);
            // Ya no deshabilitamos los botones para que puedan volver a usarlos
        });
        stickyButtonsContainer.appendChild(button);
    });
}

// Rasa API Comm
async function sendBotRequest(messageText) {
    showTypingIndicator();
    
    try {
        const response = await fetch(RASA_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                sender: sender_id,
                message: messageText
            })
        });

        const data = await response.json();
        removeTypingIndicator();
        
        if (data && data.length > 0) {
            for (let botMsg of data) {
                // Add tiny delay for realism
                await new Promise(r => setTimeout(r, 400));
                
                if (botMsg.text) {
                    appendMessage(botMsg.text, 'bot');
                }
                
                if (botMsg.buttons && botMsg.buttons.length > 0) {
                    appendButtons(botMsg.buttons);
                }
            }
        } else {
            appendMessage("Silencio... (No pude alcanzar el bot, ¿está encendido?)", 'bot');
        }

    } catch (error) {
        removeTypingIndicator();
        appendMessage("Error de conexión. Asegúrate de ejecutar Rasa con --enable-api y --cors \"*\"", 'bot');
        console.error(error);
    }
}

// UI Helpers
function scrollToBottom() {
    chatHistory.scrollTop = chatHistory.scrollHeight;
}

let typingIndicatorElement = null;

function showTypingIndicator() {
    typingIndicatorElement = document.createElement('div');
    typingIndicatorElement.classList.add('typing-indicator');
    
    for (let i = 0; i < 3; i++) {
        const dot = document.createElement('div');
        dot.classList.add('typing-dot');
        typingIndicatorElement.appendChild(dot);
    }
    
    chatHistory.appendChild(typingIndicatorElement);
    scrollToBottom();
}

function removeTypingIndicator() {
    if (typingIndicatorElement && typingIndicatorElement.parentNode) {
        typingIndicatorElement.parentNode.removeChild(typingIndicatorElement);
        typingIndicatorElement = null;
    }
}
