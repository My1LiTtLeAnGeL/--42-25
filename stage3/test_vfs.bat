@echo off
chcp 65001 >nul
echo == minimal VFS ==
python emulator.py --vfs examples\min.xml --prompt "min>" --script scripts\start_basic_min.txt
echo == several files ==
python emulator.py --vfs examples\files.xml --prompt "files>" --script scripts\start_basic.txt
echo == 3+ levels, full scenario ==
python emulator.py --vfs examples\deep.xml --prompt "deep>" --script scripts\start_full.txt
echo == errors: unclosed quote, unknown command ==
python emulator.py --vfs examples\deep.xml --script scripts\err_quote.txt
python emulator.py --vfs examples\deep.xml --script scripts\err_cmd.txt
echo Done.
pause
