# Этап 2. Конфигурация.
# Запуск: python emulator.py --vfs examples/myvfs --prompt "user@vfs$" --script scripts/start_stub.txt
import argparse
import os
import sys

try:
    import tkinter as tk
    from tkinter import scrolledtext
except ImportError:
    print("Не найден tkinter. Переустановите Python и включите опцию 'tcl/tk and IDLE'.")
    sys.exit(1)

from shell import Shell


class App:
    def __init__(self, vfs_path, prompt, script_path):
        self.prompt = prompt
        self.shell = Shell()

        # имя VFS берём из последней части пути
        vfs_name = os.path.basename(vfs_path.rstrip("/\\")) if vfs_path else "VFS"

        self.root = tk.Tk()
        self.root.title(f"Эмулятор - [VFS: {vfs_name}]")
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
            self.root.after(200, lambda: self.run_script(script_path))

    def write(self, text):
        self.output.config(state="normal")
        self.output.insert("end", text + "\n")
        self.output.see("end")
        self.output.config(state="disabled")

    def execute(self, line):
        """Выполняет команду. Возвращает True, если ошибок не было."""
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
            self.write(f"{self.prompt} {line}")  # показываем ввод
            ok = self.execute(line)
            if self.shell.finished:
                return
            if not ok:
                self.write(f"Ошибка в стартовом скрипте (строка {number}): '{line}'. Выполнение остановлено.")
                return


def main():
    parser = argparse.ArgumentParser(description="Эмулятор оболочки")
    parser.add_argument("--vfs", help="путь к физическому расположению VFS")
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

    app = App(args.vfs, args.prompt, args.script)
    for line in debug:
        app.write(line)
    app.write("Вводите команды в строку внизу окна и нажимайте Enter.")
    app.root.mainloop()


if __name__ == "__main__":
    main()
