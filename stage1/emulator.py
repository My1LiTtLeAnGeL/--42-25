# Этап 1. REPL с GUI.  Запуск: python emulator.py
import sys

try:
    import tkinter as tk
    from tkinter import scrolledtext
except ImportError:
    print("Не найден tkinter. Переустановите Python и включите опцию 'tcl/tk and IDLE'.")
    sys.exit(1)

from shell import Shell

PROMPT = "$"


class App:
    def __init__(self):
        self.shell = Shell()
        self.root = tk.Tk()
        self.root.title("Эмулятор - VFS")  # в заголовке есть имя VFS
        self.root.geometry("720x460")

        # сначала поле ввода (прижато вниз), потом окно вывода,
        # иначе поле ввода может уехать за нижний край окна
        frame = tk.Frame(self.root)
        frame.pack(side="bottom", fill="x")

        self.output = scrolledtext.ScrolledText(
            self.root, height=10, state="disabled", bg="black", fg="lightgreen", font=("Courier", 11))
        self.output.pack(side="top", fill="both", expand=True)

        tk.Label(frame, text=PROMPT, font=("Courier", 11)).pack(side="left")
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

    def write(self, text):
        self.output.config(state="normal")
        self.output.insert("end", text + "\n")
        self.output.see("end")
        self.output.config(state="disabled")

    def on_enter(self, event):
        line = self.entry.get()
        self.entry.delete(0, "end")
        self.write(f"{PROMPT} {line}")
        out, ok = self.shell.run(line)
        if out:
            self.write(out)
        if self.shell.finished:
            self.root.destroy()


if __name__ == "__main__":
    app = App()
    app.write("Вводите команды в строку внизу окна и нажимайте Enter.")
    app.root.mainloop()
