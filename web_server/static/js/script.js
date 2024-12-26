document.addEventListener("DOMContentLoaded", () => {
    const messengerIcon = document.getElementById("maia-face");
    const talkToMaiaBtn = document.getElementById("talk-to-maia-btn");
    const chatPopup = document.getElementById("maia-chat-popup");
    const chatLog = document.getElementById("chat-log");
    const inputField = document.getElementById("chat-input");
    const sendButton = document.getElementById("chat-send-btn");
    const fileInput = document.getElementById("file-input");
    const uploadButton = document.getElementById("upload-button");
    const uploadFeedback = document.getElementById("upload-feedback");

    let chatPopupVisible = false;

    function initializeChat() {
        if (chatPopupVisible) return;

        chatPopup.classList.remove("hidden");
        chatPopupVisible = true;
        inputField.focus();
    }

    function showTyping() {
        const typingMessage = document.createElement("div");
        typingMessage.classList.add("maia-message", "typing");
        typingMessage.textContent = "MAIA is typing...";
        chatLog.appendChild(typingMessage);
        chatLog.scrollTop = chatLog.scrollHeight;
        return typingMessage;
    }

    function addMessage(sender, message, cssClass) {
        const messageElement = document.createElement("div");
        messageElement.classList.add(cssClass);
        messageElement.innerHTML = `<strong>${sender}:</strong> ${message}`;
        chatLog.appendChild(messageElement);
        chatLog.scrollTop = chatLog.scrollHeight;
    }

    function sendMessage() {
        const userMessage = inputField.value.trim();
        if (!userMessage) return;

        addMessage("You", userMessage, "user-message");
        const typingIndicator = showTyping();

        fetch("/ask_maia", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ question: userMessage }),
        })
            .then((response) => {
                if (!response.ok) throw new Error(`[ERROR] Server returned status ${response.status}`);
                return response.json();
            })
            .then((data) => {
                typingIndicator.remove();
                addMessage("MAIA", data.response || "No response available.", "maia-message");
            })
            .catch((err) => {
                console.error("Error:", err);
                typingIndicator.remove();
                addMessage("MAIA", "An error occurred. Please try again.", "maia-message");
            });

        inputField.value = "";
        inputField.focus();
    }

    function uploadFile() {
        if (!fileInput.files.length) {
            uploadFeedback.innerText = "No file selected. Please choose a file to upload.";
            return;
        }

        const file = fileInput.files[0];
        const formData = new FormData();
        formData.append("file", file);

        uploadFeedback.innerText = "Uploading file...";

        fetch("/upload", {
            method: "POST",
            body: formData,
        })
            .then((response) => response.json())
            .then((data) => {
                if (data.status === "success") {
                    uploadFeedback.innerHTML = `
                        <strong>Success:</strong> ${data.message}<br>
                        <strong>Content Preview:</strong> ${data.summary}
                    `;
                } else {
                    uploadFeedback.innerHTML = `<strong>Error:</strong> ${data.message}`;
                }
            })
            .catch((err) => {
                console.error("Error uploading file:", err);
                uploadFeedback.innerText = "An unexpected error occurred during the upload.";
            });
    }

    // Close chat functionality
    document.querySelector(".close-chat").addEventListener("click", () => {
        chatPopup.classList.add("hidden");
        chatPopupVisible = false;
    });

    sendButton.addEventListener("click", sendMessage);
    inputField.addEventListener("keydown", (e) => {
        if (e.key === "Enter") sendMessage();
    });

    uploadButton.addEventListener("click", uploadFile);

    messengerIcon.addEventListener("click", initializeChat);
    talkToMaiaBtn.addEventListener("click", initializeChat);
});

// Dynamic Gallery Loader
document.addEventListener("DOMContentLoaded", () => {
    const galleryContainer = document.getElementById("gallery-container");

    fetch('/get_gallery_images')
        .then(response => response.json())
        .then(data => {
            const uniqueFilenames = new Set(data.images || []);

            uniqueFilenames.forEach(filename => {
                const img = document.createElement("img");
                img.src = `static/images/${filename}`;
                img.alt = `Gallery Image ${filename}`;
                img.loading = "lazy";
                galleryContainer.appendChild(img);
            });
        })
        .catch(err => {
            console.error("Gallery Fetch Error:", err);
        });
});
