const inputField = document.getElementById('text-input');
inputField.addEventListener("keyup", function(event) {
    if (event.key === "Enter") {
        // Trigger the function
        sendText();
    }
});

function sendText() {
    const inputField = document.getElementById('text-input');
    const message = inputField.value;

    if (message.trim() === '') return; 

    addMessageToChatBox(message, 'right'); 
    sendMessage('application/json', JSON.stringify({ message: message }));
    inputField.value = ''; 
}
function sendAudio(audioBlob) {
    sendMessage('audio/wav', audioBlob);
}

function sendImage(imageBlob) {
    sendMessage('image/jpeg', imageBlob);
}
//TODO: audio and image handling


function sendMessage(contentType, data) {
    fetch('/send_message', {
        method: 'POST',
        headers: {
            'Content-Type': contentType,
        },
        body: data
    })
    .then(response => response.json())
    .then(data => {
        textResponse(data.response, data.message_id); // Process and display the response
    })
    .catch(error => console.error('Error:', error));
}

function textResponse(responseText, bot_id) {
    addMessageToChatBox(responseText, 'left', bot_id); 
}



function addMessageToChatBox(message, side, message_id) {
    const chatBox = document.getElementById('chat-box');
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message';

    if (side === 'right') {
        // User message
        messageDiv.innerHTML = `<div class="user-message">${message}</div>`;
        messageDiv.className += ' user-message';
    } else {
        // Bot response
        messageDiv.innerHTML = `
            <div class="bot-message" id="${message_id}">
                <div class="message-content">${message}</div>
                <div class="message-actions">
                    <button class="copy-button" onclick="copyText('${message}')">
                        <img src="static/icons/clipboard.svg" alt="Copy"/> 
                    </button>
                    <button class="create-video" onclick='addVideoToChatBox(${message_id})'>
                        Create Video
                    </button>
                </div>
            </div>`;
        messageDiv.className += ' bot-message';
        // addVideoToChatBox();
    }
    chatBox.appendChild(messageDiv);
    // Scroll to the latest message
    chatBox.scrollTop = chatBox.scrollHeight;
}

function addVideoToChatBox(message_id) {
    const chatBox = document.getElementById('chat-box');
    const videoDiv = document.createElement('div');
    videoDiv.className = 'video';
        // Bot response
        videoDiv.innerHTML = `
        <video width="256" height="256" controls>
            <source src="http://127.0.0.1:5000/stream_video/${message_id}" type="video/mp4">
            Your browser does not support the video tag.
         </video>
         `;
    chatBox.appendChild(videoDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
}

function resetChatBox() {
    const chatBox = document.getElementById('chat-box');
    while (chatBox.firstChild) {
        chatBox.removeChild(chatBox.firstChild);
    }
}



// Extra features:
// Copy text to clipboard
function copyText(textToCopy) {
    navigator.clipboard.writeText(textToCopy).then(function() {
        console.log('Text copied to clipboard');
    }).catch(function(err) {
        console.error('Could not copy text: ', err);
    });
}

// Toggle dark mode
document.addEventListener('DOMContentLoaded', () => {
    const modeToggle = document.getElementById('mode-toggle');
    const lightIcon = document.getElementById('light-icon');
    const darkIcon = document.getElementById('dark-icon');
    const body = document.body;

    modeToggle.addEventListener('click', () => {
        // Toggle the class to switch themes
        body.classList.toggle('dark-theme');
        
        // Determine which icon is currently displayed and toggle animation classes accordingly
        const currentIcon = getComputedStyle(lightIcon).display !== 'none' ? lightIcon : darkIcon;
        const otherIcon = currentIcon === lightIcon ? darkIcon : lightIcon;
        
        currentIcon.style.display = 'block'; // Make sure both icons are visible before animation
        otherIcon.style.display = 'block'; // Make sure both icons are visible before animation
        
        currentIcon.classList.add('exit');
        otherIcon.classList.add('enter');
        
        // Toggle visibility of the icons after the animation completes
        setTimeout(() => {
            currentIcon.style.display = 'none';
            otherIcon.style.display = 'block';
            
            // Remove animation classes to reset for the next click
            currentIcon.classList.remove('exit');
            otherIcon.classList.remove('enter');
        }, 800); // Wait for the animation to complete (0.5s) before toggling icons
    });
});


