// Theme Toggle
const toggleSwitch = document.getElementById("theme-toggle");
toggleSwitch.addEventListener("change", () => {
    document.body.classList.toggle("light-theme");
    localStorage.setItem("theme", document.body.classList.contains("light-theme") ? "light" : "dark");
});

// Preserve Theme Preference on Reload
document.addEventListener("DOMContentLoaded", () => {
    if (localStorage.getItem("theme") === "light") {
        document.body.classList.add("light-theme");
        toggleSwitch.checked = true;
    }
});

/* Optional Light Theme CSS */
document.head.insertAdjacentHTML(
    "beforeend",
    `
    <style>
        body.light-theme {
            background: #bdbfbf;
            color: #333;
        }
        .navbar, footer {
            background: #ddd;
            color: #333;
        }
        .nav-links a {
            color: #333;
        }
        .nav-links a:hover {
            color: #00d8ff;
        }
        .cta-btn {
            background: #333;
            color: #bdbfbf;
        }
    </style>
    `
);

// Function to interact with MAIA
function talkToMaia() {
    const userInput = prompt("Ask MAIA anything...");
    if (userInput) {
        fetch("/ask_maia", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ question: userInput })
        })
        .then(response => {
            if (!response.ok) throw new Error("Network response was not ok");
            return response.json();
        })
        .then(data => {
            alert(`MAIA says: ${data.response || "No response available."}`);
        })
        .catch(error => {
            console.error("Error:", error);
            alert("Oops! Something went wrong. Please try again.");
        });
    }
}

// Dynamically load images into the gallery
document.addEventListener("DOMContentLoaded", () => {
    const galleryContainer = document.getElementById("gallery-container");

    // List of images in the 'static/images' folder
    const imageFilenames = [
        "maia1.jpg",
        "maia2.jpg",
        "maia3.jpg",
        "maia4.jpg",
        "maia5.jpg",
        "maia6.jpg"
    ];

    // Check for gallery container
    if (!galleryContainer) {
        console.warn("Gallery container not found!");
        return;
    }

    // Load each image into the gallery
    imageFilenames.forEach(filename => {
        const img = document.createElement("img");
        img.src = `static/images/${filename}`;
        img.alt = `Gallery Image ${filename}`;
        img.loading = "lazy"; // Lazy loading for performance
        img.onerror = () => console.error(`Failed to load image: ${filename}`);
        galleryContainer.appendChild(img);
    });
});
