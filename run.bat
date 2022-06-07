@ECHO OFF
setlocal
set PYTHONPATH=%cd%\Python;%cd%\Python\DLLs;%cd%\Python\lib;%cd%\Python\lib\site-packages;%cd%\Libs;%cd%\ExtLibs
Python\python.exe generateReports.py --config config.json
endlocal