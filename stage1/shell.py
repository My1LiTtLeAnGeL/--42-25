# Парсер и команды-заглушки
import shlex


class Shell:
    def __init__(self):
        self.finished = False

    def run(self, line):
        """Выполняет строку. Возвращает (текст_вывода, успешно_ли)."""
        try:
            parts = shlex.split(line)
        except ValueError:
            return "Ошибка парсера: не закрыта кавычка", False
        if not parts:
            return "", True

        name = parts[0]
        args = parts[1:]
        if name in ("ls", "cd"):
            return f"Команда: {name}\nАргументы: {args}", True
        elif name == "exit":
            if args:
                return "exit: команда не принимает аргументов", False
            self.finished = True
            return "", True
        else:
            return f"{name}: команда не найдена", False
