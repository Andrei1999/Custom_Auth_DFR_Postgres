@echo off
setlocal EnableDelayedExpansion
chcp 65001 > nul
set BASE_URL=http://127.0.0.1:8000

:: ===== LOGIN FUNCTION =====
set EMAIL=%1
set PASSWORD=%2
set TOKEN=

echo.
echo ===== LOGIN: %EMAIL% PASSWORD: %PASSWORD% =====

curl -s -X POST %BASE_URL%/api/auth/login/ ^
 -H "Content-Type: application/json" ^
 -d "{\"email\":\"%EMAIL%\",\"password\":\"%PASSWORD%\"}" > response.txt

type response.txt
echo.

:: Парсим токен (очень простой способ)
for /f "usebackq delims=" %%i in (`powershell -Command "$json = Get-Content response.txt -Raw | ConvertFrom-Json; Write-Host $json.access_token"`) do set TOKEN=%%i
:: убираем кавычки

if "%TOKEN%"=="" (
    echo LOGIN FAILED
    exit /b 1
)

set TOKENcd=%TOKEN:"=%

if "%TOKEN%"=="" (
    echo LOGIN FAILED
    exit /b 1
)

del response.txt

echo TOKEN = %TOKEN%
endlocal & set TOKEN=%TOKEN% & set BASE_URL=%BASE_URL%
exit /b 0

