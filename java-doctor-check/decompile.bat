@echo off
setlocal enabledelayedexpansion

set "TOOLS_DIR=%~dp0"
set "CFR_JAR=%TOOLS_DIR%cfr.jar"
set "JADX_HOME=%TOOLS_DIR%jadx"
set "JAVA_CMD="

for %%P in ("C:\Program Files\Java\jdk-21" "C:\Program Files\Java\jdk-17" "C:\Program Files\Java\jdk-11" "C:\Program Files\Eclipse Adoptium\jdk-21*" "C:\Program Files\Eclipse Adoptium\jdk-17*" "C:\Program Files\Eclipse Adoptium\jdk-11*" "C:\Program Files\Amazon Corretto\jdk21*" "C:\Program Files\Amazon Corretto\jdk17*" "C:\Program Files\Amazon Corretto\jdk11*" "D:\dev\Java\jdk-21" "D:\dev\Java\jdk-17" "D:\dev\Java\jdk-11") do (
    for /d %%D in (%%P) do (
        if exist "%%D\bin\java.exe" (
            set "JAVA_CMD=%%D\bin\java.exe"
            goto :found
        )
    )
)

for %%P in ("C:\Program Files\Java\jdk1.8*" "D:\dev\Java\jdk1.8*" "D:\dev\java\jdk1.8*") do (
    for /d %%D in (%%P) do (
        if exist "%%D\bin\java.exe" (
            set "JAVA_CMD=%%D\bin\java.exe"
            goto :found
        )
    )
)

if defined JAVA_HOME (
    if exist "%JAVA_HOME%\bin\java.exe" (
        set "JAVA_CMD=%JAVA_HOME%\bin\java.exe"
        goto :found
    )
)

where java >nul 2>&1
if not errorlevel 1 (
    for /f "delims=" %%i in ('where java') do (
        set "JAVA_CMD=%%i"
        goto :found
    )
)

echo [ERROR] Java not found
exit /b 1

:found
for /f "usebackq tokens=3" %%v in (`"%JAVA_CMD%" -version 2^>^&1`) do (
    set "RAW=%%~v"
    goto :parse
)
:parse
if "%RAW:~0,2%"=="1." (set "MAJOR=%RAW:~2,1%") else (for /f "tokens=1 delims=." %%m in ("%RAW%") do set "MAJOR=%%m")
echo [INFO] Java=%JAVA_CMD% ver=%RAW% major=%MAJOR%

set "JVM=-Xms128M -Xmx512M"
if defined MAJOR if !MAJOR! GEQ 11 set "JVM=-Xms128M -XX:MaxRAMPercentage=70.0 -XX:+UseG1GC"

set "TOOL=%~1"
if "%TOOL%"=="" (echo Usage: decompile [cfr^|jadx^|jadx-gui^|javap^|info] [args...] ^& exit /b 0)
shift

if /i "%TOOL%"=="info" (
    echo CFR=%CFR_JAR%
    if exist "%CFR_JAR%" (echo   [OK]) else (echo   [NOT FOUND])
    echo JADX=%JADX_HOME%
    if exist "%JADX_HOME%\bin\jadx.bat" (echo   [OK]) else (echo   [NOT FOUND])
    exit /b 0
)

if /i "%TOOL%"=="cfr" (
    if not exist "%CFR_JAR%" (echo [ERROR] CFR not found ^& exit /b 1)
    "%JAVA_CMD%" %JVM% -jar "%CFR_JAR%" %1 %2 %3 %4 %5 %6 %7 %8 %9
    exit /b !ERRORLEVEL!
)

if /i "%TOOL%"=="jadx" (
    if not exist "%JADX_HOME%\bin\jadx.bat" (echo [ERROR] JADX not found ^& exit /b 1)
    for %%i in ("%JAVA_CMD%") do set "JB=%%~dpi"
    for %%i in ("!JB!..") do set "JAVA_HOME=%%~fi"
    call "%JADX_HOME%\bin\jadx.bat" %1 %2 %3 %4 %5 %6 %7 %8 %9
    exit /b !ERRORLEVEL!
)

if /i "%TOOL%"=="jadx-gui" (
    if not exist "%JADX_HOME%\bin\jadx-gui.bat" (echo [ERROR] JADX GUI not found ^& exit /b 1)
    for %%i in ("%JAVA_CMD%") do set "JB=%%~dpi"
    for %%i in ("!JB!..") do set "JAVA_HOME=%%~fi"
    start "" "%JADX_HOME%\bin\jadx-gui.bat" %1 %2 %3 %4 %5 %6 %7 %8 %9
    exit /b 0
)

if /i "%TOOL%"=="javap" (
    for %%i in ("%JAVA_CMD%") do set "JAVAP=%%~dpijavap.exe"
    "!JAVAP!" %1 %2 %3 %4 %5 %6 %7 %8 %9
    exit /b !ERRORLEVEL!
)

echo [ERROR] Unknown tool: %TOOL%
exit /b 1
