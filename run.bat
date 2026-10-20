@echo off
chcp 65001 >nul
title TOOL TIKTOK AFFILIATE & REUP AUTOMATION

echo ===============================================================================
echo     TOOL TIKTOK AFFILIATE & REUP AUTOMATION - TU DONG CAI DAT & KHOI DONG
echo ===============================================================================
echo.

cd /d "%~dp0"

:: 1. Kiem tra Python
where python >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    where py >nul 2>&1
    if %ERRORLEVEL% NEQ 0 (
        echo [LOI] Khong tim thay Python tren may tinh cua ban!
        echo.
        echo HUONG DAN CAI DAT:
        echo 1. Truy cap: https://www.python.org/downloads/
        echo 2. Tai ban cai dat Python 3.10 tro len.
        echo 3. LUU Y QUAN TRONG: Tich chon vao o "Add Python to PATH" truoc khi bam Install!
        echo 4. Sau khi cai xong, mo lai file run.bat nay.
        echo.
        pause
        exit /b 1
    ) else (
        set PYTHON_CMD=py -3
    )
) else (
    set PYTHON_CMD=python
)

echo [1/5] Kiem tra moi truong Python...
%PYTHON_CMD% --version
if %ERRORLEVEL% NEQ 0 (
    echo [LOI] Khong the thuc thi lenh Python. Vui long kiem tra lai bien moi truong PATH.
    pause
    exit /b 1
)

:: 2. Kiem tra va khoi tao moi truong ao (.venv)
if not exist ".venv\Scripts\activate.bat" (
    echo [2/5] Chua co moi truong ao .venv. Dang tu dong tao moi truong ao...
    %PYTHON_CMD% -m venv .venv
    if %ERRORLEVEL% NEQ 0 (
        echo [CANH BAO] Khong the tao .venv. Se su dung Python truc tiep cua he thong.
        set VENV_PYTHON=%PYTHON_CMD%
    ) else (
        echo [+] Da tao thanh cong moi truong ao .venv!
        call .venv\Scripts\activate.bat
        set VENV_PYTHON=python
    )
) else (
    echo [2/5] Kich hoat moi truong ao .venv...
    call .venv\Scripts\activate.bat
    set VENV_PYTHON=python
)

:: 3. Cai dat thu vien tu requirements.txt
echo [3/5] Kiem tra va cai dat cac thu vien can thiet (requirements.txt)...
%VENV_PYTHON% -m pip install --upgrade pip --quiet
%VENV_PYTHON% -m pip install -r requirements.txt
if %ERRORLEVEL% NEQ 0 (
    echo [LOI] Cai dat thu vien that bai! Vui long kiem tra ket noi mang va thu lai.
    pause
    exit /b 1
)
echo [+] Thu vien Python da duoc cai dat day du!

:: 4. Tu dong cai dat Chromium Browser cho Playwright
echo [4/5] Kiem tra va tu dong cai dat Chromium (Playwright Browser)...
%VENV_PYTHON% -m playwright install chromium
if %ERRORLEVEL% NEQ 0 (
    echo [CANH BAO] Cai dat Chromium mac dinh gap loi, dang thu cai kem dependencies...
    %VENV_PYTHON% -m playwright install chromium --with-deps
)
echo [+] Trinh duyet Chromium da duoc cai dat va san sang su dung!

:: 5. Kiem tra file cau hinh .env
echo [5/5] Kiem tra file cau hinh .env...
if not exist ".env" (
    if exist ".env.example" (
        copy .env.example .env >nul
        echo [+] Da tu dong tao file .env tu file mau .env.example.
        echo [!] CHU Y: Vui long mo file .env de dien GEMINI_API_KEY cua ban.
    )
)

findstr /C:"GEMINI_API_KEY=" .env >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [CANH BAO] File .env chua co GEMINI_API_KEY! Hay chac chan ban da them API key.
)

echo.
echo ===============================================================================
echo     TAT CA MOI TRUONG DA SAN SANG! DANG KHOI CHAY CHUONG TRINH...
echo ===============================================================================
echo.

%VENV_PYTHON% main.py %*

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [THONG BAO] Tien trinh da dung voi ma loi: %ERRORLEVEL%
    pause
)
