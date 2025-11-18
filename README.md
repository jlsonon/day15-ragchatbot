# RAG Chatbot

A full-featured RAG (Retrieval-Augmented Generation) chatbot with semantic search, embeddings, and vector similarity. Upload documents and ask questions with AI-powered answers based on document content. Built with React and FastAPI, powered by Groq AI and sentence transformers.

## Features

- **Full RAG Implementation** – Semantic search using embeddings and vector similarity
- **Document Upload** – Upload PDF, DOCX, or TXT files
- **Smart Chunking** – Intelligent text chunking with overlap for better context
- **Embeddings** – Uses sentence transformers (all-MiniLM-L6-v2) for semantic understanding
- **Vector Search** – Cosine similarity-based retrieval of relevant document chunks
- **Conversation Memory** – Maintains context throughout your conversation
- **Fallback Support** – Falls back to keyword search if embeddings fail

## How It Works

1. **Upload** a document (PDF, DOCX, or TXT)
2. **Document Processing:**
   - Text is extracted and chunked intelligently (500 chars with 100 char overlap)
   - Each chunk is converted to embeddings using sentence transformers
   - Embeddings are stored for semantic search
3. **Ask questions:**
   - Your question is converted to an embedding
   - System finds most similar chunks using cosine similarity
   - Top 4 most relevant chunks are retrieved
4. **AI generates answers** based on the retrieved context with relevance scores

## Quick Start

### Option 1: Docker Compose (Recommended)

```bash
# Navigate to project directory
cd "/Users/jlsonon/Downloads/day 15"

# Create .env file with your Groq API key (optional)
echo "GROQ_API_KEY=your_groq_api_key_here" > .env
echo "GROQ_MODEL=llama3-70b-8192" >> .env

# Start the application
docker compose up --build
```

Access at:
- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000

### Option 2: Manual Setup

**Terminal 1 - Backend:**
```bash
cd "/Users/jlsonon/Downloads/day 15/backend"
python3 -m venv .venv
source .venv/bin/activate
pip install -r app/requirements.txt
echo "GROQ_API_KEY=your_key" > .env
uvicorn app.main:app --reload
```

**Terminal 2 - Frontend:**
```bash
cd "/Users/jlsonon/Downloads/day 15/frontend"
npm install
npm run dev
```

Access at: http://localhost:5173

**For detailed instructions, see [HOW_TO_RUN.md](./HOW_TO_RUN.md)**

## Environment Variables

| Variable | Location | Description | Required |
|----------|----------|-------------|----------|
| `GROQ_API_KEY` | Backend | Your Groq API key | No (app works without it) |
| `GROQ_MODEL` | Backend | Model name (default: `llama3-70b-8192`) | No |
| `VITE_BACKEND_URL` | Frontend | Backend URL (auto-detected) | No |

## API Endpoints

- `POST /conversation/init` - Initialize a new conversation
- `POST /upload` - Upload a document
- `POST /chat` - Send a chat message
- `GET /health` - Health check

## Architecture

- **Backend:** FastAPI with document parsing and full RAG pipeline
- **Frontend:** React with a simple chat interface
- **RAG Pipeline:**
  - **Embeddings:** Sentence Transformers (all-MiniLM-L6-v2)
  - **Vector Store:** In-memory numpy arrays with cosine similarity
  - **Retrieval:** Semantic search with relevance scoring
  - **Chunking:** Smart chunking with sentence boundary preservation
- **AI:** Groq API for text generation

## Tech Stack

- **Frontend:** React, Vite, Framer Motion
- **Backend:** FastAPI, Python 3.11+
- **AI:** Groq API
- **Embeddings:** sentence-transformers (all-MiniLM-L6-v2)
- **Vector Operations:** NumPy for cosine similarity
- **Document Parsing:** PyPDF2, python-docx

## Use Cases

- **Research Papers** – Ask questions about academic papers
- **Business Documents** – Query reports, contracts, or proposals
- **Study Materials** – Get answers from textbooks or notes
- **Any Text Document** – Upload and chat about any PDF, DOCX, or TXT file

## Notes

- The app works without a Groq API key but with limited functionality
- Get a free API key at: https://console.groq.com
- First document upload will download the embedding model (~80MB) - this is a one-time download
- Documents are automatically chunked and embedded for semantic search
- Conversation history is maintained in memory (not persisted)
- Embeddings are stored in memory (for production, consider a vector DB)

## RAG Features

**Semantic Search** - Uses embeddings to find semantically similar content, not just keywords  
**Relevance Scoring** - Shows similarity scores for retrieved chunks  
**Smart Chunking** - Preserves sentence boundaries and uses overlap for context  
**Fallback Support** - Falls back to keyword search if embeddings fail  
**Context-Aware** - Maintains conversation history for better answers  


## Deployment

The project is deployed and accessible at:

https://day15-ragchatbot-3wjbcmkjl-jlsonons-projects.vercel.app/

Simply open the link in any modern browser to access the live application.

## Future Enhancements

- Vector database integration (Pinecone, Weaviate, ChromaDB)
- Multiple document support with document-specific retrieval
- Conversation persistence to database
- Export chat history
- Hybrid search (semantic + keyword)
- Re-ranking of retrieved chunks
