#!/bin/bash
# этап 2: проверка параметров командной строки
echo "== 1. только --prompt (интерактивно, закройте окно сами) =="
python3 emulator.py --prompt "student>"
echo "== 2. --vfs + --prompt + --script =="
python3 emulator.py --vfs examples/files.xml --prompt "user@host:~$" --script scripts/start_basic.txt
echo "== 3. скрипт с ошибкой (остановится на cd nothing) =="
python3 emulator.py --vfs examples/deep.xml --prompt ">" --script scripts/err_cd.txt
echo "== 4. несуществующий скрипт =="
python3 emulator.py --script scripts/no_such.txt
echo "== 5. несуществующая VFS (ошибка в консоли) =="
python3 emulator.py --vfs examples/no_such.xml
