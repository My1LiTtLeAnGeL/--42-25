"""Получение информации о зависимостях из репозитория NuGet (API v3).

Используются только стандартные модули urllib и json: готовых менеджеров
пакетов и сторонних библиотек для получения зависимостей нет.
"""

import json
import urllib.error
import urllib.request

from depgraph.errors import NotFoundError, RepoError

REGISTRATION_TYPE = "RegistrationsBaseUrl"
TIMEOUT_SECONDS = 20
HTTP_NOT_FOUND = 404
PRERELEASE_MARK = "-"


def fetch_json(url):
    """Скачивает url и возвращает разобранный JSON."""
    request = urllib.request.Request(
        url, headers={"Accept": "application/json"})
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as resp:
            return json.load(resp)
    except urllib.error.HTTPError as err:
        if err.code == HTTP_NOT_FOUND:
            raise NotFoundError(f"ресурс не найден: {url}") from err
        raise RepoError(f"сервер ответил {err.code} на {url}") from err
    except (urllib.error.URLError, TimeoutError, ValueError) as err:
        raise RepoError(f"не удалось получить {url}: {err}") from err


def find_registration_url(index):
    """Ищет в сервисном индексе адрес каталога регистраций пакетов."""
    for resource in index.get("resources", []):
        kinds = resource.get("@type", [])
        if isinstance(kinds, str):
            kinds = [kinds]
        if any(kind.startswith(REGISTRATION_TYPE) for kind in kinds):
            return resource["@id"]
    raise RepoError("в индексе репозитория нет адреса регистраций пакетов")


def leaf_entries(leaves):
    """Достаёт описания версий (catalogEntry) из листьев страницы."""
    entries = []
    for leaf in leaves:
        entry = leaf.get("catalogEntry")
        if isinstance(entry, dict):
            entries.append(entry)
    return entries


def is_stable(entry):
    """Проверяет, что версия не предварительная (без суффикса -beta и т.п.)."""
    return PRERELEASE_MARK not in entry.get("version", "")


def entry_dependencies(entry):
    """Собирает имена зависимостей из всех групп целевых платформ.

    Менеджер пакетов выбирает одну платформу, а мы объединяем все группы
    и убираем повторы (имена в NuGet не зависят от регистра).
    """
    names = []
    seen = set()
    for group in entry.get("dependencyGroups", []):
        for dependency in group.get("dependencies", []):
            name = dependency.get("id")
            if name and name.lower() not in seen:
                seen.add(name.lower())
                names.append(name)
    return names


class NugetRepo:
    """Репозиторий NuGet, доступный по адресу сервисного индекса v3."""

    def __init__(self, index_url, fetch=fetch_json):
        """Запоминает адрес индекса и функцию загрузки JSON."""
        self.index_url = index_url
        self.fetch = fetch
        self.registration_url = None
        self.cache = {}

    def get_registration_url(self):
        """Возвращает адрес каталога регистраций (скачивает индекс один раз)."""
        if self.registration_url is None:
            index = self.fetch(self.index_url)
            self.registration_url = find_registration_url(index)
        return self.registration_url

    def load_leaves(self, page):
        """Возвращает листья страницы, при необходимости скачивая её."""
        if "items" not in page:
            page = self.fetch(page["@id"])
        return page.get("items", [])

    def find_latest_entry(self, pages):
        """Находит запись самой новой стабильной версии пакета."""
        newest = []
        for page in reversed(pages):
            entries = leaf_entries(self.load_leaves(page))
            newest = newest or entries
            stable = [entry for entry in entries if is_stable(entry)]
            if stable:
                return stable[-1]
        if not newest:
            raise RepoError("у пакета нет ни одной версии")
        return newest[-1]

    def load_package(self, package):
        """Скачивает данные пакета: возвращает (версия, зависимости)."""
        base = self.get_registration_url().rstrip("/")
        url = f"{base}/{package.lower()}/index.json"
        try:
            index = self.fetch(url)
        except NotFoundError as err:
            raise RepoError(f"пакет {package} не найден") from err
        entry = self.find_latest_entry(index.get("items", []))
        return entry.get("version", "?"), entry_dependencies(entry)

    def get_package(self, package):
        """Возвращает (версия, список прямых зависимостей) пакета."""
        key = package.lower()
        if key not in self.cache:
            self.cache[key] = self.load_package(package)
        return self.cache[key]

    def dependencies(self, package):
        """Возвращает список имён прямых зависимостей пакета."""
        return self.get_package(package)[1]
