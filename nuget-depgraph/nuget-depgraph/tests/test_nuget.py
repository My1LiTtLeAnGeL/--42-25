"""Тесты чтения зависимостей из репозитория NuGet (на подменённых данных)."""

import unittest

from depgraph.errors import NotFoundError, RepoError
from depgraph.nuget import NugetRepo, entry_dependencies

INDEX_URL = "https://repo.test/v3/index.json"
REG = "https://repo.test/reg/"
INDEX = {"resources": [
    {"@id": "https://repo.test/search", "@type": "SearchQueryService"},
    {"@id": REG, "@type": "RegistrationsBaseUrl/3.6.0"},
]}


def make_entry(version, groups):
    """Собирает лист регистрации с заданными группами зависимостей."""
    return {"catalogEntry": {"version": version, "dependencyGroups": groups}}


def group(*names):
    """Собирает группу зависимостей для целевой платформы."""
    return {"targetFramework": "net6.0",
            "dependencies": [{"id": name, "range": "1.0.0"} for name in names]}


DATA = {
    INDEX_URL: INDEX,
    REG + "foo/index.json": {"items": [{
        "@id": REG + "foo/page0.json",
        "items": [
            make_entry("1.0.0", [group("Old")]),
            make_entry("2.0.0", [group("Bar", "Baz"), group("bar", "Qux")]),
            make_entry("3.0.0-beta", [group("Beta")]),
        ],
    }]},
    REG + "paged/index.json": {"items": [{"@id": REG + "paged/p0.json"}]},
    REG + "paged/p0.json": {"items": [make_entry("1.5.0", [])]},
    REG + "onlybeta/index.json": {"items": [{
        "@id": REG + "onlybeta/p.json",
        "items": [make_entry("1.0.0-rc1", [group("X")])],
    }]},
    REG + "empty/index.json": {"items": []},
}


class FakeFetch:
    """Подменяет сетевой запрос: отдаёт данные из словаря DATA."""

    def __init__(self):
        """Создаёт пустой журнал запросов."""
        self.calls = []

    def __call__(self, url):
        """Возвращает JSON по адресу или бросает NotFoundError."""
        self.calls.append(url)
        if url not in DATA:
            raise NotFoundError(url)
        return DATA[url]


def make_repo():
    """Создаёт репозиторий с подменённой загрузкой и журналом запросов."""
    fetch = FakeFetch()
    return NugetRepo(INDEX_URL, fetch=fetch), fetch


class NugetRepoTest(unittest.TestCase):
    """Проверка NugetRepo."""

    def test_picks_latest_stable_version(self):
        """Берётся последняя стабильная версия, beta пропускается."""
        repo, _ = make_repo()
        version, deps = repo.get_package("Foo")
        self.assertEqual(version, "2.0.0")
        self.assertEqual(deps, ["Bar", "Baz", "Qux"])

    def test_page_without_items_is_downloaded(self):
        """Страница без вложенных items скачивается отдельно."""
        repo, _ = make_repo()
        self.assertEqual(repo.get_package("paged"), ("1.5.0", []))

    def test_only_prerelease(self):
        """Если стабильных версий нет, берётся последняя из имеющихся."""
        repo, _ = make_repo()
        self.assertEqual(repo.dependencies("onlybeta"), ["X"])

    def test_unknown_package(self):
        """Неизвестный пакет даёт понятную ошибку."""
        repo, _ = make_repo()
        with self.assertRaises(RepoError):
            repo.get_package("nothing")

    def test_package_without_versions(self):
        """Пакет без версий — ошибка."""
        repo, _ = make_repo()
        with self.assertRaises(RepoError):
            repo.get_package("empty")

    def test_results_are_cached(self):
        """Повторный запрос пакета не ходит в сеть."""
        repo, fetch = make_repo()
        repo.get_package("foo")
        count = len(fetch.calls)
        repo.get_package("FOO")
        self.assertEqual(len(fetch.calls), count)

    def test_index_without_registration(self):
        """В индексе нет нужного ресурса — ошибка."""
        repo = NugetRepo(INDEX_URL, fetch=lambda url: {"resources": []})
        with self.assertRaises(RepoError):
            repo.get_package("foo")


class EntryDependenciesTest(unittest.TestCase):
    """Проверка объединения групп зависимостей."""

    def test_no_groups(self):
        """У записи без групп нет зависимостей."""
        self.assertEqual(entry_dependencies({}), [])

    def test_group_without_dependencies(self):
        """Группа без ключа dependencies допустима."""
        entry = {"dependencyGroups": [{"targetFramework": "net6.0"}]}
        self.assertEqual(entry_dependencies(entry), [])
