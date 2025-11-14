# Quick Start Guide 🚀

Get the Data Cleaning Bot running in 5 minutes!

## Prerequisites
- Python 3.8+ installed
- Node.js 18+ installed
- Git

## 1️⃣ Clone & Navigate
```bash
cd data-cleaning-bot
```

## 2️⃣ Setup Backend (Terminal 1)
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Edit .env - add your OpenAI or Groq API key:
# OPENAI_API_KEY=sk-your-key-here
# or GROQ_API_KEY=gsk-your-key-here

# Start backend
python main.py
```
✅ Backend running on http://localhost:8000

## 3️⃣ Setup Frontend (Terminal 2)
```bash
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev
```
✅ Frontend running on http://localhost:3000

## 4️⃣ Test It Out
1. Open http://localhost:3000 in browser
2. Drag-drop or click to upload a CSV file
3. Wait for cleaning to complete
4. Download cleaned CSV, Python script, and view AI report

## 📝 Sample CSV to Test
Create `test.csv`:
```csv
Name, Age, Date, Salary
  John Doe  ,28, 2023-01-15, 50000
Jane Smith,35, 15/01/2023, 60000
john doe,28,2023-01-15,50000
,30,,55000
Bob Johnson,45, 1-15-2023, 75000
```

## ⚙️ Configuration

### Add Your API Key
Edit `backend/.env`:
```env
OPENAI_API_KEY=sk-your-actual-key
# or
GROQ_API_KEY=gsk-your-actual-key
AI_PROVIDER=openai  # or 'groq'
```

Get free API keys:
- **OpenAI:** https://platform.openai.com/api-keys
- **Groq:** https://console.groq.com

## 🔍 Verify Setup
```bash
# In a new terminal:
curl http://localhost:8000/health
# Should return: {"status":"ok"}
```

## 📚 Full Documentation
See [README.md](../README.md) for complete documentation.

## 🐛 Troubleshooting

### "Port already in use"
Backend is already running or port 8000 is taken.
```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9  # Linux/Mac
netstat -ano | findstr :8000   # Windows
```

### "Connection refused"
Frontend can't reach backend. Check:
- Backend is running (`python main.py`)
- `.env.local` in frontend has correct `NEXT_PUBLIC_API_URL=http://localhost:8000`

### "API key not found"
Add your API key to `backend/.env` and restart backend.

### CSV upload fails
- Try with smaller file first
- Check file is valid CSV
- Ensure no special characters in filename

## 🎯 Next Steps
- Modify cleaning pipeline in `backend/cleaning_logic.py`
- Customize UI in `frontend/components/`
- Deploy to Vercel (see README.md)

---

Happy cleaning! 🧹✨
