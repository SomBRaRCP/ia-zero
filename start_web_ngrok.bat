@echo off
setlocal

REM Ativa o venv
if exist .venv\Scripts\activate.bat (
    call .venv\Scripts\activate.bat
) else (
    echo Nao encontrei .venv\Scripts\activate.bat
    echo Ative manualmente o ambiente virtual.
    pause
    exit /b 1
)

REM Executa script Python que gerencia ngrok + servidor + navegador
python start_ngrok_public.py

endlocal