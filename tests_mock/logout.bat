@echo off
setlocal EnableDelayedExpansion

set BASE_URL=http://127.0.0.1:8000
set TOKEN=%1
set AUTH=Authorization: Session %TOKEN%

echo ===== LOGOUT =====
curl -s -X POST %BASE_URL%/api/auth/logout/ ^
 -H "%AUTH%" ^
echo.