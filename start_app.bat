@echo off
echo Starting NIMbleRAG (Backend and Frontend)...

:: Get the directory of the script and build the path to the local environment
set "ENV_PATH=%~dp0nvidia-nim"

:: Start the FastAPI backend in a new command window
echo Launching FastAPI Backend...
start "FastAPI Backend" cmd /k "conda activate "%ENV_PATH%" && uvicorn backend.api.main:app --reload"

:: Start the Streamlit frontend in a new command window
echo Launching Streamlit Frontend...
start "Streamlit Frontend" cmd /k "conda activate "%ENV_PATH%" && streamlit run frontend/app.py"

echo Success! Both services are launching in separate windows.
