@echo off

call common.bat admin@example.com Admin123
if errorlevel 1 exit /b

set AUTH=Authorization: Session %TOKEN%

echo.
echo ===== ADMIN TESTS =====

echo [1] GET PROJECTS (EXPECT 200)
curl -i %BASE_URL%/api/mock/projects/ -H "%AUTH%"


echo.
echo.
echo [2] CREATE PROJECT (EXPECT 201)
curl -i -X POST %BASE_URL%/api/mock/projects/ ^
 -H "%AUTH%" ^
 -H "Content-Type: application/json" ^
 -d "{\"name\":\"Admin project\"}"

echo.
echo.
echo [3] GET REPORTS
curl -i %BASE_URL%/api/mock/reports/ -H "%AUTH%"

echo.
echo.
echo [4] GENERATE REPORT
curl -i -X POST %BASE_URL%/api/mock/reports/ ^
 -H "%AUTH%" ^
 -H "Content-Type: application/json" ^
 -d "{\"type\":\"admin\"}"

echo.
echo.
echo [5] GET INVOICES
curl -i %BASE_URL%/api/mock/invoices/ -H "%AUTH%"

echo.
echo.
call logout.bat %TOKEN%
echo.
echo.

echo ==== ADMIN TESTS DONE ====

pause