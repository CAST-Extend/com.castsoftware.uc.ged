@ECHO OFF
setlocal
python.exe src\generateReports.py --config config.json --query query.json
endlocal