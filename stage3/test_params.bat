@echo off
chcp 65001 >nul
echo == 1. only --prompt (type exit in the window to continue) ==
python emulator.py --prompt "student>"
echo == 2. --vfs + --prompt + --script ==
python emulator.py --vfs examples\files.xml --prompt "user@host:~$" --script scripts\start_basic.txt
echo == 3. script with error (stops at cd nothing) ==
python emulator.py --vfs examples\deep.xml --prompt ">" --script scripts\err_cd.txt
echo == 4. missing script file ==
python emulator.py --script scripts\no_such.txt
echo == 5. missing VFS file (error in console) ==
python emulator.py --vfs examples\no_such.xml
echo Done.
pause
