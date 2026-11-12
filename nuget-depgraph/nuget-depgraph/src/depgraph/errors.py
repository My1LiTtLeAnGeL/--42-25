"""Исключения приложения."""


class DepGraphError(Exception):
    """Базовая ошибка: её текст показывается пользователю."""


class ConfigError(DepGraphError):
    """Пользователь передал неверные параметры."""


class RepoError(DepGraphError):
    """Не удалось получить данные из репозитория."""


class NotFoundError(RepoError):
    """Запрошенный ресурс не найден в репозитории (HTTP 404)."""


class RenderError(DepGraphError):
    """Не удалось сохранить D2-файл или создать изображение."""
