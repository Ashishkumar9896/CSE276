@echo off
echo ===============================================================
echo Starting Coaching Centre AI Chatbot (CSE276 AI CA Project)
echo ===============================================================
echo [1/2] Starting Backend (FastAPI on http://127.0.0.1:8000)...
start "Chatbot Backend (FastAPI)" cmd /k "cd /d "%~dp0" && .venv\Scripts\activate && uvicorn app.main:app --reload --port 8000"

echo [2/2] Starting Frontend (Vite on http://localhost:5173)...
start "Chatbot Frontend (React)" cmd /k "cd /d "%~dp0frontend" && npm run dev"

echo.
echo ===============================================================
echo Servers launched in separate windows!
echo - Website & Chatbot: http://localhost:5173
echo - Swagger API Docs:  http://127.0.0.1:8000/api/docs
echo ===============================================================

