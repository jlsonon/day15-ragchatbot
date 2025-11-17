# Quick Start Guide - Legal & Contract Analyzer

## ✅ All Issues Fixed!

I've fixed all the critical issues in your codebase:

1. ✅ Added `pydantic` to requirements.txt
2. ✅ Fixed RiskChart type inconsistency (polar vs bar charts)
3. ✅ Fixed Docker frontend environment variable handling
4. ✅ Improved .env file loading in backend
5. ✅ Added health check endpoint
6. ✅ Fixed API URL resolution for Docker and local dev
7. ✅ Enhanced error logging throughout

## 🚀 How to Run

### Option 1: Docker Compose (Recommended)

1. **Create `.env` file in the root directory:**
   ```bash
   cd "/Users/jlsonon/Downloads/day 15"
   echo "GROQ_API_KEY=your_groq_api_key_here" > .env
   echo "GROQ_MODEL=llama3-70b-8192" >> .env
   ```

2. **Start everything:**
   ```bash
   docker compose up --build
   ```

3. **Access the app:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - Health Check: http://localhost:8000/health

### Option 2: Manual Setup (Development)

**Terminal 1 - Backend:**
```bash
cd "/Users/jlsonon/Downloads/day 15/backend"
python3 -m venv .venv
source .venv/bin/activate
pip install -r app/requirements.txt

# Create .env file
echo "GROQ_API_KEY=your_groq_api_key_here" > .env
echo "GROQ_MODEL=llama3-70b-8192" >> .env

# Run server
uvicorn app.main:app --reload
```

**Terminal 2 - Frontend:**
```bash
cd "/Users/jlsonon/Downloads/day 15/frontend"
npm install
npm run dev
```

Then access: http://localhost:5173

## 🔍 Troubleshooting

### Check Backend Logs
The backend now logs detailed error messages. Look for:
- `GROQ_API_KEY not set` - API key missing
- `Groq API error: 401` - Invalid API key
- `Groq API error: 429` - Rate limit
- `Groq API timeout` - Network issue

### Test Backend Health
```bash
curl http://localhost:8000/health
```

### Verify API Key
```bash
# Check if it's loaded
curl http://localhost:8000/health

# Test Groq API directly
curl https://api.groq.com/openai/v1/models \
  -H "Authorization: Bearer YOUR_API_KEY"
```

## 📝 Key Fixes Made

1. **Environment Variables**: Backend now properly loads `.env` from multiple locations
2. **Frontend API URL**: Automatically detects Docker vs local dev environment
3. **Chart Rendering**: Fixed polar chart type handling in RiskChart component
4. **Error Logging**: All API errors are now logged with details
5. **Docker Build**: Frontend now properly receives build-time environment variables

## 🎯 Next Steps

1. Get a Groq API key from https://console.groq.com
2. Add it to your `.env` file
3. Restart the backend/Docker containers
4. Upload a contract and test!

The app will work in fallback mode without an API key, but you'll get much better results with a valid Groq API key.

