@echo off
setlocal enabledelayedexpansion

echo ===================================================
echo        Athkar Reminder - Standalone Compiler
echo ===================================================
echo.

:: Check if Python is installed
where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Python is not installed or not in PATH.
    echo Please install Python and try again.
    goto :error
)

:: Check Python version
for /f "tokens=2" %%V in ('python --version 2^>^&1') do set PYTHON_VERSION=%%V
echo [INFO] Using Python version: %PYTHON_VERSION%

:: Check if requirements.txt exists
if not exist requirements.txt (
    echo [INFO] Creating requirements.txt file...
    echo pillow>=9.0.0 > requirements.txt
    echo pystray>=0.19.0 >> requirements.txt
    echo pywin32>=300 ; sys_platform == 'win32' >> requirements.txt
    echo win10toast>=0.9 ; sys_platform == 'win32' >> requirements.txt
)

:: Install all required dependencies
echo [INFO] Installing all required dependencies...
python -m pip install -r requirements.txt
if %ERRORLEVEL% neq 0 (
    echo [WARNING] Some dependencies might not have installed correctly.
    echo The application may still compile but might have issues.
    set /p CONTINUE="Continue anyway? (y/n): "
    if /i "!CONTINUE!" neq "y" goto :error
)

:: Check if PyInstaller is installed
python -c "import PyInstaller" >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [INFO] Installing PyInstaller...
    python -m pip install pyinstaller
    if %ERRORLEVEL% neq 0 (
        echo [ERROR] Failed to install PyInstaller.
        goto :error
    )
)

:: Clean build directories
echo [INFO] Cleaning previous build files...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

:: Check if icon.ico exists
if exist icon.ico (
    echo [INFO] Using icon.ico for the application...
)

:: Run PyInstaller directly without using spec file
echo [INFO] Building standalone application with PyInstaller...

if exist icon.ico (
    python -m PyInstaller --clean --noconfirm --onefile --windowed --name "Athkar Reminder" ^
        --icon=icon.ico ^
        --add-data "duaas.json;." ^
        --add-data "settings.json;." ^
        --add-data "languages.py;." ^
        --add-data "version.py;." ^
        --hidden-import PIL ^
        --hidden-import PIL.Image ^
        --hidden-import PIL.ImageTk ^
        --hidden-import PIL.ImageDraw ^
        --hidden-import pystray ^
        --hidden-import win10toast ^
        --hidden-import winreg ^
        --hidden-import win32api ^
        --hidden-import win32gui ^
        --hidden-import win32con ^
        --hidden-import pystray._win32 ^
        athkar_reminder.py
) else (
    python -m PyInstaller --clean --noconfirm --onefile --windowed --name "Athkar Reminder" ^
        --add-data "duaas.json;." ^
        --add-data "settings.json;." ^
        --add-data "languages.py;." ^
        --add-data "version.py;." ^
        --hidden-import PIL ^
        --hidden-import PIL.Image ^
        --hidden-import PIL.ImageTk ^
        --hidden-import PIL.ImageDraw ^
        --hidden-import pystray ^
        --hidden-import win10toast ^
        --hidden-import winreg ^
        --hidden-import win32api ^
        --hidden-import win32gui ^
        --hidden-import win32con ^
        --hidden-import pystray._win32 ^
        athkar_reminder.py
)
if %ERRORLEVEL% neq 0 (
    echo [ERROR] PyInstaller build failed.
    goto :error
)

:: Verify the build
if exist "dist\Athkar Reminder.exe" (
    echo [INFO] Single-file executable found.
) else if exist "dist\Athkar Reminder\Athkar Reminder.exe" (
    echo [INFO] Folder-based executable found.
    echo [INFO] The application was built as a folder instead of a single file.
) else (
    echo [ERROR] Build failed - executable not found.
    goto :error
)

:: Create a simple test batch file in the dist folder
if exist "dist\Athkar Reminder.exe" (
    :: For single-file build
    echo @echo off > "dist\test_app.bat"
    echo echo Testing Athkar Reminder application... >> "dist\test_app.bat"
    echo echo If the application opens without errors, it is working correctly. >> "dist\test_app.bat"
    echo echo Close the application after testing. >> "dist\test_app.bat"
    echo echo. >> "dist\test_app.bat"
    echo echo Press any key to start the test... >> "dist\test_app.bat"
    echo pause > nul >> "dist\test_app.bat"
    echo start "" "Athkar Reminder.exe" >> "dist\test_app.bat"
    echo echo. >> "dist\test_app.bat"
    echo echo Test complete. Press any key to exit... >> "dist\test_app.bat"
    echo pause > nul >> "dist\test_app.bat"
) else (
    :: For folder-based build
    echo @echo off > "dist\Athkar Reminder\test_app.bat"
    echo echo Testing Athkar Reminder application... >> "dist\Athkar Reminder\test_app.bat"
    echo echo If the application opens without errors, it is working correctly. >> "dist\Athkar Reminder\test_app.bat"
    echo echo Close the application after testing. >> "dist\Athkar Reminder\test_app.bat"
    echo echo. >> "dist\Athkar Reminder\test_app.bat"
    echo echo Press any key to start the test... >> "dist\Athkar Reminder\test_app.bat"
    echo pause > nul >> "dist\Athkar Reminder\test_app.bat"
    echo start "" "Athkar Reminder.exe" >> "dist\Athkar Reminder\test_app.bat"
    echo echo. >> "dist\Athkar Reminder\test_app.bat"
    echo echo Test complete. Press any key to exit... >> "dist\Athkar Reminder\test_app.bat"
    echo pause > nul >> "dist\Athkar Reminder\test_app.bat"
)

echo.
echo ===================================================
echo        Compilation Completed Successfully!
echo ===================================================
echo.

if exist "dist\Athkar Reminder.exe" (
    echo Standalone application has been built and saved to:
    echo dist\Athkar Reminder.exe
    echo.
    echo You can distribute this single executable file to users.
    echo No additional installations are required.
    echo.
    echo To test the application, run test_app.bat in the dist folder.
) else (
    echo Application has been built and saved to:
    echo dist\Athkar Reminder\
    echo.
    echo You can distribute the entire "Athkar Reminder" folder to users.
    echo No additional installations are required.
    echo.
    echo To test the application, run test_app.bat in the Athkar Reminder folder.
)
echo.
goto :end

:error
echo.
echo ===================================================
echo        Compilation Failed!
echo ===================================================
echo.
exit /b 1

:end
echo Press any key to exit...
pause > nul
exit /b 0
