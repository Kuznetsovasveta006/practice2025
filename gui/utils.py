import tkinter as tk
from tkinter import messagebox
import tkinter as tk
from tkinter import messagebox, filedialog
import numpy as np
import networkx as nx
import random
import networkx as nx


# Константы для цветов и стилей
class Colors:
    """Константы цветов приложения"""
    GRAPH_BG = "#BCBCBC"
    GRAPH_ACTIVE_BG = "#C0C0C0"
    PARAM_BTN_BG = "#2B2B2B"
    PARAM_BTN_ACTIVE_BG = "#444444"
    MATRIX_BTN_BG = "#A1BBD5"
    MATRIX_BTN_ACTIVE_BG = "#7A9CC6"
    NODE_COLOR = "#A1BBD5"
    EDGE_COLOR = "#A3C2D1"
    CLIQUE_NODE_COLOR = "#0F754C"
    CLIQUE_EDGE_COLOR = "#0F754C"
    BEST_LINE_COLOR = "#0F754C"
    AVG_LINE_COLOR = "#A1BBD5"


class Styles:
    """Константы стилей приложения"""
    MATRIX_BTN_STYLE = {
        "bg": Colors.MATRIX_BTN_BG,
        "activebackground": Colors.MATRIX_BTN_ACTIVE_BG,
        "font": ("Arial", 10),
        "bd": 0,
        "padx": 12,
        "pady": 2
    }
    
    PARAM_BTN_STYLE = {
        "bg": Colors.PARAM_BTN_BG,
        "fg": "white",
        "activebackground": Colors.PARAM_BTN_ACTIVE_BG,
        "activeforeground": "white"
    }
    
    CONTROL_BTN_STYLE = {
        "bg": Colors.GRAPH_BG,
        "activebackground": Colors.GRAPH_ACTIVE_BG,
        "borderwidth": 0
    }
    
    RESET_BTN_STYLE = {
        "bg": Colors.GRAPH_BG,
        "activebackground": Colors.GRAPH_ACTIVE_BG,
        "borderwidth": 0,
        "font": ("Arial", 7),
        "padx": 5,
        "pady": 3
    }


# Параметры по умолчанию
DEFAULT_PARAMS = {
    "population_size": "50",
    "max_generations": "100",
    "mutation_rate": "0.05",
    "gene_mutation": "0.1",
    "fitness_scale": "80",
    "max_cut_points": "3",
    "decr_m_prob_step": "10",
    "reduce_cuts_step": "10",
}

# Список параметров для создания полей ввода
PARAM_FIELDS = [
    ("Population size", "population_size"),
    ("Max generations amount", "max_generations"),
    ("Mutation rate", "mutation_rate"),
    ("Gene mutation", "gene_mutation"),
    ("Fitness scale", "fitness_scale"),
    ("Max cut points", "max_cut_points"),
    ("Reduce prob./cuts by", "decr_m_prob_step"),
    ("Reduction step", "reduce_cuts_step"),
]

