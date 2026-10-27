#!/bin/bash
# проверка всех параметров командной строки
echo "== 1. без параметров (закройте окно сами или введите exit) =="
python3 emulator.py
echo "== 2. только --prompt =="
python3 emulator.py --prompt "student>"
echo "== 3. только --vfs =="
python3 emulator.py --vfs examples/myvfs
echo "== 4. только --script =="
python3 emulator.py --script scripts/start_stub.txt
echo "== 5. все три параметра =="
python3 emulator.py --vfs examples/myvfs --prompt "user@host:~$" --script scripts/start_stub.txt
echo "== 6. скрипт с неизвестной командой (остановка) =="
python3 emulator.py --prompt ">" --script scripts/err_cmd.txt
echo "== 7. скрипт с незакрытой кавычкой (остановка) =="
python3 emulator.py --prompt ">" --script scripts/err_quote.txt
echo "== 8. несуществующий скрипт =="
python3 emulator.py --script scripts/no_such.txt
