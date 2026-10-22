@echo off
setlocal
set "V2_STARTER=%~dp0test_instance_launcher.py"
pushd "%~dp0"
:find_root
if exist "venv\Scripts\pythonw.exe" goto launch
if exist "voice_stt_client" goto missing_venv
if "%CD:~3%"=="" goto missing_venv
cd ..
goto find_root
:launch
set "QT_QPA_PLATFORM=windows"
set "PYTHONUTF8=1"
set "OPENBLAS_NUM_THREADS=1"
set "OMP_NUM_THREADS=1"
start "" "%CD%\venv\Scripts\pythonw.exe" "%V2_STARTER%"
popd
exit /b 0
:missing_venv
echo Projektumgebung nicht gefunden. Bitte den Agenten informieren.
pause
popd
exit /b 1
