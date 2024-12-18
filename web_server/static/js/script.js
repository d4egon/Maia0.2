// Theme Toggle with LocalStorage
const toggleSwitch = document.getElementById("theme-toggle");
toggleSwitch.addEventListener("change", () => {
    document.body.classList.toggle("light-theme");
    localStorage.setItem("theme", document.body.classList.contains("light-theme") ? "light" : "dark");
});
document.addEventListener("DOMContentLoaded", () => {
    if (localStorage.getItem("theme") === "light") {
        document.body.classList.add("light-theme");
        toggleSwitch.checked = true;
    }
});

// MAIA Face Click - Open Chat Window
document.addEventListener("DOMContentLoaded", () => {
    const heroImage = document.getElementById("maia-face");

    heroImage.addEventListener("click", () => {
        heroImage.classList.add("hidden");

        const chatPopup = document.createElement("div");
        chatPopup.classList.add("maia-chat-popup");
        chatPopup.innerHTML = `
            <div class="maia-chat-header">
                M.A.I.A. chat
                <button class="close-chat" aria-label="Close">&times;</button>
            </div>
            <div class="maia-chat-log" id="chat-log"></div>
            <div class="maia-chat-input">
                <input type="text" id="chat-input" placeholder="Type your question here...">
                <button id="chat-send-btn">Send</button>
            </div>
        `;
        document.body.appendChild(chatPopup);

        const inputField = document.getElementById("chat-input");
        const sendButton = document.getElementById("chat-send-btn");
        const chatLog = document.getElementById("chat-log");

        inputField.focus();

        document.querySelector(".close-chat").addEventListener("click", () => {
            chatPopup.remove();
            heroImage.classList.remove("hidden");
        });

        function sendMessage() {
            const userMessage = inputField.value.trim();
            if (userMessage) {
                chatLog.innerHTML += `<div class="user-message"><strong>You:</strong> ${userMessage}</div>`;
                chatLog.scrollTop = chatLog.scrollHeight;

                fetch("/ask_maia", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ question: userMessage })
                })
                .then(response => response.json())
                .then(data => {
                    chatLog.innerHTML += `<div class="maia-message"><strong>MAIA:</strong> ${data.response || "No response available."}</div>`;
                    chatLog.scrollTop = chatLog.scrollHeight;
                })
                .catch(err => {
                    console.error("Error:", err);
                    chatLog.innerHTML += `<div class="maia-message"><strong>MAIA:</strong> Something went wrong.</div>`;
                });

                inputField.value = "";
            }
        }

        sendButton.addEventListener("click", sendMessage);
        inputField.addEventListener("keydown", (e) => {
            if (e.key === "Enter") sendMessage();
        });
    });
});

// Dynamic Gallery Loader
document.addEventListener("DOMContentLoaded", () => {
    const galleryContainer = document.getElementById("gallery-container");
    if (!galleryContainer) return console.warn("Gallery container not found!");

    fetch('/get_gallery_images')
        .then(response => response.json())
        .then(data => {
            if (data.images && data.images.length > 0) {
                data.images.forEach(filename => {
                    const img = document.createElement("img");
                    img.src = `static/images/${filename}`;
                    img.alt = `Gallery Image ${filename}`;
                    img.loading = "lazy";
                    img.onerror = () => console.error(`Failed to load image: ${filename}`);
                    galleryContainer.appendChild(img);
                });
            } else {
                galleryContainer.innerHTML = "<p>No images found.</p>";
            }
        })
        .catch(err => {
            console.error("Failed to fetch gallery images:", err);
            galleryContainer.innerHTML = "<p>Error loading gallery.</p>";
        });
});
