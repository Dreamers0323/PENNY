document.addEventListener("DOMContentLoaded", () => {
    console.log("🚀 Penny.js loaded successfully");
    
    const chatMessages = document.getElementById("chatMessages");
    const chatInput = document.getElementById("chatInput");
    const sendButton = document.getElementById("sendMessageBtn");
    const quickButtons = document.querySelectorAll(".quick-question");

    // Check if elements exist
    if (!chatMessages) console.error("❌ chatMessages element not found");
    if (!chatInput) console.error("❌ chatInput element not found");
    if (!sendButton) console.error("❌ sendMessageBtn element not found");
    if (quickButtons.length === 0) console.error("❌ No quick-question buttons found");

    // Function to append a message to chat
    function addMessage(sender, text) {
        console.log(`💬 Adding message - Sender: ${sender}, Text: ${text}`);
        const msgDiv = document.createElement("div");
        msgDiv.classList.add("message", sender);
        msgDiv.innerHTML = `<strong>${sender === "user" ? "You" : "Penny"}:</strong> ${text}`;
        chatMessages.appendChild(msgDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    // Test function to check basic communication
    async function testConnection() {
        console.log("🔧 Testing connection...");
        
        try {
            const response = await fetch("/penny/test", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ message: "Connection test" })
            });

            console.log("🔧 Test response status:", response.status);
            console.log("🔧 Test response ok:", response.ok);

            const data = await response.json();
            console.log("🔧 Test response data:", data);

            if (data.success) {
                addMessage("penny", "✅ Connection test successful!");
                console.log("🔧 Debug info:", data.debug_info);
            } else {
                addMessage("penny", "❌ Connection test failed: " + data.error);
            }
        } catch (err) {
            console.error("🔧 Test connection error:", err);
            addMessage("penny", "❌ Connection test failed: " + err.message);
        }
    }

    // Send message to backend
    async function sendMessage(text) {
        if (!text.trim()) {
            console.warn("⚠️ Empty message, not sending");
            return;
        }

        console.log("📤 Sending message:", text);
        addMessage("user", text);
        chatInput.value = "";

        // Add loading indicator
        const loadingMsg = document.createElement("div");
        loadingMsg.classList.add("message", "penny");
        loadingMsg.innerHTML = `<strong>Penny:</strong> <i>Typing...</i>`;
        loadingMsg.id = "loading-message";
        chatMessages.appendChild(loadingMsg);
        chatMessages.scrollTop = chatMessages.scrollHeight;

        try {
            console.log("📡 Making fetch request to /penny/chat");
            
            const response = await fetch("/penny/chat", {
                method: "POST",
                headers: { 
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ message: text })
            });

            console.log("📡 Response received:");
            console.log("  - Status:", response.status);
            console.log("  - Status Text:", response.statusText);
            console.log("  - OK:", response.ok);
            console.log("  - Headers:", [...response.headers.entries()]);

            // Remove loading indicator
            const loading = document.getElementById("loading-message");
            if (loading) loading.remove();

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status} - ${response.statusText}`);
            }

            const responseText = await response.text();
            console.log("📡 Raw response text:", responseText);

            let data;
            try {
                data = JSON.parse(responseText);
                console.log("📡 Parsed response data:", data);
            } catch (parseError) {
                console.error("❌ JSON parse error:", parseError);
                throw new Error(`Invalid JSON response: ${responseText}`);
            }

            // Handle different response formats
            if (data.success && data.response) {
                console.log("✅ Success response with data.response");
                addMessage("penny", data.response);
            } else if (data.response) {
                console.log("✅ Response without success flag");
                addMessage("penny", data.response);
            } else if (data.error) {
                console.log("❌ Error response");
                addMessage("penny", "❌ Error: " + data.error);
            } else {
                console.log("❓ Unexpected response format");
                addMessage("penny", "❌ Unexpected response format");
                console.log("Full response data:", data);
            }

        } catch (err) {
            console.error("❌ Fetch error details:");
            console.error("  - Error type:", err.constructor.name);
            console.error("  - Error message:", err.message);
            console.error("  - Error stack:", err.stack);
            
            // Remove loading indicator if still there
            const loading = document.getElementById("loading-message");
            if (loading) loading.remove();
            
            addMessage("penny", "⚠️ Could not reach Penny server. Error: " + err.message);
        }
    }

    // Event listeners
    if (sendButton) {
        sendButton.addEventListener("click", () => {
            console.log("🖱️ Send button clicked");
            sendMessage(chatInput.value);
        });
    }

    if (chatInput) {
        chatInput.addEventListener("keypress", (e) => {
            if (e.key === "Enter") {
                console.log("⌨️ Enter key pressed");
                sendMessage(chatInput.value);
            }
        });
    }

    quickButtons.forEach((btn, index) => {
        btn.addEventListener("click", () => {
            const question = btn.getAttribute("data-question");
            console.log(`🖱️ Quick button ${index} clicked: ${question}`);
            sendMessage(question);
        });
    });

    // Add test button (for debugging)
    console.log("🔧 Adding test connection button");
    const testButton = document.createElement("button");
    testButton.textContent = "Test Connection";
    testButton.className = "btn";
    testButton.style.marginTop = "10px";
    testButton.style.backgroundColor = "#ff6b6b";
    testButton.onclick = testConnection;
    
    // Add test button to the chat input area
    if (chatInput && chatInput.parentNode) {
        chatInput.parentNode.appendChild(testButton);
    }

    console.log("✅ Penny.js initialization complete");
});