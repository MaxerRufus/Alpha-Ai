document.addEventListener('DOMContentLoaded', () => {
    const video = document.getElementById('background-video');

    video.addEventListener('timeupdate', () => {
        if (video.currentTime >= video.duration - 0.5) {
            video.classList.add('fade-out');
        }
    });

    video.addEventListener('ended', () => {
        video.classList.remove('fade-out');
        video.currentTime = 0.5;
        video.play();
    });

    // Listen for Enter key press on input box
    document.getElementById("user-input").addEventListener("keyup", sendMessageOnEnter);
});

// Function to send message when Enter key is pressed
function sendMessageOnEnter(event) {
    if (event.key === "Enter") {
        event.preventDefault();
        sendMessage();
    }
}

// Function to send message to the server and display the response
function sendMessage() {
    var userInput = document.getElementById("user-input").value.trim();
    if (userInput !== "") {
        addToChat("user", userInput);

        // Clear input field
        document.getElementById("user-input").value = "";

        // Send message to server (in this case, handled by Python backend)
        fetch('/send-message', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: userInput
            }),
        })
        .then(response => response.json())
        .then(data => {
            // Display response from server
            addToChat("bot", data.answer);
        })
        .catch(error => {
            console.error('Error:', error);
        });
    }
}

// Function to add a message to the chat box
function addToChat(sender, message) {
    var chatBox = document.getElementById("chat-box");
    var chatMessage = document.createElement("div");
    chatMessage.className = "message " + sender.toLowerCase();

    var icon = document.createElement("img");
    icon.className = "icon";
    if (sender === "user") {
        icon.src = "/static/user-icon.jpg";
        icon.alt = "User Icon";
    } else {
        icon.src = "/static/bot-icon.png";
        icon.alt = "Bot Icon";
    }

    var messageContent = document.createElement("div");
    messageContent.className = "message-content";
    messageContent.textContent = message;

    chatMessage.appendChild(icon);
    chatMessage.appendChild(messageContent);
    chatBox.appendChild(chatMessage);

    // Scroll to bottom of chat box
    chatBox.scrollTop = chatBox.scrollHeight;
}
