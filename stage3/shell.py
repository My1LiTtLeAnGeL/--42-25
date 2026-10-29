# Парсер и команды эмулятора (без GUI, чтобы было проще тестировать)
import shlex


class Shell:
    def __init__(self, vfs):
        self.vfs = vfs
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
        if name == "ls":
            return self.cmd_ls(args)
        elif name == "cd":
            return self.cmd_cd(args)
        elif name == "pwd":
            return self.cmd_pwd(args)
        elif name == "exit":
            return self.cmd_exit(args)
        else:
            return f"{name}: команда не найдена", False

    def cmd_ls(self, args):
        if not args:
            args = ["."]
        result = []
        ok = True
        for path in args:
            try:
                node = self.vfs.resolve(path)
            except Exception as e:
                result.append(f"ls: {e}")
                ok = False
                continue
            if len(args) > 1:
                result.append(f"{path}:")
            if node.is_dir:
                names = []
                for child_name in sorted(node.children):
                    child = node.children[child_name]
                    names.append(child_name + "/" if child.is_dir else child_name)
                if names:
                    result.append("\n".join(names))
            else:
                result.append(node.name)
        return "\n".join(result), ok

    def cmd_cd(self, args):
        if len(args) > 1:
            return "cd: слишком много аргументов", False
        path = args[0] if args else "/"
        try:
            node = self.vfs.resolve(path)
        except Exception as e:
            return f"cd: {e}", False
        if not node.is_dir:
            return f"cd: {path}: не каталог", False
        self.vfs.cwd = node
        return "", True

    def cmd_pwd(self, args):
        if args:
            return "pwd: команда не принимает аргументов", False
        return self.vfs.get_path(), True

    def cmd_exit(self, args):
        if args:
            return "exit: команда не принимает аргументов", False
        self.finished = True
        return "", True
