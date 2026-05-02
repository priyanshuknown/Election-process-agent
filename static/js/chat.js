document.addEventListener('DOMContentLoaded', () => {
    const chatFab = document.getElementById('chat-fab');
    const chatWindow = document.getElementById('chat-window');
    const closeChatBtn = document.getElementById('close-chat');
    const chatInput = document.getElementById('chat-input');
    const sendChatBtn = document.getElementById('send-chat');
    const chatBody = document.getElementById('chat-body');

    if (!chatFab || !chatWindow) return;

    chatFab.addEventListener('click', () => {
        chatWindow.classList.toggle('active');
        if(chatWindow.classList.contains('active')) {
            chatInput.focus();
        }
    });

    closeChatBtn.addEventListener('click', () => {
        chatWindow.classList.remove('active');
    });

    function addMessage(text, isUser = false) {
        const msgDiv = document.createElement('div');
        msgDiv.classList.add('chat-message');
        msgDiv.classList.add(isUser ? 'user' : 'bot');
        msgDiv.classList.add('animate-fade-in');
        
        // Handle suggestions
        if (!isUser && text.includes("||SUGGESTION:")) {
            const parts = text.split("||SUGGESTION:");
            let mainText = parts[0];
            let suggestionText = parts[1];
            
            msgDiv.innerText = mainText;
            
            let suggestionLink = "#";
            if(suggestionText.includes("Journey")) suggestionLink = "/journey";
            else if(suggestionText.includes("Booth")) suggestionLink = "/booth";
            else if(suggestionText.includes("Document")) suggestionLink = "/documents";
            
            const chip = document.createElement('a');
            chip.href = suggestionLink;
            chip.classList.add('suggestion-chip');
            chip.innerText = "👉 " + suggestionText;
            
            msgDiv.appendChild(document.createElement('br'));
            msgDiv.appendChild(chip);
        } else {
            msgDiv.innerText = text;
        }

        chatBody.appendChild(msgDiv);
        chatBody.scrollTop = chatBody.scrollHeight;
    }

    async function sendMessage() {
        const text = chatInput.value.trim();
        if (!text) return;

        addMessage(text, true);
        chatInput.value = '';

        try {
            const res = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ message: text })
            });
            const data = await res.json();
            
            setTimeout(() => {
                addMessage(data.response, false);
            }, 600); // Small delay to feel natural
            
        } catch(e) {
            console.error("Chat error", e);
            addMessage("Oops, I encountered an error connecting to the server.", false);
        }
    }

    sendChatBtn.addEventListener('click', sendMessage);
    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });
});
