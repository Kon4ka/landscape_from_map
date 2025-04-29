import os
import tkinter as tk
from tkinter import ttk
import pyperclip

MAX_TEXT_LENGTH = 3000
COMMENT_PREFIXES = {
    '.py': '#',
    '.js': '//',
    '.c': '//',
    '.cpp': '//',
    '.java': '//',
    '.html': '<!--',
    '.xml': '<!--',
    '.ini': ';',
}

project_root = os.path.abspath(os.path.dirname(__file__))
file_tree = {}
checkbox_vars = {}

def collect_file_tree():
    tree = {}
    for dirpath, dirnames, filenames in os.walk(project_root):
        dirnames[:] = [d for d in dirnames if not d.startswith('.')]
        for f in filenames:
            full_path = os.path.join(dirpath, f)
            if os.path.isfile(full_path):
                rel_path = os.path.relpath(full_path, project_root)
                tree[rel_path] = full_path
    return tree

file_tree = collect_file_tree()

class FileSelector(tk.Tk):
    def __init__(self, file_tree):
        super().__init__()
        self.title("Выбор файлов")
        self.geometry("700x750")
        self.configure(bg="#1e1e1e")

        self.comment_ignore = tk.BooleanVar(value=False)
        self.skip_empty = tk.BooleanVar(value=False)

        tk.Checkbutton(self, text="Игнорировать комментарии", variable=self.comment_ignore,
                       bg="#1e1e1e", fg="white", selectcolor="#2e2e2e", activebackground="#2e2e2e").pack(anchor="w", pady=2)
        tk.Checkbutton(self, text="Игнорировать пустые файлы", variable=self.skip_empty,
                       bg="#1e1e1e", fg="white", selectcolor="#2e2e2e", activebackground="#2e2e2e").pack(anchor="w", pady=2)

        canvas = tk.Canvas(self, bg="#1e1e1e", highlightthickness=0)
        scrollbar = tk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self.scroll_frame = tk.Frame(canvas, bg="#1e1e1e")

        self.scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.nodes = {}
        self.populate_tree(file_tree)

        tk.Button(self, text="Готово", command=self.on_done,
                  bg="#2e2e2e", fg="white", activebackground="#3e3e3e").pack(pady=10)

        self.selected_files = []

    def populate_tree(self, file_tree):
        for rel_path, full_path in sorted(file_tree.items()):
            parts = rel_path.split(os.sep)
            parent = self.scroll_frame
            full = ""
            for i, part in enumerate(parts):
                full = os.path.join(full, part)
                if full not in self.nodes:
                    f = os.path.join(project_root, full)
                    var = tk.BooleanVar()
                    checkbox_vars[full] = var

                    frame = tk.Frame(parent, bg="#1e1e1e")
                    pad = tk.Label(frame, width=4 * i, bg="#1e1e1e")
                    pad.pack(side="left")

                    cb = tk.Checkbutton(frame, text=part, variable=var,
                                        bg="#1e1e1e", fg="white", selectcolor="#2e2e2e",
                                        activebackground="#2e2e2e", anchor="w", command=lambda p=full: self.toggle_children(p))
                    cb.pack(side="left", fill="x", expand=True)
                    frame.pack(fill="x", anchor="w")

                    self.nodes[full] = {"frame": frame, "var": var, "children": []}

                    # Привязываем к родителю
                    if i > 0:
                        parent_path = os.path.join(*parts[:i])
                        self.nodes[parent_path]["children"].append(full)
                parent = self.scroll_frame

    def toggle_children(self, path):
        val = checkbox_vars[path].get()
        for child in self.nodes[path]["children"]:
            checkbox_vars[child].set(val)
            self.toggle_children(child)

    def on_done(self):
        self.selected_files = []
        for path, data in self.nodes.items():
            full_path = os.path.join(project_root, path)
            if os.path.isfile(full_path) and data["var"].get():
                if self.skip_empty.get():
                    try:
                        if os.path.getsize(full_path) == 0:
                            continue
                    except Exception:
                        continue
                self.selected_files.append(full_path)
        self.destroy()

def read_and_format(files, ignore_comments):
    result = ""
    for fpath in files:
        rel_path = os.path.relpath(fpath, project_root)
        ext = os.path.splitext(fpath)[1]
        try:
            with open(fpath, "r", encoding="utf-8") as f:
                lines = f.readlines()
                if ignore_comments and ext in COMMENT_PREFIXES:
                    prefix = COMMENT_PREFIXES[ext]
                    lines = [l for l in lines if not l.strip().startswith(prefix)]
                elif ignore_comments and ext in {'.html', '.xml'}:
                    import re
                    content = "".join(lines)
                    content = re.sub(r'<!--.*?-->', '', content, flags=re.DOTALL)
                    lines = content.splitlines(keepends=True)
                result += f"====== {rel_path} ======\n"
                result += "".join(lines) + "\n"
        except Exception as e:
            result += f"====== {rel_path} (не удалось прочитать) ======\nОшибка: {e}\n\n"
    return result

if __name__ == "__main__":
    file_tree = collect_file_tree()
    app = FileSelector(file_tree)
    app.mainloop()

    if app.selected_files:
        content = read_and_format(app.selected_files, app.comment_ignore.get())
        if len(content) <= MAX_TEXT_LENGTH:
            pyperclip.copy(content)
            print("Содержимое скопировано в буфер обмена.")
        else:
            with open(os.path.join(project_root, "scan.txt"), "w", encoding="utf-8") as f:
                f.write(content)
            print("Содержимое записано в файл scan.txt рядом со скриптом.")
    else:
        print("Файлы не выбраны.")
