export default function ChatPanel({
  selectedDoc,
  chatMessages,
  chatInput,
  setChatInput,
  chatLoading,
  handleSendQuestion,
  onClose,
}) {
  if (!selectedDoc) return null;

  return (
    <aside className="chat-panel" role="complementary">
      {/* Header */}
      <div className="chat-title">
        Chat with: {selectedDoc.filename}
        <button
          className="chat-close"
          onClick={onClose}
          aria-label="Close chat"
        >
          ✕
        </button>
      </div>

      {/* Messages */}
      <div className="chat-messages">
        {chatMessages.length === 0 && !chatLoading && (
          <div className="empty">Ask something…</div>
        )}

        {chatMessages.map((msg, idx) => (
          <div
            key={idx}
            className={`chat-message ${msg.role === "user" ? "user" : ""}`}
          >
            <div className="chat-message-role">
              {msg.role === "user" ? "You" : "Assistant"}
            </div>
            <div>{msg.content}</div>
          </div>
        ))}

        {chatLoading && (
          <div className="chat-message">
            <div className="chat-message-role">Assistant</div>
            <div>Thinking…</div>
          </div>
        )}
      </div>

      {/* Input */}
      <form className="chat-input-row" onSubmit={handleSendQuestion}>
        <input
          value={chatInput}
          onChange={(e) => setChatInput(e.target.value)}
          placeholder="Ask something…"
          disabled={chatLoading}
        />
        <button
          type="submit"
          disabled={!chatInput.trim() || chatLoading}
        >
          Send
        </button>
      </form>
    </aside>
  );
}
