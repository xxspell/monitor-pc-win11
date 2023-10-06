Set WshShell = CreateObject("WScript.Shell")
WshShell.Run "cmd /c .venv\Scripts\python.exe main.py", 0
Set WshShell = Nothing
