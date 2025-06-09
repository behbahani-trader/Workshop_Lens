@echo off
echo ==========================================
echo    Building Portable Version
echo ==========================================
echo.

echo Step 1: Installing PyInstaller...
pip install pyinstaller

echo.
echo Step 2: Cleaning previous builds...
if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"

echo.
echo Step 3: Building executable...
pyinstaller --onefile --add-data "app/templates;app/templates" --add-data "app/static;app/static" --add-data "instance;instance" --name "LensWorkshop" run.py

echo.
echo Step 4: Creating portable folder...
mkdir "dist\LensWorkshop_Portable"
move "dist\LensWorkshop.exe" "dist\LensWorkshop_Portable\"

echo.
echo Step 5: Creating startup script...
echo @echo off > "dist\LensWorkshop_Portable\start.bat"
echo echo ========================================== >> "dist\LensWorkshop_Portable\start.bat"
echo echo    Lens Workshop Management System >> "dist\LensWorkshop_Portable\start.bat"
echo echo ========================================== >> "dist\LensWorkshop_Portable\start.bat"
echo echo. >> "dist\LensWorkshop_Portable\start.bat"
echo echo Starting server... >> "dist\LensWorkshop_Portable\start.bat"
echo echo. >> "dist\LensWorkshop_Portable\start.bat"
echo echo After startup, open your browser and go to: >> "dist\LensWorkshop_Portable\start.bat"
echo echo http://localhost:5000 >> "dist\LensWorkshop_Portable\start.bat"
echo echo. >> "dist\LensWorkshop_Portable\start.bat"
echo echo Login: admin / admin >> "dist\LensWorkshop_Portable\start.bat"
echo echo. >> "dist\LensWorkshop_Portable\start.bat"
echo echo To exit, close this window. >> "dist\LensWorkshop_Portable\start.bat"
echo echo. >> "dist\LensWorkshop_Portable\start.bat"
echo LensWorkshop.exe >> "dist\LensWorkshop_Portable\start.bat"
echo pause >> "dist\LensWorkshop_Portable\start.bat"

echo.
echo Step 6: Creating README file...
echo ========================================== > "dist\LensWorkshop_Portable\README.txt"
echo    Lens Workshop Management System >> "dist\LensWorkshop_Portable\README.txt"
echo ========================================== >> "dist\LensWorkshop_Portable\README.txt"
echo. >> "dist\LensWorkshop_Portable\README.txt"
echo How to use: >> "dist\LensWorkshop_Portable\README.txt"
echo 1. Double-click start.bat >> "dist\LensWorkshop_Portable\README.txt"
echo 2. Open browser and go to http://localhost:5000 >> "dist\LensWorkshop_Portable\README.txt"
echo 3. Login with admin/admin >> "dist\LensWorkshop_Portable\README.txt"
echo. >> "dist\LensWorkshop_Portable\README.txt"
echo Important notes: >> "dist\LensWorkshop_Portable\README.txt"
echo - No internet connection required >> "dist\LensWorkshop_Portable\README.txt"
echo - All data is stored locally >> "dist\LensWorkshop_Portable\README.txt"
echo - Use Reports section for backup >> "dist\LensWorkshop_Portable\README.txt"
echo - Copy entire folder to transfer to another system >> "dist\LensWorkshop_Portable\README.txt"

echo.
echo Step 7: Copying database...
if exist "instance\database.db" (
    copy "instance\database.db" "dist\LensWorkshop_Portable\"
)

echo.
echo ==========================================
echo Build completed successfully!
echo ==========================================
echo.
echo Files location: dist\LensWorkshop_Portable
echo To run: Double-click start.bat
echo To transfer: Copy entire LensWorkshop_Portable folder
echo.
echo This folder can be run on any Windows system without installation!
echo.
pause
