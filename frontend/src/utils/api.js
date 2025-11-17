import axios from "axios";

// Get backend URL from environment or default
// In Docker, frontend is served by nginx, so we need to use the host's backend URL
// For local dev, use localhost
const getBackendUrl = () => {
  if (import.meta.env.VITE_BACKEND_URL) {
    return import.meta.env.VITE_BACKEND_URL;
  }
  // In production/Docker, backend is on same host but different port
  // In local dev, use localhost
  if (window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1") {
    return "http://localhost:8000";
  }
  // For Docker/production, construct URL from current host
  const protocol = window.location.protocol;
  const hostname = window.location.hostname;
  return `${protocol}//${hostname}:8000`;
};

const API_URL = getBackendUrl();

const client = axios.create({
  baseURL: API_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

export const initConversation = async () => {
  const { data } = await client.post("/conversation/init");
  return data.conversation_id;
};

export const uploadDocument = async ({ file, conversationId }) => {
  const formData = new FormData();
  formData.append("file", file);
  if (conversationId) {
    formData.append("conversation_id", conversationId);
  }

  const { data } = await axios.post(`${API_URL}/upload`, formData, {
    headers: {
      "Content-Type": "multipart/form-data",
    },
  });
  return data;
};

export const askFollowUp = async ({ conversationId, question }) => {
  const { data } = await client.post("/chat", {
    conversation_id: conversationId,
    question,
  });
  return data;
};

export const getAdminMetrics = async () => {
  const { data } = await client.get("/admin/metrics");
  return data;
};

