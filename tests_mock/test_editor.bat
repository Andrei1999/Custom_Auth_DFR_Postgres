@echo off
call common.bat editor@example.com Editor123
if errorlevel 1 exit /b

set AUTH=Authorization: Session %TOKEN%

echo.
echo ===== EDITOR TESTS =====

echo [1] PROJECTS READ
curl -i %BASE_URL%/api/mock/projects/ -H "%AUTH%"

echo.
echo.
echo [2] PROJECT CREATE (OK)
curl -i -X POST %BASE_URL%/api/mock/projects/ ^
 -H "%AUTH%" ^
 -H "Content-Type: application/json" ^
 -d "{\"name\":\"Editor project\"}"

echo.
echo.
echo [3] REPORT GENERATE (OK)
curl -i -X POST %BASE_URL%/api/mock/reports/ ^
 -H "%AUTH%" ^
 -H "Content-Type: application/json" ^
 -d "{\"type\":\"editor\"}"

echo.
echo.
echo [4] INVOICES (403)
curl -i %BASE_URL%/api/mock/invoices/ -H "%AUTH%"

echo.
echo.
echo ==== EDITOR TESTS DONE ====
pause