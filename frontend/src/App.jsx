import { useCallback, useEffect, useRef, useState } from "react";
import { LuSend, LuUpload, LuFileText, LuX } from "react-icons/lu";
import { motion, AnimatePresence } from "framer-motion";
import { initConversation, uploadDocument, askFollowUp } from "./utils/api.js";
import "./App.css";

const makeId = () => (crypto?.randomUUID ? crypto.randomUUID() : Math.random().toString(36).slice(2));

export default function App() {
  const [conversationId, setConversationId] = useState(null);
  const [history, setHistory] = useState([]);
  const [message, setMessage] = useState("");
  const [uploading, setUploading] = useState(false);
  const [chatting, setChatting] = useState(false);
  const [uploadedFile, setUploadedFile] = useState(null);
  const [resetting, setResetting] = useState(false);
  const [showAbout, setShowAbout] = useState(false);
  const [showAdmin, setShowAdmin] = useState(false);
  const [adminMetrics, setAdminMetrics] = useState(null);
  const [loadingAdmin, setLoadingAdmin] = useState(false);
  const [theme, setTheme] = useState("dark");
  const fileInputRef = useRef(null);
  const chatEndRef = useRef(null);

  useEffect(() => {
    const bootstrap = async () => {
      const id = await initConversation();
      setConversationId(id);
    };
    bootstrap().catch((error) => console.error("Failed to init conversation", error));
  }, []);

  // Apply theme to body for global theming
  useEffect(() => {
    document.body.dataset.theme = theme;
  }, [theme]);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [history]);

  const handleFileUpload = useCallback(
    async (file) => {
      if (!file) return;
      
      try {
        setUploading(true);
        const response = await uploadDocument({
          file,
          conversationId,
        });

        setConversationId(response.conversation_id);
        setUploadedFile(file);
        setHistory((prev) => [
          ...prev,
          {
            id: makeId(),
            role: "assistant",
            content: response.message,
            meta: "Document uploaded",
          },
        ]);
      } catch (error) {
        console.error(error);
        setHistory((prev) => [
          ...prev,
          {
            id: makeId(),
            role: "assistant",
            content: "Failed to upload document. Please try again.",
            meta: "Error",
          },
        ]);
      } finally {
        setUploading(false);
      }
    },
    [conversationId],
  );

  const handleClearSession = useCallback(async () => {
    try {
      setResetting(true);
      // Start a fresh conversation so the backend no longer uses the old document context
      const newId = await initConversation();
      setConversationId(newId);
      setUploadedFile(null);
      setHistory([]);
      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }
    } catch (error) {
      console.error("Failed to reset session", error);
    } finally {
      setResetting(false);
    }
  }, []);

  const handleSend = useCallback(
    async (text) => {
      if (!text.trim()) return;
      if (!uploadedFile && history.length === 0) {
        setHistory((prev) => [
          ...prev,
          {
            id: makeId(),
            role: "assistant",
            content: "Please upload a document first to start chatting.",
            meta: "Info",
          },
        ]);
        return;
      }

      try {
        setChatting(true);
        setHistory((prev) => [
          ...prev,
          {
            id: makeId(),
            role: "user",
            content: text,
          },
        ]);

        const response = await askFollowUp({
          conversationId,
          question: text,
        });
        const sources = Array.isArray(response.sources) ? response.sources : [];

        // Create an assistant message and simulate streaming by gradually revealing the content
        const messageId = makeId();
        const fullText = response.answer || "";
        const baseMessage = {
          id: messageId,
          role: "assistant",
          content: "",
          sources,
        };

        setHistory((prev) => [...prev, baseMessage]);

        let index = 0;
        const step = Math.max(3, Math.floor(fullText.length / 120));
        const interval = setInterval(() => {
          index += step;
          const nextSlice = fullText.slice(0, index);
          setHistory((prev) =>
            prev.map((m) => (m.id === messageId ? { ...m, content: nextSlice } : m)),
          );
          if (index >= fullText.length) {
            clearInterval(interval);
            setHistory((prev) =>
              prev.map((m) => (m.id === messageId ? { ...m, content: fullText } : m)),
            );
          }
        }, 18);

        setMessage("");
      } catch (error) {
        console.error(error);
        setHistory((prev) => [
          ...prev,
          {
            id: makeId(),
            role: "assistant",
            content: "I couldn't process that. Please make sure the backend is running.",
            meta: "Error",
          },
        ]);
      } finally {
        setChatting(false);
      }
    },
    [conversationId, uploadedFile, history.length],
  );

  const handleFileSelect = (event) => {
    const file = event.target.files?.[0];
    if (file) {
      handleFileUpload(file);
    }
  };

  return (
    <div className={`rag-app rag-app-${theme}`}>
      <header className="rag-header">
        <div>
          <h1>RAG Chatbot</h1>
          <p>Upload a document and ask questions about it</p>
        </div>
        <button
          type="button"
          className="theme-toggle"
          onClick={() => setTheme((prev) => (prev === "dark" ? "light" : "dark"))}
        >
          {theme === "dark" ? "Light mode" : "Dark mode"}
        </button>
      </header>

      <div className="rag-container">
        <div
          className="rag-upload-area"
          onDragOver={(e) => {
            e.preventDefault();
          }}
          onDrop={(e) => {
            e.preventDefault();
            const file = e.dataTransfer.files?.[0];
            if (file) {
              handleFileUpload(file);
            }
          }}
        >
          <input
            ref={fileInputRef}
            type="file"
            accept=".pdf,.docx,.txt"
            onChange={handleFileSelect}
            style={{ display: "none" }}
          />
          <div className="upload-actions">
            <button
              className="upload-btn"
              onClick={() => fileInputRef.current?.click()}
              disabled={uploading}
            >
              <LuUpload size={20} />
              {uploading ? "Uploading..." : uploadedFile ? `Uploaded: ${uploadedFile.name}` : "Upload Document"}
            </button>
            <button
              type="button"
              className="clear-btn"
              onClick={handleClearSession}
              disabled={resetting || (!uploadedFile && history.length === 0)}
            >
              <LuX size={16} />
              {resetting ? "Clearing..." : "Clear"}
            </button>
          </div>

          {uploadedFile && (
            <div className="file-info">
              <LuFileText size={16} />
              <span>{uploadedFile.name}</span>
            </div>
          )}
        </div>

        <div className="rag-chat">
          <div className="chat-messages">
            {history.length === 0 && (
              <div className="chat-empty">
                <p>Upload a document to start chatting!</p>
                <p className="hint">Supported: PDF, DOCX, TXT</p>
              </div>
            )}
            <AnimatePresence initial={false}>
              {history.map((msg) => (
                <motion.div
                  key={msg.id}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -10 }}
                  className={`chat-message chat-message-${msg.role}`}
                >
                  <div className="message-content">
                    <span className="message-role">{msg.role === "assistant" ? "AI" : "You"}</span>
                    <p>{msg.content}</p>
                    {msg.meta && <span className="message-meta">{msg.meta}</span>}
                  </div>
                </motion.div>
              ))}
            </AnimatePresence>
            <div ref={chatEndRef} />
          </div>

          <form
            className="chat-input-area"
            onSubmit={(e) => {
              e.preventDefault();
              handleSend(message);
            }}
          >
            <input
              type="text"
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              placeholder="Ask a question about the document..."
              disabled={chatting || !uploadedFile}
            />
            <button type="submit" disabled={!message.trim() || chatting || !uploadedFile}>
              {chatting ? "..." : <LuSend size={18} />}
            </button>
          </form>
        </div>
      </div>

      <footer className="rag-footer">
        <span className="rag-footer-text">
          InQuest RAG Assistant · Built by Jericho Sonon, Generative AI enthusiast
        </span>
        <div className="rag-footer-actions">
          <button type="button" className="about-btn" onClick={() => setShowAbout(true)}>
            About this app
          </button>
          <button type="button" className="about-btn admin-btn" onClick={() => setShowAdmin(true)}>
            Admin
          </button>
        </div>
      </footer>

      <AnimatePresence>
        {showAbout && (
          <motion.div
            className="about-backdrop"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={() => setShowAbout(false)}
          >
            <motion.div
              className="about-modal"
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              onClick={(e) => e.stopPropagation()}
            >
              <header className="about-modal-header">
                <h2>About this project</h2>
                <button type="button" onClick={() => setShowAbout(false)} aria-label="Close about">
                  <LuX size={18} />
                </button>
              </header>
              <div className="about-modal-body">
                <p>
                  This is a portfolio-ready Retrieval-Augmented Generation (RAG) app. Upload a document and the AI
                  will retrieve the most relevant passages and answer your questions grounded in that context.
                </p>
                <p>
                  Under the hood it uses semantic embeddings, smart chunking, and conversation memory so you can ask
                  natural follow-up questions without re-explaining your document.
                </p>
                <p>
                  It was crafted by <strong>Jericho Sonon</strong>, a Generative AI enthusiast focused on building
                  practical, polished AI tools that are easy to demo and iterate on.
                </p>
                <p className="about-meta">
                  Built with FastAPI, Groq/LLM backends, and a React + Vite frontend focused on clarity and
                  transparency.
                </p>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      <AnimatePresence>
        {showAdmin && (
          <motion.div
            className="about-backdrop"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={() => setShowAdmin(false)}
          >
            <motion.div
              className="about-modal"
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              onClick={(e) => e.stopPropagation()}
            >
              <header className="about-modal-header">
                <h2>Admin metrics</h2>
                <button type="button" onClick={() => setShowAdmin(false)} aria-label="Close admin">
                  <LuX size={18} />
                </button>
              </header>
              <div className="about-modal-body">
                {loadingAdmin && <p>Loading usage stats...</p>}
                {!loadingAdmin && !adminMetrics && (
                  <button
                    type="button"
                    className="about-btn"
                    onClick={async () => {
                      try {
                        setLoadingAdmin(true);
                        const metrics = await (await import("./utils/api.js")).getAdminMetrics();
                        setAdminMetrics(metrics);
                      } catch (error) {
                        console.error("Failed to load admin metrics", error);
                      } finally {
                        setLoadingAdmin(false);
                      }
                    }}
                  >
                    Load stats
                  </button>
                )}
                {!loadingAdmin && adminMetrics && (
                  <>
                    <p>Total conversations: {adminMetrics.total_conversations}</p>
                    <p>Documents indexed: {adminMetrics.documents_indexed}</p>
                    <p>Total questions asked: {adminMetrics.total_queries}</p>
                    <p className="about-meta">Last reset at: {adminMetrics.generated_at}</p>
                  </>
                )}
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
