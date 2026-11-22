@echo off
set "PYTHONHOME=D:\"
set "PYTHONPATH=D:\Lib\site-packages;%~dp0src;%PYTHONPATH%"
if exist "D:\python.exe" (
    "D:\python.exe" "%~dp0generate_test_report.py" %*
) else (
    py -3.11 "%~dp0generate_test_report.py" %*
)
