import os
import tkinter as tk
from tkinter import filedialog, messagebox
import pyperclip

# ========== НАСТРОЙКА ==========
# Укажи путь вручную, если скрипт работает с сетевого диска:
# Например: r"//toster/Sovinoe/LockNet/Share/Diploma/Code/landscape_from_map"
BASE_DIR = r""  # оставить пустым, если использовать путь к самому скрипту
# ===============================

# Функция для рекурсивного обхода папки
def scan_directory(base_path):
    file_paths = []
    for root, dirs, files in os.walk(base_path):
        for file in files:
            file_paths.append(os.path.relpath(os.path.join(root, file), base_path))
    return file_paths

# Функция для фильтрации комментариев
def remove_comments(text, filepath):
    ext = os.path.splitext(filepath)[1].lower()
    if ext in ['.py', '.cpp', '.c', '.h', '.hpp', '.java', '.js', '.ts', '.html', '.xml', '.css', '.json', '.md', '.txt']:
        lines = text.splitlines()
        filtered = []
        for line in lines:
            stripped = line.strip()
            if not (stripped.startswith('#') or stripped.startswith('//') or stripped.startswith('/*') or stripped.startswith('*') or stripped.startswith('--') or stripped.startswith('<!--')):
                filtered.append(line)
        return '\n'.join(filtered)
    return text

# Основная функция работы скрипта
def main():
    root = tk.Tk()
    root.withdraw()  # Скрыть главное окно

    base_dir = BASE_DIR if BASE_DIR else os.path.dirname(os.path.abspath(__file__))
    if not os.path.exists(base_dir):
        messagebox.showerror("Ошибка", f"Указанный путь не существует:\n{base_dir}")
        return

    all_files = scan_directory(base_dir)

    selected_files = filedialog.askopenfilenames(
        title="Выберите файлы для обработки",
        initialdir=base_dir,
        filetypes=[("Все файлы", "*.*")],
        multiple=True
    )

    if not selected_files:
        messagebox.showinfo("Информация", "Файлы не выбраны.")
        return

    remove_comments_flag = messagebox.askyesno("Фильтрация комментариев", "Удалять комментарии из текстов?")

    output_text = ""
    for filepath in selected_files:
        relative_path = os.path.relpath(filepath, base_dir)
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                if remove_comments_flag:
                    content = remove_comments(content, filepath)
        except Exception as e:
            content = f"[Ошибка чтения файла: {e}]"

        output_text += f"====== {relative_path} ======\n"
        output_text += f"{content}\n"

    if len(output_text) < 50000:
        pyperclip.copy(output_text)
        messagebox.showinfo("Готово", "Текст скопирован в буфер обмена!")
    else:
        output_path = os.path.join(base_dir, 'scan.txt')
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(output_text)
        messagebox.showinfo("Готово", f"Текст записан в файл: {output_path}")

if __name__ == "__main__":
    main()