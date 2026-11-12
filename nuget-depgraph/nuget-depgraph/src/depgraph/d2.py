"""Текстовое представление графа на языке D2 и создание SVG-файла."""

import os
import subprocess

from depgraph.errors import RenderError

D2_COMMAND = "d2"
D2_EXTENSION = ".d2"
ROOT_STYLE = '{style.fill: "#ffe082"}'


def quote(name):
    """Берёт имя в кавычки, чтобы точки в нём не считались вложенностью."""
    escaped = name.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def make_d2(graph, root):
    """Строит D2-текст: рёбра «пакет -> зависимость», корень выделен."""
    lines = ["direction: right", "", f"{quote(root)}: {ROOT_STYLE}"]
    for name, dependencies in graph.items():
        if not dependencies and name != root:
            lines.append(quote(name))
        for dependency in dependencies:
            lines.append(f"{quote(name)} -> {quote(dependency)}")
    return "\n".join(lines) + "\n"


def render_svg(d2_path, svg_path):
    """Запускает программу d2, чтобы получить SVG из D2-файла."""
    try:
        result = subprocess.run([D2_COMMAND, d2_path, svg_path],
                                capture_output=True, text=True, check=False)
    except FileNotFoundError as err:
        raise RenderError(
            "программа d2 не найдена, установите её: https://d2lang.com"
        ) from err
    if result.returncode:
        raise RenderError(f"d2 завершилась с ошибкой: {result.stderr.strip()}")


def save_image(graph, root, output):
    """Сохраняет D2-файл рядом с изображением и создаёт SVG.

    Возвращает путь к D2-файлу.
    """
    d2_path = os.path.splitext(output)[0] + D2_EXTENSION
    try:
        with open(d2_path, "w", encoding="utf-8") as d2_file:
            d2_file.write(make_d2(graph, root))
    except OSError as err:
        raise RenderError(f"не удалось записать {d2_path}: {err}") from err
    render_svg(d2_path, output)
    return d2_path
