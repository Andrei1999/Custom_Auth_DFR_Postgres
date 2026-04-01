@echo off
call common.bat viewer@example.com Viewer123!
if errorlevel 1 exit /b

set AUTH=Authorization: Session %TOKEN%

echo.
echo ===== VIEWER TESTS =====

echo [1] GET PROJECTS (OK)
curl -i %BASE_URL%/api/mock/projects/ -H "%AUTH%"

echo.
echo.
echo [2] CREATE PROJECT (ожидаем 403)
curl -i -X POST %BASE_URL%/api/mock/projects/ ^
 -H "%AUTH%" ^
 -H "Content-Type: application/json" ^
 -d "{\"name\":\"Viewer project\"}"

echo.
echo.
echo [3] GET REPORTS (OK)
curl -i %BASE_URL%/api/mock/reports/ -H "%AUTH%"

echo.
echo.
echo [4] GENERATE REPORT (403)
curl -i -X POST %BASE_URL%/api/mock/reports/ ^
 -H "%AUTH%" ^
 -H "Content-Type: application/json" ^
 -d "{\"type\":\"viewer\"}"

echo.
echo.
echo [5] INVOICES (403 или нет доступа)
curl -i %BASE_URL%/api/mock/invoices/ -H "%AUTH%"

echo.
echo.
echo ==== VIEWER TESTS DONE ====
pause