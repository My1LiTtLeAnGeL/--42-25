"""Основной сценарий работы приложения."""

from depgraph.d2 import save_image
from depgraph.file_repo import open_file_repo
from depgraph.graph import build_graph
from depgraph.nuget import NugetRepo
from depgraph.order import load_order
from depgraph.tree import build_tree_lines


def make_repo(config):
    """Создаёт источник данных по параметрам запуска."""
    if config.test_mode:
        return open_file_repo(config.repo)
    return NugetRepo(config.repo)


def print_load_order(graph):
    """Печатает порядок загрузки: сначала зависимости, потом зависящие."""
    order, stuck = load_order(graph)
    for number, name in enumerate(order, start=1):
        print(f"{number}. {name}")
    if stuck:
        print("Внимание: для этих пакетов порядок найти нельзя, потому что "
              "они входят в цикл или зависят от пакетов из цикла:")
        print("  " + ", ".join(stuck))


def run(config):
    """Строит граф, печатает порядок загрузки или дерево, сохраняет SVG.

    В режиме --load-order печатается только порядок загрузки.
    """
    repo = make_repo(config)
    graph = build_graph(repo, config.package, config.max_depth,
                        config.filter_substring)
    if config.load_order:
        print_load_order(graph)
        return
    if config.ascii_tree:
        print("\n".join(build_tree_lines(graph, config.package)))
    d2_path = save_image(graph, config.package, config.output)
    print(f"Изображение сохранено: {config.output} (D2-текст: {d2_path})")
