document.addEventListener('DOMContentLoaded', function() {
    const chatList = document.getElementById('chat-list');
    const resetButton = document.getElementById('reset-history');
    const startChatButton = document.getElementById('start-chat-button');

    // Load chat sessions
    function loadChatSessions() {
        fetch('/get-chats')
            .then(response => response.json())
            .then(data => {
                chatList.innerHTML = '';
                data.forEach(chat => {
                    const chatItem = document.createElement('li');
                    const chatTitleSpan = document.createElement('span');
                    const renameButton = document.createElement('button');
                    const icon = document.createElement('img');
    
                    renameButton.className = 'rename-chat-button';
                    icon.src = 'static/icons/rename.svg';
                    icon.alt = 'Rename';
                    renameButton.appendChild(icon);
    
                    chatTitleSpan.textContent = chat.chatTitle || `Chat Session ${chat.chatSessionId}`;
                    chatItem.appendChild(chatTitleSpan);
                    chatItem.appendChild(renameButton);
    
                    // Chat item click event
                    chatItem.onclick = () => loadChat(chat.chatSessionId);
    
                    // Rename button click event
                    renameButton.onclick = (e) => {
                        e.stopPropagation(); // Prevents the chat from loading when clicking the rename button
                        createEditableTitle(chatTitleSpan, chat.chatSessionId, chatTitleSpan.textContent);
                    };
    
                    chatList.appendChild(chatItem);
                });
            });
    }
    
    function createEditableTitle(element, chatSessionId, currentTitle) {
        element.innerHTML = ''; // Clear the current title
    
        // Create an editable text input
        const input = document.createElement('input');
        input.type = 'text';
        input.value = currentTitle;
        input.className = 'chat-title-input'; 
        element.appendChild(input);
        input.focus(); 
        input.addEventListener('keypress', function(event) {
            if (event.key === 'Enter') {
                event.preventDefault();
                if (input.value.trim()) {
                    renameChat(chatSessionId, input.value.trim());
                    element.textContent = input.value.trim(); 
                } else {
                    element.textContent = currentTitle;
                }
            }
        });
    }
    
    function renameChat(chatSessionId, newTitle) {
        fetch(`/rename-chat/${chatSessionId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ newTitle })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to rename chat.');
            }
            loadChatSessions(); // Reload to reflect changes
        })
        .catch(error => console.error('Error:', error));
    }
    

    function resetSideBar() {
        // Remove all child <li> elements from the <ul>
        while (chatList.firstChild) {
            chatList.removeChild(chatList.firstChild);
        }
    }

    // Load a specific chat
    function loadChat(chatSessionId) {
        resetChatBox();
        fetch('/load-chat', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'id': chatSessionId
            }
        })
        .then(response => response.json())
        .then(data => {
            data.forEach(message => addMessageToChatBox(message['message'], message['by_user'] == 1 ? "right" : "left", message['message_id']))
            console.log(data)
        })
        .catch(error => console.error('Error:', error));
        console.log(`Loading chat: ${chatSessionId}`);
        loadChatSessions();
    }

    // Reset chat history
    resetButton.addEventListener('click', () => {
        // Implement reset functionality
        console.log('Resetting chat history');
        // Example: fetch('/api/reset-history', { method: 'POST' })
        fetch('/reset-sidebar', {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
            }
        })
        .then(response => response.json())
        .then(() => {
            resetSideBar();
            loadChatSessions();
        })
        .catch(error => console.error('Error:', error));
        resetSideBar();
        loadChatSessions();
    });

    startChatButton.addEventListener('click', () => {
        const chatBox = document.getElementById('chat-box');
        if (chatBox.firstChild) {
            window.location.href = '/';
        }
    })

    // Initial load
    loadChatSessions();
});
