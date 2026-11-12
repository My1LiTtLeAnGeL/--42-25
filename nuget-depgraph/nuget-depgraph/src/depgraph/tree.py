"""Вывод зависимостей в виде ASCII-дерева."""

BRANCH = "|-- "
LAST_BRANCH = "`-- "
PIPE = "|   "
BLANK = "    "
REPEAT_MARK = " (см. выше)"


def child_items(graph, name, prefix):
    """Готовит детей пакета для стека (в обратном порядке)."""
    children = graph.get(name, [])
    last = len(children) - 1
    items = [(child, prefix, index == last)
             for index, child in enumerate(children)]
    items.reverse()
    return items


def build_tree_lines(graph, root):
    """Строит строки дерева зависимостей пакета root.

    Если пакет уже был показан раньше (общая зависимость или цикл), его
    поддерево повторно не раскрывается, а рядом пишется пометка.
    Обход сделан через стек, без рекурсии.
    """
    lines = [root]
    shown = {root}
    stack = child_items(graph, root, "")
    while stack:
        name, prefix, is_last = stack.pop()
        branch = LAST_BRANCH if is_last else BRANCH
        repeated = name in shown
        mark = REPEAT_MARK if repeated and graph.get(name) else ""
        lines.append(f"{prefix}{branch}{name}{mark}")
        if not repeated:
            shown.add(name)
            indent = BLANK if is_last else PIPE
            stack.extend(child_items(graph, name, prefix + indent))
    return lines
