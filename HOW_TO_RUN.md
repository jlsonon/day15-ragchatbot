# How to Run - AI Business & Research Adviser

## 🚀 Quick Start (Choose One Method)

---

## Method 1: Docker Compose (Easiest - Recommended)

### Step 1: Get a Groq API Key (Optional but Recommended)
1. Visit https://console.groq.com
2. Sign up/login
3. Create an API key (starts with `gsk_`)

### Step 2: Create Environment File
```bash
cd "/Users/jlsonon/Downloads/day 15"
echo "GROQ_API_KEY=your_groq_api_key_here" > .env
echo "GROQ_MODEL=llama3-70b-8192" >> .env
```

**Important:** Replace `your_groq_api_key_here` with your actual API key. The format must be:
```
GROQ_API_KEY=gsk_your_actual_key_here
```

**Note:** Replace `your_groq_api_key_here` with your actual API key. The app will work without it but with limited functionality.

### Step 3: Start the Application
```bash
docker compose up --build
```

### Step 4: Access the App
- **Frontend (Web UI):** http://localhost:3000
- **Backend API:** http://localhost:8000
- **Health Check:** http://localhost:8000/health

### To Stop:
Press `Ctrl+C` in the terminal, then:
```bash
docker compose down
```

---

## Method 2: Manual Setup (Development Mode)

### Prerequisites
- Python 3.11+ installed
- Node.js 18+ installed
- Groq API key (optional)

### Step 1: Setup Backend

**Open Terminal 1:**
```bash
cd "/Users/jlsonon/Downloads/day 15/backend"

# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate

# Install dependencies
pip install -r app/requirements.txt

# Create .env file
echo "GROQ_API_KEY=your_groq_api_key_here" > .env
echo "GROQ_MODEL=llama3-70b-8192" >> .env

# Start backend server
uvicorn app.main:app --reload
```

You should see: `Uvicorn running on http://0.0.0.0:8000`

### Step 2: Setup Frontend

**Open Terminal 2 (new terminal window):**
```bash
cd "/Users/jlsonon/Downloads/day 15/frontend"

# Install dependencies
npm install

# Start development server
npm run dev
```

You should see: `Local: http://localhost:5173/`

### Step 3: Access the App
- **Frontend:** http://localhost:5173
- **Backend API:** http://localhost:8000

---

## 🧪 Testing the Application

1. **Open the frontend** in your browser (http://localhost:3000 or http://localhost:5173)

2. **Upload a document:**
   - Drag & drop a PDF, DOCX, or TXT file
   - Or click "browse" to select a file
   - Supported: Reports, research papers, market studies, business documents

3. **Ask a question:**
   - Enter a question like: "What are the key opportunities?" or "What trends should I know?"
   - Click "Analyze"

4. **View results:**
   - See the executive summary
   - Check key findings and insights
   - Explore the insight radar chart
   - Review strategic recommendations

5. **Ask follow-up questions:**
   - Use the chat interface to dive deeper
   - Ask questions like: "What are the main opportunities?" or "Summarize the trends"

---

## 🔍 Troubleshooting

### Backend Not Starting?

**Check if port 8000 is available:**
```bash
lsof -i :8000
```

**Check backend logs for errors:**
- Look for messages like `GROQ_API_KEY not set` (this is OK, app works in fallback mode)
- Look for import errors or missing dependencies

**Test backend health:**
```bash
curl http://localhost:8000/health
```

Should return: `{"status":"ok","service":"AI Business & Research Adviser"}`

### Frontend Not Starting?

**Check if port 5173 (or 3000) is available:**
```bash
lsof -i :5173
lsof -i :3000
```

**Clear node_modules and reinstall:**
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### API Key Issues?

**Test your Groq API key:**
```bash
curl https://api.groq.com/openai/v1/models \
  -H "Authorization: Bearer YOUR_API_KEY"
```

**Check if API key is loaded:**
- Backend logs will show: `GROQ_API_KEY not set` if missing
- Check your `.env` file is in the correct location:
  - For Docker: root directory (`/Users/jlsonon/Downloads/day 15/.env`)
  - For manual: backend directory (`/Users/jlsonon/Downloads/day 15/backend/.env`)

### Docker Issues?

**Rebuild containers:**
```bash
docker compose down
docker compose up --build
```

**Check Docker logs:**
```bash
docker compose logs backend
docker compose logs frontend
```

---

## 📝 Environment Variables

| Variable | Location | Description | Required |
|----------|----------|-------------|----------|
| `GROQ_API_KEY` | Backend | Your Groq API key | No (app works without it) |
| `GROQ_MODEL` | Backend | Model name (default: `llama3-70b-8192`) | No |
| `VITE_BACKEND_URL` | Frontend | Backend URL (auto-detected) | No |

---

## ✅ Quick Verification Checklist

- [ ] Backend running on port 8000
- [ ] Frontend running on port 5173 (dev) or 3000 (Docker)
- [ ] Health check returns OK: `curl http://localhost:8000/health`
- [ ] Can access frontend in browser
- [ ] Can upload a document
- [ ] Can see analysis results (even without API key)

---

## 🎯 Next Steps

1. **Get a Groq API key** for full AI-powered analysis
2. **Upload a business document** (PDF, DOCX, or TXT)
3. **Ask questions** and explore insights
4. **Try follow-up questions** in the chat interface

The app works in fallback mode without an API key, but you'll get much better, AI-powered insights with a valid Groq API key!

---

## 💡 Tips

- **Without API key:** App uses heuristic analysis (basic pattern matching)
- **With API key:** Full AI-powered analysis with deep insights
- **Best documents:** Business reports, research papers, market studies, strategic plans
- **File size limit:** Up to 20MB
- **Supported formats:** PDF, DOCX, TXT

