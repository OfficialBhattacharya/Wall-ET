@echo off
echo ======================================
echo StockPicker GitHub Push Utility
echo ======================================
echo.

python utils\github_push.py %*

echo.
echo Press any key to exit...
pause > nul 