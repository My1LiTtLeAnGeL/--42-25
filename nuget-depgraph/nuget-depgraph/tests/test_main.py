"""Сквозные тесты: запуск main на тестовых репозиториях."""

import contextlib
import io
import os
import unittest
from unittest import mock

from depgraph.cli import EXIT_ERROR, EXIT_OK, main

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")


def run_main(*args):
    """Запускает main, возвращает (код, stdout, stderr)."""
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = main(list(args))
    return code, out.getvalue(), err.getvalue()


def data(name):
    """Путь к файлу тестового репозитория."""
    return os.path.join(DATA_DIR, name)


class MainTest(unittest.TestCase):
    """Проверка режимов приложения."""

    def test_ascii_tree_and_image(self):
        """Дерево печатается, изображение сохраняется."""
        with mock.patch("depgraph.app.save_image",
                        return_value="graph.d2") as save:
            code, out, _ = run_main("-p", "A", "-r", data("diamond.txt"),
                                    "-t", "-a")
        self.assertEqual(code, EXIT_OK)
        self.assertIn("|-- B", out)
        self.assertIn("graph.svg", out)
        save.assert_called_once()

    def test_no_tree_without_flag(self):
        """Без -a дерево не печатается."""
        with mock.patch("depgraph.app.save_image", return_value="g.d2"):
            _, out, _ = run_main("-p", "A", "-r", data("chain.txt"), "-t")
        self.assertNotIn("`--", out)

    def test_load_order_mode(self):
        """Режим -l печатает порядок и не создаёт изображение."""
        with mock.patch("depgraph.app.save_image") as save:
            code, out, _ = run_main("-p", "A", "-r", data("chain.txt"),
                                    "-t", "-l")
        self.assertEqual(code, EXIT_OK)
        self.assertEqual(out.splitlines(), ["1. C", "2. B", "3. A"])
        save.assert_not_called()

    def test_unknown_package(self):
        """Неизвестный пакет: ошибка и ненулевой код."""
        code, _, err = run_main("-p", "Z", "-r", data("chain.txt"), "-t")
        self.assertEqual(code, EXIT_ERROR)
        self.assertIn("не найден", err)

    def test_filter_and_depth(self):
        """Фильтр и глубина работают вместе."""
        with mock.patch("depgraph.app.save_image", return_value="g.d2"):
            _, out, _ = run_main("-p", "APP", "-r", data("libs.txt"), "-t",
                                 "-a", "-f", "LIB", "-d", "1")
        self.assertEqual(out.splitlines()[:2], ["APP", "`-- CORE"])
