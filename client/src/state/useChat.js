import { useState } from "react";
import { askDocumentQuestion } from "../api/chat.api";

export function useChat() {
  const [selectedDoc, setSelectedDoc] = useState(null);
  const [chatMessages, setChatMessages] = useState([]);
  const [chatInput, setChatInput] = useState("");
  const [chatLoading, setChatLoading] = useState(false);

  function openChatForDoc(doc) {
    setSelectedDoc(doc);
    setChatMessages([]);
    setChatInput("");
  }

  function closeChat() {
    setSelectedDoc(null);
    setChatMessages([]);
    setChatInput("");
    setChatLoading(false);
  }

  async function sendQuestion(e) {
    e.preventDefault();

    if (!chatInput.trim() || !selectedDoc) return;

    const question = chatInput.trim();

    // Optimistic UI
    setChatMessages((prev) => [
      ...prev,
      { role: "user", content: question },
    ]);
    setChatInput("");
    setChatLoading(true);

    const res = await askDocumentQuestion(selectedDoc.id, question);

    setChatMessages((prev) => [
      ...prev,
      {
        role: "assistant",
        content: res?.answer || "Error contacting backend.",
      },
    ]);

    setChatLoading(false);
  }

  return {
    selectedDoc,
    chatMessages,
    chatInput,
    chatLoading,
    setChatInput,
    openChatForDoc,
    closeChat,
    sendQuestion,
  };
}
