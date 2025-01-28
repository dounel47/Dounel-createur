@echo off
echo Iniciando servicios...

:: Iniciar MongoDB
start "" "C:\Program Files\MongoDB\Server\7.0\bin\mongod.exe" --dbpath C:\data\db

:: Esperar un momento para que MongoDB inicie
timeout /t 5 /nobreak > nul

:: Iniciar servidor Flask
cd /d "%~dp0"
python app.py

pause
