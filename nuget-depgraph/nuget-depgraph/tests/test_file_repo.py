"""Тесты тестового репозитория (файла с описанием графа)."""

import os
import unittest

from depgraph.errors import RepoError
from depgraph.file_repo import FileRepo, open_file_repo, parse_text

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")


class ParseTextTest(unittest.TestCase):
    """Разбор текста файла."""

    def test_simple(self):
        """Строки разбираются в словарь, пустые строки пропускаются."""
        table = parse_text("A: B C\n\nB:\n")
        self.assertEqual(table, {"A": ["B", "C"], "B": []})

    def test_duplicate_dependencies_removed(self):
        """Повторы зависимостей в строке убираются."""
        self.assertEqual(parse_text("A: B B C"), {"A": ["B", "C"]})

    def test_no_colon(self):
        """Строка без двоеточия — ошибка."""
        with self.assertRaises(RepoError):
            parse_text("A B")

    def test_lowercase_name(self):
        """Имена только из больших латинских букв."""
        with self.assertRaises(RepoError):
            parse_text("a: B")
        with self.assertRaises(RepoError):
            parse_text("A: b")

    def test_package_described_twice(self):
        """Пакет нельзя описать два раза."""
        with self.assertRaises(RepoError):
            parse_text("A: B\nA: C")


class FileRepoTest(unittest.TestCase):
    """Проверка FileRepo."""

    def test_dependencies(self):
        """Зависимости возвращаются, а пакет без строки — без зависимостей."""
        repo = FileRepo(parse_text("A: B"))
        self.assertEqual(repo.dependencies("A"), ["B"])
        self.assertEqual(repo.dependencies("B"), [])

    def test_unknown_package(self):
        """Неизвестный пакет — ошибка."""
        repo = FileRepo(parse_text("A: B"))
        with self.assertRaises(RepoError):
            repo.dependencies("Z")

    def test_open_file(self):
        """Файл из tests/data читается."""
        repo = open_file_repo(os.path.join(DATA_DIR, "chain.txt"))
        self.assertEqual(repo.dependencies("B"), ["C"])

    def test_missing_file(self):
        """Несуществующий файл — ошибка репозитория."""
        with self.assertRaises(RepoError):
            open_file_repo(os.path.join(DATA_DIR, "no_such_file.txt"))
