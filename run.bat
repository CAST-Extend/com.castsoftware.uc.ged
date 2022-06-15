@ECHO OFF
setlocal
set PYTHONPATH=%cd%\Python;%cd%\Python\DLLs;%cd%\Python\lib;%cd%\Python\lib\site-packages;%cd%\ExtLibs
Python\python.exe src\generateReports.py --config config.json --query query.json
endlocal