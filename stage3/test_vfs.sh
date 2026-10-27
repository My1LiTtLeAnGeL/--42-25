#!/bin/bash
# этап 3: разные варианты VFS
echo "== минимальная VFS =="
python3 emulator.py --vfs examples/min.xml --prompt "min>" --script scripts/start_basic_min.txt
echo "== несколько файлов =="
python3 emulator.py --vfs examples/files.xml --prompt "files>" --script scripts/start_basic.txt
echo "== 3+ уровня вложенности, полный сценарий =="
python3 emulator.py --vfs examples/deep.xml --prompt "deep>" --script scripts/start_full.txt
echo "== ошибки: кавычка, неизвестная команда =="
python3 emulator.py --vfs examples/deep.xml --script scripts/err_quote.txt
python3 emulator.py --vfs examples/deep.xml --script scripts/err_cmd.txt
