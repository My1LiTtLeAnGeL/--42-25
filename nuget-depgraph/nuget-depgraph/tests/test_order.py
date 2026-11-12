"""Тесты порядка загрузки зависимостей."""

import os
import unittest

from depgraph.file_repo import open_file_repo
from depgraph.graph import build_graph
from depgraph.order import load_order

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
BIG_DEPTH = 100


def order_for(name, root="A", depth=BIG_DEPTH):
    """Строит граф из файла tests/data и возвращает порядок загрузки."""
    repo = open_file_repo(os.path.join(DATA_DIR, name))
    return load_order(build_graph(repo, root, depth))


class LoadOrderTest(unittest.TestCase):
    """Проверка load_order."""

    def test_chain(self):
        """Сначала самая глубокая зависимость."""
        self.assertEqual(order_for("chain.txt"), (["C", "B", "A"], []))

    def test_diamond(self):
        """D грузится раньше B и C, корень последний."""
        self.assertEqual(order_for("diamond.txt"), (["D", "B", "C", "A"], []))

    def test_single_package(self):
        """Пакет без зависимостей грузится один."""
        self.assertEqual(order_for("chain.txt", "C"), (["C"], []))

    def test_cycle(self):
        """В цикле порядка нет: все пакеты возвращаются как застрявшие."""
        self.assertEqual(order_for("cycle.txt"), ([], ["A", "B", "C"]))

    def test_self_loop(self):
        """Зависимость от самого себя тоже цикл."""
        self.assertEqual(order_for("self_loop.txt"), (["B"], ["A"]))

    def test_partial_cycle(self):
        """Пакет вне цикла X загружается, остальные застревают."""
        self.assertEqual(order_for("partial_cycle.txt"),
                         (["X"], ["A", "B", "C"]))

    def test_dependencies_come_first(self):
        """В любом порядке зависимость стоит раньше зависящего пакета."""
        repo = open_file_repo(os.path.join(DATA_DIR, "libs.txt"))
        graph = build_graph(repo, "APP", BIG_DEPTH)
        order, stuck = load_order(graph)
        self.assertEqual(stuck, [])
        for name, dependencies in graph.items():
            for dependency in dependencies:
                self.assertLess(order.index(dependency), order.index(name))

    def test_depth_limit_changes_order(self):
        """С ограничением глубины в порядок попадают только нужные пакеты."""
        order, _ = order_for("chain.txt", depth=1)
        self.assertEqual(order, ["B", "A"])
