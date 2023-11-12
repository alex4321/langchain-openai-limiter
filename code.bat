@echo off
SET SCRIPT_PATH=%~dp0
SET SCRIPT_FNAME="__script.bat"
echo conda activate pino-inferior > %SCRIPT_FNAME%
echo SET PYTHONPATH=%SCRIPT_PATH%;%%PYTHONPATH%% >> %SCRIPT_FNAME%
echo code.exe . >> %SCRIPT_FNAME%
cmd /K C:\Users\alex4321\anaconda3\Scripts\activate.bat C:\Users\alex4321\anaconda3 < %SCRIPT_FNAME%