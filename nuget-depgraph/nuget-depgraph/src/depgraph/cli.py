"""Разбор и проверка параметров командной строки."""

import argparse
import os
import re
import sys
from dataclasses import dataclass
from typing import Optional

from depgraph.app import run
from depgraph.errors import ConfigError, DepGraphError
from depgraph.file_repo import TEST_NAME_PATTERN

EXIT_OK = 0
EXIT_ERROR = 1
EXIT_CONFIG_ERROR = 2
DEFAULT_OUTPUT = "graph.svg"
DEFAULT_DEPTH = 3
MIN_DEPTH = 1
SVG_EXTENSION = ".svg"
URL_PATTERN = re.compile(r"^https?://\S+$")
NUGET_NAME_PATTERN = re.compile(r"^[A-Za-z0-9._-]+$")


@dataclass
class Config:
    """Параметры запуска, заданные пользователем."""

    package: str
    repo: str
    test_mode: bool
    output: str
    ascii_tree: bool
    max_depth: int
    filter_substring: Optional[str] = None
    load_order: bool = False


def add_input_options(parser):
    """Добавляет параметры, которые говорят, что и откуда анализировать."""
    parser.add_argument("-p", "--package", required=True,
                        help="имя анализируемого пакета")
    parser.add_argument("-r", "--repo", required=True,
                        help="URL репозитория NuGet (index.json) или путь "
                             "к файлу тестового репозитория")
    parser.add_argument("-t", "--test-mode", action="store_true",
                        help="работать с тестовым репозиторием (файлом)")


def add_graph_options(parser):
    """Добавляет параметры, которые влияют на построение графа."""
    parser.add_argument("-d", "--max-depth", type=int,
                        default=DEFAULT_DEPTH,
                        help="максимальная глубина анализа зависимостей")
    parser.add_argument("-f", "--filter", dest="filter_substring",
                        default=None,
                        help="не учитывать пакеты, в имени которых есть "
                             "эта подстрока")


def add_output_options(parser):
    """Добавляет параметры вывода результата."""
    parser.add_argument("-o", "--output", default=DEFAULT_OUTPUT,
                        help="имя файла с изображением графа (.svg)")
    parser.add_argument("-a", "--ascii-tree", action="store_true",
                        help="вывести зависимости в виде ASCII-дерева")
    parser.add_argument("-l", "--load-order", action="store_true",
                        help="вывести порядок загрузки зависимостей пакета")


def build_parser():
    """Создаёт разборщик аргументов командной строки."""
    parser = argparse.ArgumentParser(
        prog="depgraph",
        description="Визуализация графа зависимостей пакетов NuGet.",
    )
    add_input_options(parser)
    add_graph_options(parser)
    add_output_options(parser)
    return parser


def check_package(package, test_mode):
    """Проверяет имя пакета."""
    if test_mode:
        if not TEST_NAME_PATTERN.match(package):
            raise ConfigError(
                "в тестовом режиме имя пакета состоит из больших "
                f"латинских букв, а получено {package!r}")
    elif not NUGET_NAME_PATTERN.match(package):
        raise ConfigError(f"недопустимое имя пакета NuGet: {package!r}")


def check_repo(repo, test_mode):
    """Проверяет URL репозитория или путь к тестовому файлу."""
    if test_mode:
        if not os.path.isfile(repo):
            raise ConfigError(f"файл тестового репозитория не найден: {repo}")
    elif not URL_PATTERN.match(repo):
        raise ConfigError(f"некорректный URL репозитория: {repo}")


def check_output(output):
    """Проверяет имя файла с изображением."""
    if not output.lower().endswith(SVG_EXTENSION):
        raise ConfigError("файл изображения должен иметь расширение .svg")
    folder = os.path.dirname(output)
    if folder and not os.path.isdir(folder):
        raise ConfigError(f"каталог для изображения не существует: {folder}")


def check_depth(max_depth):
    """Проверяет максимальную глубину анализа."""
    if max_depth < MIN_DEPTH:
        raise ConfigError(
            f"максимальная глубина должна быть не меньше {MIN_DEPTH}")


def check_filter(substring):
    """Проверяет подстроку фильтра: пустая отфильтровала бы всё."""
    if substring is not None and not substring:
        raise ConfigError("подстрока фильтра не должна быть пустой")


def validate(config):
    """Проверяет все параметры, при ошибке бросает ConfigError."""
    check_package(config.package, config.test_mode)
    check_repo(config.repo, config.test_mode)
    check_output(config.output)
    check_depth(config.max_depth)
    check_filter(config.filter_substring)


def parse_args(argv=None):
    """Разбирает аргументы командной строки и возвращает Config."""
    args = build_parser().parse_args(argv)
    config = Config(
        package=args.package,
        repo=args.repo,
        test_mode=args.test_mode,
        output=args.output,
        ascii_tree=args.ascii_tree,
        max_depth=args.max_depth,
        filter_substring=args.filter_substring,
        load_order=args.load_order,
    )
    validate(config)
    return config


def main(argv=None):
    """Точка входа: возвращает код завершения программы."""
    try:
        run(parse_args(argv))
    except ConfigError as err:
        print(f"Ошибка: {err}", file=sys.stderr)
        return EXIT_CONFIG_ERROR
    except DepGraphError as err:
        print(f"Ошибка: {err}", file=sys.stderr)
        return EXIT_ERROR
    return EXIT_OK
