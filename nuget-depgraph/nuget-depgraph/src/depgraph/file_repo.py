"""Тестовый репозиторий: граф зависимостей описан в текстовом файле.

Формат файла: на каждой строке «ПАКЕТ: ЗАВИСИМОСТЬ1 ЗАВИСИМОСТЬ2 ...».
Имена пакетов состоят из больших латинских букв. Пустые строки
пропускаются. Пакет, которого нет слева от двоеточия, считается пакетом
без зависимостей.
"""

import re

from depgraph.errors import RepoError

TEST_NAME_PATTERN = re.compile(r"^[A-Z]+$")


def check_name(name, line_number):
    """Проверяет, что имя состоит только из больших латинских букв."""
    if not TEST_NAME_PATTERN.match(name):
        raise RepoError(
            f"строка {line_number}: недопустимое имя пакета {name!r}")


def parse_line(line, line_number):
    """Разбирает строку «A: B C», возвращает (имя, зависимости)."""
    name, colon, rest = line.partition(":")
    if not colon:
        raise RepoError(f"строка {line_number}: нет двоеточия")
    name = name.strip()
    check_name(name, line_number)
    dependencies = list(dict.fromkeys(rest.split()))
    for dependency in dependencies:
        check_name(dependency, line_number)
    return name, dependencies


def parse_text(text):
    """Разбирает текст файла в словарь «пакет -> список зависимостей»."""
    table = {}
    for number, line in enumerate(text.splitlines(), start=1):
        if not line.strip():
            continue
        name, dependencies = parse_line(line, number)
        if name in table:
            raise RepoError(f"строка {number}: пакет {name} описан дважды")
        table[name] = dependencies
    return table


def load_table(path):
    """Читает файл тестового репозитория."""
    try:
        with open(path, encoding="utf-8") as repo_file:
            return parse_text(repo_file.read())
    except (OSError, UnicodeDecodeError) as err:
        raise RepoError(f"не удалось прочитать {path}: {err}") from err


class FileRepo:
    """Репозиторий, данные которого заданы словарём (обычно из файла)."""

    def __init__(self, table):
        """Запоминает таблицу и множество всех известных пакетов."""
        self.table = table
        self.known = set(table)
        for dependencies in table.values():
            self.known.update(dependencies)

    def dependencies(self, package):
        """Возвращает список прямых зависимостей пакета."""
        if package not in self.known:
            raise RepoError(f"пакет {package} не найден в тестовом репозитории")
        return list(self.table.get(package, []))


def open_file_repo(path):
    """Создаёт FileRepo из файла."""
    return FileRepo(load_table(path))
