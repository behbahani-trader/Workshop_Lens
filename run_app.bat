@echo off
REM فعال‌سازی محیط مجازی
IF EXIST .venv (
    call .venv\Scripts\activate
) ELSE (
    echo محیط مجازی پیدا نشد. لطفاً ابتدا محیط مجازی را بسازید و وابستگی‌ها را نصب کنید.
    pause
    exit /b
)
REM اجرای برنامه
python run.py
pause 