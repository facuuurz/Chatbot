@echo off
title NASA Explorer Bot - Launcher
color 0B

echo.
echo  ===================================================
echo   🚀 NASA Explorer Bot — Iniciando...
echo  ===================================================
echo.

:: Activar el entorno virtual
call .\venv\Scripts\activate

echo  [1/2] Iniciando servidor de acciones en :5055...
start "Action Server" cmd /k "call .\venv\Scripts\activate && python -m rasa run actions"

timeout /t 3 /nobreak >nul

echo  [2/2] Iniciando Rasa con CORS habilitado en :5005...
start "Rasa Server" cmd /k "call .\venv\Scripts\activate && set PYTHONIOENCODING=utf-8 && python -m rasa run --cors * --enable-api"

timeout /t 5 /nobreak >nul

echo.
echo  ===================================================
echo   ✅ Servidores iniciados. Abriendo interfaz...
echo  ===================================================
echo.

:: Abrir el chat en el navegador
start "" "chat.html"

echo  Podés cerrar esta ventana.
pause
