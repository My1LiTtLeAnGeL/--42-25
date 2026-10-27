@echo off
chcp 65001 >nul
echo == 1. no parameters (type exit in the window to continue) ==
python emulator.py
echo == 2. only --prompt ==
python emulator.py --prompt "student>"
echo == 3. only --vfs ==
python emulator.py --vfs examples\myvfs
echo == 4. only --script ==
python emulator.py --script scripts\start_stub.txt
echo == 5. all three parameters ==
python emulator.py --vfs examples\myvfs --prompt "user@host:~$" --script scripts\start_stub.txt
echo == 6. script with unknown command (stops) ==
python emulator.py --prompt ">" --script scripts\err_cmd.txt
echo == 7. script with unclosed quote (stops) ==
python emulator.py --prompt ">" --script scripts\err_quote.txt
echo == 8. missing script file ==
python emulator.py --script scripts\no_such.txt
echo Done.
pause
