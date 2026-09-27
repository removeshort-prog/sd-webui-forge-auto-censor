@echo off
chcp 65001 >nul
setlocal
set "FORGE_ROOT=%~1"
if "%FORGE_ROOT%"=="" set /p "FORGE_ROOT=请输入 Forge Neo 根目录（包含 launch.py）: "
if not exist "%FORGE_ROOT%\launch.py" goto error
if not exist "%FORGE_ROOT%\modules" goto error
set "DEST=%FORGE_ROOT%\extensions\sd-webui-forge-auto-censor"
if exist "%DEST%" goto exists
mkdir "%FORGE_ROOT%\extensions" 2>nul
xcopy "%~dp0*" "%DEST%\" /E /I /Y /EXCLUDE:"%~dp0install-exclude.txt" >nul
echo 已安装 [自动打码]：%DEST%
pause
exit /b 0
:exists
echo 目标目录已存在，请先移走旧版本：%DEST%
pause
exit /b 1
:error
echo 无法确认 Forge Neo 根目录。
pause
exit /b 1
