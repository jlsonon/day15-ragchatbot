import { useState } from "react";
import { LuSend } from "react-icons/lu";
import { motion, AnimatePresence } from "framer-motion";

export default function ChatInterface({ history, onSend, loading }) {
  const [question, setQuestion] = useState("");

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (!question.trim()) return;
    await onSend(question.trim());
    setQuestion("");
  };

  return (
    <section className="chat-container">
      <header className="chat-header">
        <div>
          <h2>Research Assistant</h2>
          <p>Ask follow-up questions, explore insights, or dive deeper into specific topics.</p>
        </div>
      </header>
      <div className="chat-history">
        <AnimatePresence initial={false}>
          {history.map((message) => (
            <motion.div
              key={message.id}
              layout
              initial={{ opacity: 0, translateY: 8 }}
              animate={{ opacity: 1, translateY: 0 }}
              exit={{ opacity: 0, translateY: -8 }}
              className={`chat-bubble chat-bubble-${message.role}`}
            >
              <span className="chat-role">{message.role === "assistant" ? "AI Adviser" : "You"}</span>
              <p>{message.content}</p>
              {message.meta && <span className="chat-meta">{message.meta}</span>}
            </motion.div>
          ))}
        </AnimatePresence>
      </div>
      <form className="chat-input" onSubmit={handleSubmit}>
        <input
          type="text"
          placeholder="Ask follow-up questions... e.g. 'What are the key opportunities?' or 'Summarize the main trends'"
          value={question}
          onChange={(event) => setQuestion(event.target.value)}
          disabled={loading}
        />
        <button type="submit" disabled={!question.trim() || loading}>
          {loading ? "Thinking..." : <LuSend size={18} />}
        </button>
      </form>
    </section>
  );
}

