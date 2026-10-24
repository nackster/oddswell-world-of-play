@echo off
rem Build the economy check against the real league core and run it.
rem Usage: run_economy.bat <work dir> [seasons]
setlocal
set WORK=%~1
if "%WORK%"=="" set WORK=%TEMP%\oddswell_economy
set HERE=%~dp0
if not exist "%WORK%" mkdir "%WORK%"
call "C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvars64.bat" >nul || exit /b 1
cl /nologo /std:c++17 /O2 /EHsc /W4 /fp:precise /Fe:"%WORK%\league_economy.exe" /Fo:"%WORK%\\" "%HERE%economy_main.cpp" "%HERE%..\..\OddsWell\Source\OddsWell\League\OddsWellLeagueCore.cpp" || exit /b 1
"%WORK%\league_economy.exe" %2
