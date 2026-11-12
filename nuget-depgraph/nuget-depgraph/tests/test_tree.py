"""Тесты вывода ASCII-дерева."""

import os
import unittest

from depgraph.file_repo import FileRepo, open_file_repo, parse_text
from depgraph.graph import build_graph
from depgraph.tree import build_tree_lines

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
BIG_DEPTH = 100


def tree_for(name, root="A", depth=BIG_DEPTH):
    """Строит дерево для графа из файла tests/data."""
    repo = open_file_repo(os.path.join(DATA_DIR, name))
    return build_tree_lines(build_graph(repo, root, depth), root)


class TreeTest(unittest.TestCase):
    """Проверка build_tree_lines."""

    def test_chain(self):
        """Цепочка рисуется лесенкой."""
        self.assertEqual(tree_for("chain.txt"), [
            "A",
            "`-- B",
            "    `-- C",
        ])

    def test_diamond_leaf_repeat(self):
        """Лист D показывается в обеих ветках, пометка не нужна."""
        self.assertEqual(tree_for("diamond.txt"), [
            "A",
            "|-- B",
            "|   `-- D",
            "`-- C",
            "    `-- D",
        ])

    def test_shared_dependency_with_children(self):
        """Общая зависимость с поддеревом раскрывается один раз."""
        repo = FileRepo(parse_text("A: B C\nB: D\nC: D\nD: E\nE:"))
        graph = build_graph(repo, "A", BIG_DEPTH)
        self.assertEqual(build_tree_lines(graph, "A"), [
            "A",
            "|-- B",
            "|   `-- D",
            "|       `-- E",
            "`-- C",
            "    `-- D (см. выше)",
        ])

    def test_cycle_stops(self):
        """Цикл обрывается пометкой, а не бесконечным выводом."""
        self.assertEqual(tree_for("cycle.txt"), [
            "A",
            "`-- B",
            "    `-- C",
            "        `-- A (см. выше)",
        ])

    def test_self_loop(self):
        """Зависимость от самого себя."""
        self.assertEqual(tree_for("self_loop.txt"), [
            "A",
            "|-- A (см. выше)",
            "`-- B",
        ])

    def test_single_package(self):
        """Пакет без зависимостей — одна строка."""
        self.assertEqual(tree_for("chain.txt", "C"), ["C"])

    def test_depth_limit(self):
        """Глубина ограничивает дерево."""
        self.assertEqual(tree_for("chain.txt", depth=1), ["A", "`-- B"])
