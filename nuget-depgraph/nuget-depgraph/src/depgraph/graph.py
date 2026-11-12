"""Построение графа зависимостей обходом в ширину (BFS) без рекурсии."""

from collections import deque

from depgraph.errors import ConfigError


def is_filtered(name, substring):
    """Проверяет, что пакет нужно исключить из анализа."""
    return substring is not None and substring in name


def visible_dependencies(repo, package, substring):
    """Возвращает зависимости пакета без отфильтрованных."""
    dependencies = repo.dependencies(package)
    return [name for name in dependencies if not is_filtered(name, substring)]


def build_graph(repo, root, max_depth, substring=None):
    """Строит граф зависимостей пакета root.

    Граф — словарь «пакет -> список зависимостей», ключи идут в порядке
    обхода в ширину. Корень имеет глубину 0, пакеты на глубине max_depth
    попадают в граф, но их зависимости не загружаются. Уже встреченные
    пакеты повторно не обрабатываются, поэтому циклы не зацикливают обход.
    """
    if is_filtered(root, substring):
        raise ConfigError(
            f"корневой пакет {root} содержит подстроку фильтра {substring!r}")
    graph = {}
    seen = {root}
    queue = deque([(root, 0)])
    while queue:
        name, depth = queue.popleft()
        if depth >= max_depth:
            graph[name] = []
            continue
        graph[name] = visible_dependencies(repo, name, substring)
        for child in graph[name]:
            if child not in seen:
                seen.add(child)
                queue.append((child, depth + 1))
    return graph
