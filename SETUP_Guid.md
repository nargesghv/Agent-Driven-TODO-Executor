# Web Interface Setup Guide

## Quick Start for New Users

### 1. Clone the Project
```bash
git clone <your-repository-url>
cd Agent-Driven-TODO-Executor
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Add Your OpenAI API Key
Create a `.env` file in the project root:
```
OPENAI_API_KEY=your-api-key-here
```

Or edit `config.py` and paste your key directly.

### 4. Start the Backend
```bash
python backend.py
```

You should see:
```
============================================================
Agent TODO Executor Backend
============================================================
Backend API: http://localhost:8007
```

### 5. Open the Frontend
- Open `frontend.html` in your browser
- Or visit: `file:///path/to/your/project/frontend.html`

**That's it** Start chatting with the agent. 

---

## Troubleshooting Common Issues

### Issue 1: Backend Won't Start

**Error:** `ModuleNotFoundError: No module named 'fastapi'`

**Solution:**
```bash
pip install -r requirements.txt
```

---

### Issue 2: "Session Not Found" After Edit

**Solution:** Restart the backend after making code changes:
1. Stop backend (Ctrl+C)
2. Start again: `python backend.py`
3. Refresh browser (Ctrl+Shift+R)

---

### Issue 3: Connection Errors on Windows

**Error:** `ConnectionResetError: [WinError 10054]`

**Solution:** Already fixed in the code. These warnings are harmless during WebSocket connections.

---

### Issue 4: OpenAI API Error

**Error:** `AuthenticationError` or `Invalid API key`

**Solution:**
1. Check your API key in `.env` or `config.py`
2. Verify the key is valid at https://platform.openai.com/api-keys
3. Restart backend after updating the key

---

## Advanced Configuration

### Change Port
Edit `backend.py`:
```python
port=8007  # Change this to your preferred port
```

### Change Model
Edit `config.py`:
```python
OPENAI_MODEL = "gpt-4o-mini"  # Or any other OpenAI model
```

---

## File Structure
```
project/
├── backend.py          # FastAPI backend
├── frontend.html       # Web interface
├── agent.py           # Core agent logic
├── llm.py             # OpenAI integration
├── todo.py            # Task management
├── config.py          # Configuration
└── requirements.txt   # Dependencies
```

---

## Need Help?

1. Check backend terminal for errors
2. Open browser console (F12) for frontend errors
3. Visit: `http://127.0.0.1:8007/api/debug/sessions` to see active sessions

**Still having issues?** Make sure:
- Backend is running
- API key is set
- All dependencies are installed
- Using Python 3.8+
