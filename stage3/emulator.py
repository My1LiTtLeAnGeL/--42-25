# Эмулятор оболочки с GUI (tkinter).
# Запуск: python emulator.py --vfs vfs/files.xml --prompt "user@vfs$" --script scripts/start_full.txt
import argparse
import sys
try:
    import tkinter as tk
    from tkinter import scrolledtext
except ImportError:
    print("Не найден tkinter. Переустановите Python и включите опцию 'tcl/tk and IDLE'.")
    sys.exit(1)

from shell import Shell
from vfs import VFS, VFSError, load_vfs


class App:
    def __init__(self, vfs, prompt, script_path):
        self.vfs = vfs
        self.prompt = prompt
        self.shell = Shell(vfs)

        self.root = tk.Tk()
        self.root.title(f"Эмулятор - [VFS: {vfs.name}]")  # имя VFS в заголовке
        self.root.geometry("720x460")

        # сначала поле ввода (прижато вниз), потом окно вывода,
        # иначе поле ввода может уехать за нижний край окна
        frame = tk.Frame(self.root)
        frame.pack(side="bottom", fill="x")

        self.output = scrolledtext.ScrolledText(
            self.root, height=10, state="disabled", bg="black", fg="lightgreen", font=("Courier", 11))
        self.output.pack(side="top", fill="both", expand=True)

        tk.Label(frame, text=prompt, font=("Courier", 11)).pack(side="left")
        # тёмное поле ввода с белым текстом и белым курсором, чтобы его было видно
        self.entry = tk.Entry(frame, font=("Courier", 11), bg="#303030", fg="white",
                              insertbackground="white", relief="sunken", bd=3)
        self.entry.pack(side="left", fill="x", expand=True)
        self.entry.bind("<Return>", self.on_enter)

        # клик по окну вывода возвращает курсор в поле ввода
        self.output.bind("<Button-1>", lambda e: self.entry.after(1, self.entry.focus_force))

        # поднимаем окно поверх остальных и отдаём фокус полю ввода
        self.root.lift()
        self.root.attributes("-topmost", True)
        self.root.after(300, lambda: self.root.attributes("-topmost", False))
        self.root.after(400, self.entry.focus_force)

        if script_path:
            # запускаем скрипт, когда окно уже нарисовалось
            self.root.after(200, lambda: self.run_script(script_path))

    def write(self, text):
        self.output.config(state="normal")
        self.output.insert("end", text + "\n")
        self.output.see("end")
        self.output.config(state="disabled")

    def execute(self, line):
        """Выполняет команду, печатает вывод. Возвращает True, если ошибок не было."""
        out, ok = self.shell.run(line)
        if out:
            self.write(out)
        if self.shell.finished:
            self.root.destroy()
        return ok

    def on_enter(self, event):
        line = self.entry.get()
        self.entry.delete(0, "end")
        self.write(f"{self.prompt} {line}")
        self.execute(line)

    def run_script(self, path):
        try:
            with open(path, encoding="utf-8") as f:
                lines = f.read().splitlines()
        except OSError as e:
            self.write(f"Ошибка: не удалось открыть скрипт: {e}")
            return
        for number, line in enumerate(lines, 1):
            line = line.strip()
            if line == "" or line.startswith("#"):
                continue
            self.write(f"{self.prompt} {line}")  # показываем ввод как будто пользователь печатает
            ok = self.execute(line)
            if self.shell.finished:
                return
            if not ok:
                self.write(f"Ошибка в стартовом скрипте (строка {number}): '{line}'. Выполнение остановлено.")
                return

    def start(self):
        self.root.mainloop()


def main():
    parser = argparse.ArgumentParser(description="Эмулятор оболочки с VFS")
    parser.add_argument("--vfs", help="путь к XML-файлу с VFS")
    parser.add_argument("--prompt", default="$", help="приглашение к вводу")
    parser.add_argument("--script", help="путь к стартовому скрипту")
    args = parser.parse_args()

    # отладочный вывод всех параметров
    debug = [
        "[DEBUG] Параметры запуска:",
        f"[DEBUG]   vfs    = {args.vfs}",
        f"[DEBUG]   prompt = {args.prompt}",
        f"[DEBUG]   script = {args.script}",
    ]
    print("\n".join(debug))

    if args.vfs:
        try:
            vfs = load_vfs(args.vfs)
        except VFSError as e:
            print(f"Ошибка загрузки VFS: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        vfs = VFS()  # пустая VFS, если путь не указан

    app = App(vfs, args.prompt, args.script)
    for line in debug:
        app.write(line)
    app.write("Вводите команды в строку внизу окна и нажимайте Enter.")
    app.start()


if __name__ == "__main__":
    main()
