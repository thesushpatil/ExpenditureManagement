/**
 * Chatbot - Gemini AI powered financial assistant
 */

const GEMINI_API_KEY = "AIzaSyCryeRzLO0Wc_7avWkeTBBpllkqNcsK5xg";
const GEMINI_MODEL = "gemini-1.5-flash-latest";
const SYSTEM_INSTRUCTION = `You are an intelligent, friendly financial assistant for ExpManage app. Help users with:
1. Quick expense/income logging guidance
2. Budget setting tips
3. Financial management strategies
4. App navigation help
Be concise, use emojis sparingly, and format responses with markdown. If asked to log data, explain they can use the Expenses/Income/Savings pages in the app.`;

let chatMessages = [];
let isGenerating = false;

const messagesEl = document.getElementById('chat-messages');
const inputEl = document.getElementById('chat-input');
const sendBtn = document.getElementById('chat-send');
const typingEl = document.getElementById('chat-typing');

// Input handling
inputEl.addEventListener('input', () => {
    inputEl.style.height = 'auto';
    inputEl.style.height = inputEl.scrollHeight + 'px';
    sendBtn.disabled = inputEl.value.trim() === '' || isGenerating;
});
inputEl.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(); }
});

function sendSuggestion(text) {
    inputEl.value = text;
    sendMessage();
}

function startNewChat() {
    chatMessages = [];
    messagesEl.innerHTML = `
        <div class="chat-intro">
            <div class="chat-intro-icon"><i class="fas fa-robot"></i></div>
            <h2>EM AI Assistant</h2>
            <p>I can help you log finances, set budgets, and offer financial guidance. Ask me anything!</p>
            <div class="suggestion-chips">
                <button class="chip" onclick="sendSuggestion('How to add expenses')">How to add expenses</button>
                <button class="chip" onclick="sendSuggestion('How to set Budget')">How to set Budget</button>
                <button class="chip" onclick="sendSuggestion('Pros of Expenditure Management')">Pros of Expenditure Management</button>
                <button class="chip" onclick="sendSuggestion('Strategies for Better Financial Growth')">Financial Growth Tips</button>
            </div>
        </div>`;
}

async function sendMessage() {
    const text = inputEl.value.trim();
    if (!text || isGenerating) return;

    // Clear intro
    const intro = messagesEl.querySelector('.chat-intro');
    if (intro) intro.remove();

    // Add user message
    addBubble(text, 'user');
    chatMessages.push({ role: 'user', parts: [{ text }] });
    inputEl.value = '';
    inputEl.style.height = 'auto';
    sendBtn.disabled = true;

    // Show typing
    isGenerating = true;
    typingEl.style.display = 'flex';
    messagesEl.scrollTop = messagesEl.scrollHeight;

    // Call Gemini
    try {
        const response = await fetch(
            `https://generativelanguage.googleapis.com/v1beta/models/${GEMINI_MODEL}:generateContent?key=${GEMINI_API_KEY}`,
            {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    contents: chatMessages,
                    system_instruction: { parts: [{ text: SYSTEM_INSTRUCTION }] },
                }),
            }
        );

        const data = await response.json();
        let aiText = '';

        if (data.candidates?.[0]?.content?.parts?.[0]?.text) {
            aiText = data.candidates[0].content.parts[0].text;
        } else if (data.error) {
            aiText = `Error: ${data.error.message}`;
        } else {
            aiText = 'Sorry, I could not generate a response. Please try again.';
        }

        chatMessages.push({ role: 'model', parts: [{ text: aiText }] });
        addBubble(aiText, 'ai');
    } catch (err) {
        addBubble('Network error. Please check your connection and try again.', 'ai');
    } finally {
        isGenerating = false;
        typingEl.style.display = 'none';
        sendBtn.disabled = inputEl.value.trim() === '';
    }
}

function addBubble(text, sender) {
    const bubble = document.createElement('div');
    bubble.className = `chat-bubble ${sender}`;

    if (sender === 'ai' && typeof marked !== 'undefined') {
        bubble.innerHTML = marked.parse(text);
        bubble.querySelectorAll('pre code').forEach(block => {
            if (typeof hljs !== 'undefined') hljs.highlightElement(block);
        });
    } else {
        bubble.textContent = text;
    }

    messagesEl.appendChild(bubble);
    messagesEl.scrollTop = messagesEl.scrollHeight;
}
