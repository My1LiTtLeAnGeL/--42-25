"""Тесты разбора параметров командной строки."""

import contextlib
import io
import os
import tempfile
import unittest

from depgraph.cli import (DEFAULT_DEPTH, DEFAULT_OUTPUT, EXIT_CONFIG_ERROR,
                          main, parse_args)
from depgraph.errors import ConfigError

URL = "https://api.nuget.org/v3/index.json"
BASE = ["-p", "Newtonsoft.Json", "-r", URL]


class ParseArgsTest(unittest.TestCase):
    """Проверка значений параметров."""

    def test_defaults(self):
        """Без необязательных параметров берутся значения по умолчанию."""
        config = parse_args(BASE)
        self.assertEqual(config.package, "Newtonsoft.Json")
        self.assertEqual(config.output, DEFAULT_OUTPUT)
        self.assertEqual(config.max_depth, DEFAULT_DEPTH)
        self.assertFalse(config.ascii_tree)
        self.assertFalse(config.test_mode)
        self.assertIsNone(config.filter_substring)

    def test_all_options(self):
        """Все параметры разбираются."""
        args = BASE + ["-o", "out.svg", "-a", "-d", "2", "-f", "System"]
        config = parse_args(args)
        self.assertEqual(config.output, "out.svg")
        self.assertTrue(config.ascii_tree)
        self.assertEqual(config.max_depth, 2)
        self.assertEqual(config.filter_substring, "System")

    def test_test_mode_with_existing_file(self):
        """В тестовом режиме принимается путь к существующему файлу."""
        with tempfile.NamedTemporaryFile("w", suffix=".txt") as repo_file:
            config = parse_args(["-p", "A", "-r", repo_file.name, "-t"])
        self.assertTrue(config.test_mode)


class ParseArgsErrorsTest(unittest.TestCase):
    """Проверка обработки ошибок для каждого параметра."""

    def test_bad_package_name(self):
        """Имя пакета с пробелом недопустимо."""
        with self.assertRaises(ConfigError):
            parse_args(["-p", "bad name", "-r", URL])

    def test_lowercase_package_in_test_mode(self):
        """В тестовом режиме имя пакета только из больших букв."""
        with tempfile.NamedTemporaryFile("w", suffix=".txt") as repo_file:
            with self.assertRaises(ConfigError):
                parse_args(["-p", "a", "-r", repo_file.name, "-t"])

    def test_bad_url(self):
        """URL должен начинаться с http:// или https://."""
        with self.assertRaises(ConfigError):
            parse_args(["-p", "A", "-r", "ftp://example.com"])

    def test_missing_repo_file(self):
        """Несуществующий файл тестового репозитория."""
        with self.assertRaises(ConfigError):
            parse_args(["-p", "A", "-r", "no_such_file.txt", "-t"])

    def test_output_extension(self):
        """Изображение можно сохранить только в .svg."""
        with self.assertRaises(ConfigError):
            parse_args(BASE + ["-o", "graph.png"])

    def test_output_folder_missing(self):
        """Каталог для изображения должен существовать."""
        path = os.path.join("no_such_folder", "graph.svg")
        with self.assertRaises(ConfigError):
            parse_args(BASE + ["-o", path])

    def test_depth_too_small(self):
        """Глубина меньше минимальной."""
        with self.assertRaises(ConfigError):
            parse_args(BASE + ["-d", "0"])

    def test_depth_not_a_number(self):
        """Глубина не число: argparse завершает программу."""
        with contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit):
                parse_args(BASE + ["-d", "abc"])

    def test_empty_filter(self):
        """Пустая подстрока фильтра запрещена."""
        with self.assertRaises(ConfigError):
            parse_args(BASE + ["-f", ""])

    def test_missing_required(self):
        """Без имени пакета программа не запускается."""
        with contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit):
                parse_args(["-r", URL])


class MainTest(unittest.TestCase):
    """Проверка точки входа."""

    def test_main_reports_config_error(self):
        """main печатает ошибку параметров и возвращает код 2."""
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            code = main(["-p", "A", "-r", "ftp://x"])
        self.assertEqual(code, EXIT_CONFIG_ERROR)
        self.assertIn("Ошибка", err.getvalue())
