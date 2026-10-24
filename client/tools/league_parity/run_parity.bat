@echo off
rem Build the standalone C++ league core and compare it with fresh Python reference output.
rem Usage: run_parity.bat <work dir>
setlocal
set WORK=%~1
if "%WORK%"=="" set WORK=%TEMP%\oddswell_league_parity
set HERE=%~dp0
set PY=C:\Users\reali\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe
if not exist "%WORK%" mkdir "%WORK%"
"%PY%" "%HERE%golden.py" --out "%WORK%" || exit /b 1
call "C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvars64.bat" >nul || exit /b 1
cl /nologo /std:c++17 /O2 /EHsc /W4 /fp:precise /Fe:"%WORK%\league_parity.exe" /Fo:"%WORK%\\" "%HERE%parity_main.cpp" "%HERE%..\..\OddsWell\Source\OddsWell\League\OddsWellLeagueCore.cpp" || exit /b 1
"%WORK%\league_parity.exe" "%WORK%"
