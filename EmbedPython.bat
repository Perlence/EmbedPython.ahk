@echo off
"C:\Program Files\AutoHotkey\AutoHotkey.exe" "%~dp0EmbedPython.ahk" %* 2>&1 | wsl cat
