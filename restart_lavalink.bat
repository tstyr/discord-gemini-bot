@echo off
echo ========================================
echo   Lavalink Restart Script
echo ========================================
echo.

echo Stopping any running Lavalink instances...
taskkill /F /IM java.exe /FI "WINDOWTITLE eq Lavalink*" 2>nul
timeout /t 2 /nobreak >nul

echo.
echo Starting Lavalink with updated configuration...
cd lavalink
start "Lavalink" java -jar Lavalink.jar

echo.
echo ========================================
echo   Lavalink is starting...
echo   Check the Lavalink window for status
echo ========================================
echo.
echo Wait for: "Lavalink is ready to accept connections."
echo.
pause
