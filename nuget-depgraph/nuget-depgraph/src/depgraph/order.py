"""Порядок загрузки зависимостей (топологическая сортировка)."""

from collections import deque


def count_waiting(graph):
    """Для каждого пакета считает, сколько его зависимостей ещё не загружено."""
    return {name: len(dependencies) for name, dependencies in graph.items()}


def find_dependents(graph):
    """Для каждого пакета находит пакеты, которые от него зависят."""
    dependents = {name: [] for name in graph}
    for name, dependencies in graph.items():
        for dependency in dependencies:
            dependents[dependency].append(name)
    return dependents


def load_order(graph):
    """Возвращает (порядок загрузки, пакеты, для которых порядок не найден).

    Пакет можно загрузить, когда загружены все его зависимости (алгоритм
    Кана без рекурсии). Среди готовых пакетов выбор идёт по алфавиту, чтобы
    результат не менялся от запуска к запуску. Пакеты из циклов и те, что
    от них зависят, загрузить в правильном порядке нельзя: они возвращаются
    вторым списком.
    """
    waiting = count_waiting(graph)
    dependents = find_dependents(graph)
    ready = deque(sorted(name for name, count in waiting.items() if not count))
    order = []
    while ready:
        name = ready.popleft()
        order.append(name)
        newly_ready = []
        for parent in dependents[name]:
            waiting[parent] -= 1
            if not waiting[parent]:
                newly_ready.append(parent)
        ready.extend(sorted(newly_ready))
    loaded = set(order)
    stuck = [name for name in graph if name not in loaded]
    return order, stuck
