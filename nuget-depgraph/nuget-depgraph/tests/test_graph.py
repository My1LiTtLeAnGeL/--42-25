"""Тесты построения графа зависимостей (BFS)."""

import os
import unittest

from depgraph.errors import ConfigError, RepoError
from depgraph.file_repo import FileRepo, open_file_repo, parse_text
from depgraph.graph import build_graph

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
BIG_DEPTH = 100
LONG_CHAIN = 5000


def load(name):
    """Открывает тестовый репозиторий из tests/data."""
    return open_file_repo(os.path.join(DATA_DIR, name))


class BuildGraphTest(unittest.TestCase):
    """Проверка обхода в ширину."""

    def test_chain(self):
        """Цепочка A -> B -> C."""
        graph = build_graph(load("chain.txt"), "A", BIG_DEPTH)
        self.assertEqual(graph, {"A": ["B"], "B": ["C"], "C": []})

    def test_diamond_has_each_package_once(self):
        """Общая зависимость D обрабатывается один раз."""
        graph = build_graph(load("diamond.txt"), "A", BIG_DEPTH)
        self.assertEqual(list(graph), ["A", "B", "C", "D"])
        self.assertEqual(graph["B"], ["D"])
        self.assertEqual(graph["C"], ["D"])

    def test_bfs_order(self):
        """Пакеты идут по уровням: сначала ближние, потом дальние."""
        graph = build_graph(load("complex.txt"), "A", BIG_DEPTH)
        self.assertEqual(list(graph), ["A", "B", "C", "D", "E", "F"])

    def test_depth_limit(self):
        """На предельной глубине зависимости уже не загружаются."""
        graph = build_graph(load("chain.txt"), "A", 1)
        self.assertEqual(graph, {"A": ["B"], "B": []})

    def test_depth_two(self):
        """Глубина 2 включает пакеты до C."""
        graph = build_graph(load("chain.txt"), "A", 2)
        self.assertEqual(graph, {"A": ["B"], "B": ["C"], "C": []})

    def test_cycle(self):
        """Цикл A -> B -> C -> A не зацикливает обход, ребро сохраняется."""
        graph = build_graph(load("cycle.txt"), "A", BIG_DEPTH)
        self.assertEqual(graph, {"A": ["B"], "B": ["C"], "C": ["A"]})

    def test_self_loop(self):
        """Пакет, зависящий от самого себя."""
        graph = build_graph(load("self_loop.txt"), "A", BIG_DEPTH)
        self.assertEqual(graph, {"A": ["A", "B"], "B": []})

    def test_cycle_inside_big_graph(self):
        """Цикл B -> D -> F -> B внутри большого графа."""
        graph = build_graph(load("complex.txt"), "A", BIG_DEPTH)
        self.assertEqual(graph["F"], ["B"])

    def test_filter(self):
        """Пакеты с подстрокой LIB в имени не попадают в граф."""
        graph = build_graph(load("libs.txt"), "APP", BIG_DEPTH, "LIB")
        self.assertEqual(graph, {"APP": ["CORE"], "CORE": []})

    def test_filter_without_matches(self):
        """Подстрока, которой нет в именах, ничего не меняет."""
        graph = build_graph(load("libs.txt"), "APP", BIG_DEPTH, "ZZZ")
        self.assertEqual(len(graph), 5)

    def test_filter_root(self):
        """Корневой пакет с подстрокой фильтра — ошибка."""
        with self.assertRaises(ConfigError):
            build_graph(load("libs.txt"), "APP", BIG_DEPTH, "AP")

    def test_unknown_root(self):
        """Неизвестный корневой пакет — ошибка репозитория."""
        with self.assertRaises(RepoError):
            build_graph(load("chain.txt"), "Z", BIG_DEPTH)

    def test_long_chain_without_recursion(self):
        """Очень длинная цепочка не вызывает RecursionError."""
        names = []
        for number in range(LONG_CHAIN):
            names.append(chr(65 + number % 26) * (number // 26 + 1))
        lines = [f"{names[i]}: {names[i + 1]}" for i in range(LONG_CHAIN - 1)]
        repo = FileRepo(parse_text("\n".join(lines)))
        graph = build_graph(repo, names[0], LONG_CHAIN)
        self.assertEqual(len(graph), LONG_CHAIN)
