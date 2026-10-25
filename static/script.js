const messagesEl = document.getElementById("messages");
const form = document.getElementById("chatForm");
const input = document.getElementById("userInput");
const sendBtn = document.getElementById("sendBtn");
const chips = document.getElementById("chips");
const clearBtn = document.getElementById("clearBtn");

const WELCOME = "Hi! I'm CodeBuddy 🤖 Ask me about programming, resumes, interviews or study tips. Type 'help' to see everything I can do.";

function timeNow() {
  return new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}

function addMessage(text, sender) {
  const div = document.createElement("div");
  div.className = "msg " + sender;
  div.textContent = text;
  const small = document.createElement("small");
  small.textContent = timeNow();
  div.appendChild(small);
  messagesEl.appendChild(div);
  messagesEl.scrollTop = messagesEl.scrollHeight;
  return div;
}

function showTyping() {
  const div = document.createElement("div");
  div.className = "msg bot typing";
  div.innerHTML = "<span></span><span></span><span></span>";
  messagesEl.appendChild(div);
  messagesEl.scrollTop = messagesEl.scrollHeight;
  return div;
}

async function sendMessage(text) {
  text = text.trim();
  if (!text) return;
  addMessage(text, "user");
  input.value = "";
  sendBtn.disabled = true;
  const typing = showTyping();

  try {
    const res = await fetch("/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: text }),
    });
    const data = await res.json();
    await new Promise((r) => setTimeout(r, 400)); // small natural delay
    typing.remove();
    addMessage(data.reply, "bot");
  } catch (err) {
    typing.remove();
    addMessage("⚠️ Could not reach the server. Is it running?", "bot");
  } finally {
    sendBtn.disabled = false;
    input.focus();
  }
}

form.addEventListener("submit", (e) => {
  e.preventDefault();
  sendMessage(input.value);
});

chips.addEventListener("click", (e) => {
  if (e.target.tagName === "BUTTON") sendMessage(e.target.textContent);
});

clearBtn.addEventListener("click", () => {
  messagesEl.innerHTML = "";
  addMessage(WELCOME, "bot");
});

addMessage(WELCOME, "bot");
input.focus();
