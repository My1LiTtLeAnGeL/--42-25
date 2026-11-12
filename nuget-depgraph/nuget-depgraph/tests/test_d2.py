"""Тесты D2-текста и создания SVG (программа d2 подменяется)."""

import os
import subprocess
import tempfile
import unittest
from unittest import mock

from depgraph.d2 import make_d2, quote, render_svg, save_image
from depgraph.errors import RenderError

GRAPH = {"A": ["B", "C"], "B": [], "C": []}


class MakeD2Test(unittest.TestCase):
    """Проверка текста на языке D2."""

    def test_text(self):
        """Корень выделен, рёбра записаны стрелками, листья объявлены."""
        self.assertEqual(make_d2(GRAPH, "A"), "\n".join([
            "direction: right",
            "",
            '"A": {style.fill: "#ffe082"}',
            '"A" -> "B"',
            '"A" -> "C"',
            '"B"',
            '"C"',
            "",
        ]))

    def test_dots_are_quoted(self):
        """Имена с точками берутся в кавычки."""
        self.assertEqual(quote("System.Text.Json"), '"System.Text.Json"')

    def test_quote_escaping(self):
        """Кавычка и обратная косая черта экранируются."""
        self.assertEqual(quote('a"b\\c'), '"a\\"b\\\\c"')

    def test_single_root(self):
        """Корень без зависимостей не дублируется."""
        text = make_d2({"A": []}, "A")
        self.assertEqual(text.count('"A"'), 1)


class RenderTest(unittest.TestCase):
    """Проверка запуска d2."""

    def test_missing_program(self):
        """Если d2 не установлена, будет понятная ошибка."""
        with mock.patch("depgraph.d2.subprocess.run",
                        side_effect=FileNotFoundError):
            with self.assertRaises(RenderError):
                render_svg("a.d2", "a.svg")

    def test_d2_failure(self):
        """Ненулевой код возврата d2 — ошибка."""
        failed = subprocess.CompletedProcess([], 1, "", "syntax error")
        with mock.patch("depgraph.d2.subprocess.run", return_value=failed):
            with self.assertRaises(RenderError):
                render_svg("a.d2", "a.svg")

    def test_save_image(self):
        """D2-файл записывается рядом с SVG, d2 вызывается с нужными путями."""
        done = subprocess.CompletedProcess([], 0, "", "")
        with tempfile.TemporaryDirectory() as folder:
            output = os.path.join(folder, "out.svg")
            with mock.patch("depgraph.d2.subprocess.run",
                            return_value=done) as run_mock:
                d2_path = save_image(GRAPH, "A", output)
            self.assertEqual(d2_path, os.path.join(folder, "out.d2"))
            with open(d2_path, encoding="utf-8") as d2_file:
                self.assertIn('"A" -> "B"', d2_file.read())
            command = run_mock.call_args[0][0]
            self.assertEqual(command, ["d2", d2_path, output])

    def test_cannot_write_d2(self):
        """Нельзя записать D2-файл — ошибка RenderError."""
        with self.assertRaises(RenderError):
            save_image(GRAPH, "A", os.path.join("no_such_folder", "o.svg"))
