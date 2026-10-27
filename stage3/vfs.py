# Виртуальная файловая система. Всё хранится в памяти, на диск ничего не распаковывается.
import base64
import binascii
import xml.etree.ElementTree as ET


class VFSError(Exception):
    pass


class File:
    def __init__(self, name, data):
        self.name = name
        self.data = data  # bytes
        self.parent = None
        self.is_dir = False


class Dir:
    def __init__(self, name):
        self.name = name
        self.children = {}  # имя -> File или Dir
        self.parent = None
        self.is_dir = True

    def add(self, node):
        if node.name in self.children:
            raise VFSError(f"дубликат имени '{node.name}'")
        node.parent = self
        self.children[node.name] = node


class VFS:
    def __init__(self, name="VFS"):
        self.name = name
        self.root = Dir("")
        self.cwd = self.root

    def get_path(self):
        # собираем путь от текущей папки вверх до корня
        parts = []
        node = self.cwd
        while node.parent is not None:
            parts.append(node.name)
            node = node.parent
        return "/" + "/".join(reversed(parts))

    def resolve(self, path):
        # находит узел по абсолютному или относительному пути
        node = self.root if path.startswith("/") else self.cwd
        for part in path.split("/"):
            if part == "" or part == ".":
                continue
            if not node.is_dir:
                raise VFSError(f"{path}: не каталог")
            if part == "..":
                if node.parent is not None:
                    node = node.parent
            elif part in node.children:
                node = node.children[part]
            else:
                raise VFSError(f"{path}: нет такого файла или каталога")
        return node


def _build(xml_elem, directory):
    for child in xml_elem:
        name = child.get("name")
        if not name or "/" in name:
            raise VFSError(f"некорректное имя элемента: {name!r}")
        if child.tag == "dir":
            new_dir = Dir(name)
            directory.add(new_dir)
            _build(child, new_dir)
        elif child.tag == "file":
            encoding = child.get("encoding", "text")
            text = child.text or ""
            if encoding == "base64":
                try:
                    data = base64.b64decode(text.strip(), validate=True)
                except (binascii.Error, ValueError):
                    raise VFSError(f"файл '{name}': некорректный base64")
            elif encoding == "text":
                data = text.encode("utf-8")
            else:
                raise VFSError(f"файл '{name}': неизвестная кодировка '{encoding}'")
            directory.add(File(name, data))
        else:
            raise VFSError(f"неизвестный тег <{child.tag}>")


def load_vfs(path):
    try:
        tree = ET.parse(path)
    except OSError as e:
        raise VFSError(f"не удалось открыть файл VFS: {e}")
    except ET.ParseError as e:
        raise VFSError(f"ошибка XML: {e}")
    xml_root = tree.getroot()
    if xml_root.tag != "vfs":
        raise VFSError("корневой тег должен быть <vfs>")
    vfs = VFS(xml_root.get("name", "VFS"))
    _build(xml_root, vfs.root)
    return vfs
