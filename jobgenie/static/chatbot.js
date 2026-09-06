function toggleChatbot() {
    const bot = document.getElementById("chatbotBox");
    bot.classList.toggle("hidden");

    // Hide suggestions after first interaction
    const suggestions = document.getElementById("chatSuggestions");
    if (!bot.classList.contains("hidden") && suggestions) {
        suggestions.style.display = "flex";
    }
}

function sendMessage() {
    const input = document.getElementById("chatInput");
    const body = document.getElementById("chatBody");
    const msg = input.value.trim();

    if (!msg) return;

    // Hide suggestions
    const suggestions = document.getElementById("chatSuggestions");
    if (suggestions) suggestions.style.display = "none";

    // Add user message
    appendMessage(body, msg, "user");
    input.value = "";

    // Show typing indicator
    const typingId = showTyping(body);

    fetch("/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: msg })
    })
    .then(res => res.json())
    .then(data => {
        removeTyping(typingId);
        appendMessage(body, data.reply, "bot");
    })
    .catch(() => {
        removeTyping(typingId);
        appendMessage(body, "Something went wrong. Please try again! 😅", "bot");
    });
}

function sendSuggestion(text) {
    document.getElementById("chatInput").value = text;
    sendMessage();
}

function appendMessage(body, text, type) {
    const div = document.createElement("div");
    div.className = type === "user" ? "user-msg" : "bot-msg";
    div.textContent = text;
    div.style.opacity = "0";
    div.style.transform = "translateY(8px)";
    body.appendChild(div);
    body.scrollTop = body.scrollHeight;

    // Animate in
    requestAnimationFrame(() => {
        div.style.transition = "opacity 0.3s ease, transform 0.3s ease";
        div.style.opacity = "1";
        div.style.transform = "translateY(0)";
    });
}

function showTyping(body) {
    const id = "typing-" + Date.now();
    const div = document.createElement("div");
    div.className = "bot-msg typing-indicator";
    div.id = id;
    div.innerHTML = '<span></span><span></span><span></span>';
    body.appendChild(div);
    body.scrollTop = body.scrollHeight;
    return id;
}

function removeTyping(id) {
    const el = document.getElementById(id);
    if (el) el.remove();
}
