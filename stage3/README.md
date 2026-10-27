# Эмулятор оболочки с VFS

Один проект, три этапа (см. `git log`): REPL -> конфигурация -> VFS.

## Запуск
1. Откройте терминал в папке проекта (Windows: в проводнике в адресной строке напишите `cmd`, Enter).
2. Введите (Windows `python`, Linux/Mac `python3`):

    python emulator.py --vfs examples/deep.xml --prompt "user@vfs$" --script scripts/start_full.txt

   Или двойной клик по `run_demo.bat` (Windows) / `./run_demo.sh`.

Откроется окно: чёрная область вывода и строка ввода внизу. Команда - Enter.
Без параметров тоже работает: `python emulator.py` (пустая VFS).

Если "python не найден" - переустановите Python с галочкой Add to PATH.
Если "Не найден tkinter" - переустановите Python с опцией "tcl/tk and IDLE".

## Параметры
- `--vfs`    путь к XML-файлу с VFS
- `--prompt` приглашение к вводу
- `--script` стартовый скрипт (останавливается на первой ошибке)

## Команды
- `ls [путь ...]`, `cd [путь]`, `pwd` (текущая папка), `exit`
- `cd` ничего не печатает (как в Linux); чтобы увидеть, где вы, введите `pwd`

## Формат VFS (XML)
    <vfs name="имя">
      <dir name="docs">
        <file name="a.txt">текст</file>
        <file name="b.bin" encoding="base64">AAECAwQF</file>
      </dir>
    </vfs>

## Демонстрация (запуск с examples/deep.xml, вводить по очереди)
    ls
    ls home/user /etc
    cd home/user/projects
    ls
    cd ..
    cd
    ls "не закрыта кавычка     <- ошибка парсера
    foo bar                    <- неизвестная команда
    cd nothing                 <- нет такого каталога
    cd home/user/a.txt         <- не каталог
    exit

## Тесты (реальная ОС)
`test_params.sh` / `.bat` - параметры командной строки;
`test_vfs.sh` / `.bat` - разные VFS (минимальная, несколько файлов, 4 уровня).

## История этапов
`git log --oneline`; посмотреть этап: `git checkout <хеш>`, вернуться: `git checkout main`.
