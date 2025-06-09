@echo off
REM نصب وابستگی‌ها در محیط مجازی (در صورت وجود)
IF EXIST .venv (
    call .venv\Scripts\activate
) ELSE (
    echo محیط مجازی پیدا نشد. لطفاً ابتدا محیط مجازی بسازید.
)
pip install --upgrade pip
pip install -r requirements.txt
pause 