import { useState } from "react";
import "./App.css";

function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  const [sessionId] = useState(
    () => crypto.randomUUID()
  );

  async function sendMessage() {
    if (!input.trim() || loading) return;

    const userMessage = input;
    setInput("");

    setMessages(prev => [
      ...prev,
      { role: "user", content: userMessage }
    ]);

    setLoading(true);

    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL}/chat`, {        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          session_id: sessionId,
          message: userMessage
        })
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Something went wrong");
      }

      setMessages(prev => [
        ...prev,
        {
          role: "assistant",
          content: data.reply,
          metadata: data.metadata
        }
      ]);
    } catch (error) {
      setMessages(prev => [
        ...prev,
        {
          role: "assistant",
          content: `Error: ${error.message}`
        }
      ]);
    }

    setLoading(false);
  }

  return (
    <div className="app">
      <header>
        <h1>Lyftr AI</h1>
        <p>Your intelligent AI assistant</p>
      </header>

      <main className="chat">
        {messages.map((msg, index) => (
          <div
            key={index}
            className={`message ${msg.role}`}
            data-testid={msg.role === "assistant" ? "assistant-message" : undefined}
          >
            <strong>
              {msg.role === "user" ? "You" : "Lyftr AI"}
            </strong>

            <p>{msg.content}</p>

            {msg.metadata && (
              <div className="metadata">
                <span data-testid="meta-source">
                  Source: {msg.metadata.resolution_source}
                </span>
                <span data-testid="meta-model">
                  Model: {msg.metadata.model}
                </span>
                <span data-testid="meta-latency">
                  Latency: {msg.metadata.latency_ms} ms
                </span>
                <span data-testid="meta-input-tokens">
                  Input tokens: {msg.metadata.input_tokens}
                </span>
                <span data-testid="meta-output-tokens">
                  Output tokens: {msg.metadata.output_tokens}
                </span>
              </div>
            )}
          </div>
        ))}

        {loading && <p>Lyftr AI is thinking...</p>}
      </main>

      <footer>
        <input
          data-testid="chat-input"
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => e.key === "Enter" && sendMessage()}
          placeholder="Ask Lyftr anything..."
        />

        <button
          data-testid="send-button"
          onClick={sendMessage}
          disabled={loading}
        >
          Send
        </button>
      </footer>
    </div>
  );
}

export default App;