class Formatter:
    @staticmethod
    def format_solution_list(solutions, widget_width):
        """Форматирование списка решений для отображения"""
        pad = ' ' * max(2, int(widget_width * 0.03 // 8))
        formatted_solutions = []
        for i, sol in enumerate(solutions, 1):
            s = ''.join(str(x) for x in sol)
            formatted_solutions.append(f"{pad}{i}. {s}{pad}")
        return formatted_solutions

class Validator:
    """Класс для валидации данных"""

    @staticmethod
    def validate_graph_exists(graph):
        """Проверка существования графа"""
        if graph is None:
            show_error("Error", "Graph not created!")
            return False
        return True

    @staticmethod
    def validate_graph_for_save(adj_matrix):
        """Проверка наличия графа для сохранения"""
        if adj_matrix is None:
            show_error("Ошибка", "Нет графа для сохранения!")
            return False
        return True

    @staticmethod
    def validate_parameters(entries_dict):
        """Валидация параметров из полей ввода"""
        params = {}
        for key, entry in entries_dict.items():
            value = entry.get().strip()
            if not value:
                return None, f"Поле не может быть пустым"

            # Преобразуем значения в соответствующие типы
            if key in ["population_size", "max_generations", "max_cut_points", "decr_m_prob_step", "reduce_cuts_step"]:
                params[key] = int(value)
            elif key in ["mutation_rate", "gene_mutation"]:
                params[key] = float(value)
            elif key == "fitness_scale":
                params[key] = int(value)
            else:
                params[key] = value

        return params, None

    @staticmethod
    def validate_matrix_size(size, max_size=15):
        """Валидация размера матрицы"""
        if size > max_size:
            messagebox.showwarning("Большой размер",
                                   f"Матрица размера {size} слишком большая для ручного ввода.\n"
                                   "Используйте кнопку '↻' для генерации или загрузите из файла.")
            return max_size
        return size

    @staticmethod
    def validate_cell_value(value):
        """Валидация значения ячейки матрицы"""
        try:
            val = int(value)
            if val not in (0, 1):
                raise ValueError
            return val
        except Exception:
            show_error("Input error", "Matrix values must be 0 or 1")
            return None


    @staticmethod
    def validate_matrix(matrix):
        """Валидация матрицы смежности"""
        size = len(matrix)

        # Проверяем, что матрица квадратная
        for row in matrix:
            if len(row) != size:
                return False, "Матрица должна быть квадратной"

        # Проверяем, что матрица симметричная
        for i in range(size):
            for j in range(size):
                if matrix[i][j] != matrix[j][i]:
                    return False, "Матрица смежности должна быть симметричной"

        # Проверяем, что на диагонали нули
        for i in range(size):
            if matrix[i][i] != 0:
                return False, "На диагонали матрицы должны быть нули"

        return True, "OK"

class FileManager:
    """Класс для работы с файлами"""

    @staticmethod
    def get_save_filename(title="Сохранить как...", defaultextension=".txt",
                          filetypes=[("Text files", "*.txt"), ("All files", "*.*")]):
        """Получение имени файла для сохранения"""
        return filedialog.asksaveasfilename(
            title=title,
            defaultextension=defaultextension,
            filetypes=filetypes
        )

    @staticmethod
    def get_open_filename(title="Выберите файл", filetypes=[("All files", "*.*")]):
        """Получение имени файла для открытия"""
        return filedialog.askopenfilename(title=title, filetypes=filetypes)

    def parse_matrix_from_file(filename):
        """Парсинг матрицы из файла"""
        try:
            with open(filename, 'r') as f:
                lines = f.readlines()

            # Удаляем пустые строки и лишние пробелы
            lines = [line.strip() for line in lines if line.strip()]

            if not lines:
                return None, "Файл пустой или содержит только пустые строки"

            # Парсим матрицу
            matrix = []
            for line in lines:
                row = [int(x) for x in line.split()]
                matrix.append(row)

            # Валидируем матрицу
            is_valid, message = Validator.validate_matrix(matrix)
            if not is_valid:
                return None, message

            return matrix, f"Матрица смежности загружена из файла: {filename}\nРазмер графа: {len(matrix)}x{len(matrix)}"

        except ValueError:
            return None, "Файл содержит некорректные данные. Используйте только числа, разделенные пробелами"
        except Exception as e:
            return None, f"Не удалось загрузить файл: {e}"

    @staticmethod
    def save_matrix_to_file(filename, matrix):
        """Сохранение матрицы в файл"""
        try:
            with open(filename, "w") as f:
                for row in matrix:
                    f.write(" ".join(map(str, row)) + "\n")
            show_info("Сохранено", f"Граф сохранён в файл: {filename}")
            return True
        except Exception as e:
            show_error("Ошибка", f"Не удалось сохранить файл: {e}")
            return False

    @staticmethod
    def load_matrix_from_file(filename):
        """Загрузка матрицы из файла"""
        matrix, message = FileManager.parse_matrix_from_file(filename)
        if matrix is not None:
            return np.array(matrix), message
        else:
            show_error("Ошибка", message)
            return None, message


class UIManager:
    """Универсальный менеджер для работы с UI"""

    # === Базовые UI элементы ===
    @staticmethod
    def create_frame(parent, **kwargs):
        """Создание фрейма"""
        return tk.Frame(parent, **kwargs)

    @staticmethod
    def create_label(parent, text="", **kwargs):
        """Создание метки"""
        return tk.Label(parent, text=text, **kwargs)

    @staticmethod
    def create_button(parent, text="", command=None, **kwargs):
        """Создание кнопки"""
        return tk.Button(parent, text=text, command=command, **kwargs)

    @staticmethod
    def create_entry(parent, **kwargs):
        """Создание поля ввода"""
        return tk.Entry(parent, **kwargs)

    @staticmethod
    def configure_grid_frame(frame, rows, cols):
        """Настройка сетки для фрейма"""
        for i in range(rows):
            frame.grid_rowconfigure(i, weight=1, minsize=30)
        for j in range(cols):
            frame.grid_columnconfigure(j, weight=1, minsize=30)

    # === Инициализация окон ===
    @staticmethod
    def initialize_window(window, title, geometry=None, resizable=(True, True)):
        """Инициализация окна"""
        window.title(title)
        if geometry:
            window.geometry(geometry)
        window.resizable(*resizable)

    @staticmethod
    def bind_resize_event(window, callback):
        """Привязка события изменения размера"""
        window.bind('<Configure>', callback)

    # === Сложные UI композиции ===
    @staticmethod
    def create_header_frame(parent, title, buttons):
        """Создание фрейма с заголовком и кнопками"""
        frame = UIManager.create_frame(parent)
        frame.pack(fill=tk.X, pady=(12, 0), padx=12)
        frame.grid_columnconfigure(1, weight=1)

        # Заголовок
        UIManager.create_label(frame, text=title, font=("Arial", 15, "bold")).grid(row=0, column=0, sticky="w")

        # Разделитель
        UIManager.create_label(frame).grid(row=0, column=1, sticky="ew")

        # Кнопки
        for i, button_data in enumerate(buttons):
            text, command, style = button_data
            btn = UIManager.create_button(frame, text=text, command=command, **style)
            btn.grid(row=0, column=i + 2, padx=(0, 7) if i < len(buttons) - 1 else (0, 0))

        return frame

    @staticmethod
    def create_control_frame(parent, label_text, entry_var, button_text, button_command):
        """Создание фрейма с меткой, полем ввода и кнопкой"""
        frame = UIManager.create_frame(parent)
        frame.pack(fill=tk.X, pady=(12, 0), padx=12)
        frame.grid_columnconfigure(1, weight=1)

        # Метка
        UIManager.create_label(frame, text=label_text, font=("Arial", 12)).grid(row=0, column=0, sticky="w")

        # Разделитель
        UIManager.create_label(frame).grid(row=0, column=1, sticky="ew")

        # Поле ввода
        entry = UIManager.create_entry(frame, textvariable=entry_var, width=4, font=("Arial", 11))
        entry.grid(row=0, column=2, padx=(0, 7))

        # Кнопка
        btn = UIManager.create_button(frame, text=button_text, command=button_command, width=4,
                                      **Styles.MATRIX_BTN_STYLE)
        btn.grid(row=0, column=3)

        return frame

    @staticmethod
    def create_table_header(parent, text, row, col, **kwargs):
        """Создание заголовка таблицы"""
        header = UIManager.create_label(parent, text=text, font=("Arial", 10, "bold"),
                                        relief="ridge", bd=1, bg=Colors.MATRIX_BTN_BG, anchor="center", **kwargs)
        header.grid(row=row, column=col, padx=0, pady=0, sticky="nsew")
        return header


class MatrixGenerator:
    """Класс для генерации матриц"""

    @staticmethod
    def generate_random_matrix(size):
        """Генерация случайной симметричной матрицы"""
        matrix = np.zeros((size, size), dtype=int)
        for i in range(size):
            for j in range(i + 1, size):
                val = np.random.randint(0, 2)
                matrix[i][j] = matrix[j][i] = val
        return matrix

    @staticmethod
    def matrix_to_text(matrix):
        """Преобразование матрицы в текстовый формат"""
        lines = []
        for row in matrix:
            lines.append(' '.join(map(str, row)))
        return '\n'.join(lines)

def show_error(title, message):
    """Утилита для показа ошибок"""
    messagebox.showerror(title, message)


def show_info(title, message):
    """Утилита для показа информационных сообщений"""
    messagebox.showinfo(title, message)


def create_button(parent, **kwargs):
    """Утилита для создания кнопки с общими стилями"""
    return tk.Button(parent, **kwargs)


def create_frame(parent, **kwargs):
    """Утилита для создания фрейма с общими стилями"""
    return tk.Frame(parent, **kwargs)


def create_label(parent, **kwargs):
    """Утилита для создания метки с общими стилями"""
    return tk.Label(parent, **kwargs)


def create_parameter_fields(parent, entries_dict, callback=None):
    """Создание полей параметров"""
    for i, (label, key) in enumerate(PARAM_FIELDS):
        create_label(parent, text=label).pack(anchor="w", pady=(8 if i == 0 else 2, 0), padx=5)
        entry = tk.Entry(parent, width=16)
        entry.pack(fill=tk.X, padx=5, pady=2)
        if callback:
            entry.bind('<KeyRelease>', callback)
        entries_dict[key] = entry


def set_default_values(entries_dict):
    """Установка значений по умолчанию"""
    for key, value in DEFAULT_PARAMS.items():
        if key in entries_dict:
            entries_dict[key].delete(0, tk.END)
            entries_dict[key].insert(0, value)


def generate_random_solutions(population_size, matrix_size):
    """Генерация случайных решений для алгоритма"""
    solutions = []
    for _ in range(population_size):
        k = random.randint(1, matrix_size)  # случайное количество единиц
        sol = [0] * matrix_size
        ones_indices = random.sample(range(matrix_size), k)
        for idx in ones_indices:
            sol[idx] = 1
        solutions.append(sol)
    return solutions



def create_control_panel(parent, play_img, step_img, save_img, attach_img,
                        play_cmd, step_cmd, save_cmd, load_cmd):
    """Создание панели управления"""
    control_frame = create_frame(parent, bg=Colors.GRAPH_BG)
    control_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=5)

    # Кнопки воспроизведения
    play_btn = create_button(control_frame, image=play_img, command=play_cmd, **Styles.CONTROL_BTN_STYLE)
    play_btn.pack(side=tk.LEFT, padx=5)
    step_btn = create_button(control_frame, image=step_img, command=step_cmd, **Styles.CONTROL_BTN_STYLE)
    step_btn.pack(side=tk.LEFT, padx=5)

    # Spacer для центрирования
    create_label(control_frame, bg=Colors.GRAPH_BG).pack(side=tk.LEFT, expand=True)

    # Информационная панель
    info_frame = create_frame(control_frame, bg=Colors.GRAPH_BG)
    info_frame.pack(side=tk.LEFT)
    generation_label = create_label(info_frame, text="Generations: 0", width=18, anchor="center", bg=Colors.GRAPH_BG)
    generation_label.pack(side=tk.TOP)
    best_clique_label = create_label(info_frame, text="Max Clique: -", width=18, anchor="center", bg=Colors.GRAPH_BG)
    best_clique_label.pack(side=tk.TOP)

    create_label(control_frame, bg=Colors.GRAPH_BG).pack(side=tk.LEFT, expand=True)

    # Правые кнопки
    right_btns = create_frame(control_frame, bg=Colors.GRAPH_BG)
    right_btns.pack(side=tk.RIGHT)
    load_btn = create_button(right_btns, text="📎", image=attach_img, command=load_cmd, **Styles.CONTROL_BTN_STYLE)
    load_btn.pack(side=tk.LEFT, padx=5)
    save_btn = create_button(right_btns, image=save_img, command=save_cmd, **Styles.CONTROL_BTN_STYLE)
    save_btn.pack(side=tk.LEFT, padx=5)

    return control_frame, generation_label, best_clique_label