@echo off
REM Convenience launcher to run report generator with Python 3.11
if exist "D:\python.exe" (
    "D:\python.exe" generate_test_report.py %*
) else (
    py -3.11 generate_test_report.py %*
)
