@echo off
chcp 65001 >nul
python emulator.py --vfs examples\deep.xml --prompt "user@vfs$" --script scripts\start_full.txt
pause
