@echo off
echo ========================================
echo    ساخت نسخه قابل حمل نرم‌افزار
echo ========================================
echo.

echo مرحله 1: نصب وابستگی‌ها...
pip install pyinstaller
pip install -r requirements.txt

echo.
echo مرحله 2: پاک کردن فایل‌های قبلی...
if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"

echo.
echo مرحله 3: ساخت فایل اجرایی...
pyinstaller app.spec

echo.
echo مرحله 4: کپی کردن فایل‌های اضافی...
if not exist "dist\LensWorkshop\database" mkdir "dist\LensWorkshop\database"
if exist "instance\database.db" copy "instance\database.db" "dist\LensWorkshop\database\"

echo.
echo مرحله 5: ایجاد فایل راه‌اندازی...
echo @echo off > "dist\LensWorkshop\start.bat"
echo echo ========================================== >> "dist\LensWorkshop\start.bat"
echo echo    نرم‌افزار مدیریت کارگاه عینک‌سازی >> "dist\LensWorkshop\start.bat"
echo echo ========================================== >> "dist\LensWorkshop\start.bat"
echo echo. >> "dist\LensWorkshop\start.bat"
echo echo در حال راه‌اندازی سرور... >> "dist\LensWorkshop\start.bat"
echo echo. >> "dist\LensWorkshop\start.bat"
echo echo پس از راه‌اندازی، مرورگر خود را باز کرده و به آدرس زیر بروید: >> "dist\LensWorkshop\start.bat"
echo echo http://localhost:5000 >> "dist\LensWorkshop\start.bat"
echo echo. >> "dist\LensWorkshop\start.bat"
echo echo برای خروج، این پنجره را ببندید. >> "dist\LensWorkshop\start.bat"
echo echo. >> "dist\LensWorkshop\start.bat"
echo LensWorkshop.exe >> "dist\LensWorkshop\start.bat"
echo pause >> "dist\LensWorkshop\start.bat"

echo.
echo مرحله 6: ایجاد فایل راهنما...
echo ========================================== > "dist\LensWorkshop\README.txt"
echo    نرم‌افزار مدیریت کارگاه عینک‌سازی >> "dist\LensWorkshop\README.txt"
echo ========================================== >> "dist\LensWorkshop\README.txt"
echo. >> "dist\LensWorkshop\README.txt"
echo نحوه استفاده: >> "dist\LensWorkshop\README.txt"
echo 1. فایل start.bat را اجرا کنید >> "dist\LensWorkshop\README.txt"
echo 2. مرورگر خود را باز کرده و به آدرس http://localhost:5000 بروید >> "dist\LensWorkshop\README.txt"
echo 3. با نام کاربری admin و رمز عبور admin وارد شوید >> "dist\LensWorkshop\README.txt"
echo. >> "dist\LensWorkshop\README.txt"
echo نکات مهم: >> "dist\LensWorkshop\README.txt"
echo - این نرم‌افزار نیازی به اینترنت ندارد >> "dist\LensWorkshop\README.txt"
echo - تمام اطلاعات در پوشه database ذخیره می‌شود >> "dist\LensWorkshop\README.txt"
echo - برای پشتیبان‌گیری، پوشه database را کپی کنید >> "dist\LensWorkshop\README.txt"
echo - برای انتقال به سیستم دیگر، کل پوشه را کپی کنید >> "dist\LensWorkshop\README.txt"

echo.
echo ========================================
echo ✅ ساخت نسخه قابل حمل تکمیل شد!
echo ========================================
echo.
echo فایل‌های آماده در پوشه: dist\LensWorkshop
echo برای اجرا: start.bat را دابل کلیک کنید
echo.
pause
