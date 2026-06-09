@echo off
title BarberApp - Servicio de Recordatorios WhatsApp
echo ========================================================
echo SERVICIO DE RECORDATORIOS INICIADO
echo ========================================================
echo Este programa revisara las citas cada 1 hora.
echo Por favor, minimiza esta ventana pero NO LA CIERRES.
echo Si cierras esta ventana, los mensajes no se enviaran.
echo ========================================================

cd /d "%~dp0"
:loop
echo [%date% %time%] Ejecutando revision de recordatorios...
call .\venv\Scripts\python.exe manage.py enviar_recordatorios

echo.
echo Esperando 1 hora (3600 segundos) para la siguiente revision...
timeout /t 3600 /nobreak
goto loop
