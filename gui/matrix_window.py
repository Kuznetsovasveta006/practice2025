from utils import *


class MatrixWindow(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self._initialize_window()
        self._initialize_variables()
        self._create_ui()

    def _initialize_window(self):
        """Инициализация окна"""
        UIManager.initialize_window(self, "Adjacency Matrix")

    def _initialize_variables(self):
        """Инициализация переменных"""
        self.size_var = tk.IntVar(value=5)
        self.entries = []

    def _create_ui(self):
        """Создание пользовательского интерфейса"""
        self._create_top_frame()
        self._create_size_frame()
        self._create_table_frame()

    def _create_top_frame(self):
        """Создание верхней панели с заголовком и кнопками"""
        buttons = [
            ("Create graph", self.create_graph, Styles.MATRIX_BTN_STYLE),
            ("↻", self.random_matrix, {**Styles.MATRIX_BTN_STYLE, "width": 4})
        ]
        UIManager.create_header_frame(self, "Adj matrix", buttons)

    def _create_size_frame(self):
        """Создание панели для выбора размера матрицы"""
        UIManager.create_matrix_control(self, "Size:", self.size_var, "Fill", self.create_matrix_table)

    def _create_table_frame(self):
        """Создание фрейма для таблицы матрицы"""
        self.table_frame = tk.Frame(self)
        self.table_frame.pack(pady=18, padx=12, fill=tk.BOTH, expand=True)

    def create_matrix_table(self):
        """Создание таблицы матрицы"""
        self._clear_table_frame()
        size = self._get_validated_size()
        if size > 0:

            self._initialize_matrix_arrays(size)
            self._configure_grid_layout(size)
            self._create_table_headers(size)
            self._create_matrix_cells(size)

    def _clear_table_frame(self):
        """Очистка фрейма таблицы"""
        for widget in self.table_frame.winfo_children():
            widget.destroy()

    def _get_validated_size(self):
        """Получение и валидация размера матрицы"""
        size = self.size_var.get()
        validated_size = Validator.validate_matrix_size(size)
        if validated_size != size:
            self.size_var.set(validated_size)
        return validated_size

    def _initialize_matrix_arrays(self, size):
        """Инициализация массивов для хранения элементов матрицы"""
        self.entries = [[None for _ in range(size)] for _ in range(size)]
        self.labels = [[None for _ in range(size)] for _ in range(size)]

    def _configure_grid_layout(self, size):
        """Настройка сетки для таблицы"""
        UIManager.configure_grid_frame(self.table_frame, size + 1, size + 1)

    def _create_table_headers(self, size):
        """Создание заголовков таблицы"""
        UIManager.create_table_header(self.table_frame, "", 0, 0)
        for j in range(size):
            UIManager.create_table_header(self.table_frame, str(j), 0, j + 1)
            UIManager.create_table_header(self.table_frame, str(j), j + 1, 0)

    def _create_matrix_cells(self, size):
        """Создание ячеек матрицы"""
        for i in range(size):
            for j in range(size):
                if j <= i:
                    self._create_diagonal_cell(i, j)
                else:
                    self._create_editable_cell(i, j)

    def _create_diagonal_cell(self, i, j):
        """Создание ячейки на диагонали (неизменяемая)"""
        l = tk.Label(self.table_frame, text="0",
                     font=("Arial", 10), bg=Colors.MATRIX_BTN_BG, fg="#666666",
                     relief="ridge", bd=1, anchor="center")
        l.grid(row=i + 1, column=j + 1, padx=0, pady=0, sticky="nsew")
        self.labels[i][j] = l

    def _create_editable_cell(self, i, j):
        """Создание редактируемой ячейки"""
        btn = tk.Button(self.table_frame, text="0",
                        font=("Arial", 10), relief="ridge", bg="#F4F4F4",
                        activebackground=Colors.MATRIX_BTN_BG, bd=1,
                        command=lambda x=i, y=j: self.toggle_cell(x, y))
        btn.grid(row=i + 1, column=j + 1, padx=0, pady=0, sticky="nsew")
        self.entries[i][j] = btn

    def toggle_cell(self, i, j):
        btn = self.entries[i][j]
        val = btn["text"]
        if val == "0":
            new_val = "1"
            btn.config(text="1", bg=Colors.MATRIX_BTN_ACTIVE_BG, fg="white")
        else:
            new_val = "0"
            btn.config(text="0", bg="#F4F4F4", fg="black")

        if self.labels[j][i]:
            self.labels[j][i].config(text=new_val)

    def random_matrix(self):
        """Генерация случайной матрицы"""
        size = self.size_var.get()
        matrix = self._generate_random_matrix(size)

        if size > 15:
            self._handle_large_matrix(matrix)
        else:
            self._handle_small_matrix(matrix)

    def _generate_random_matrix(self, size):
        """Генерация случайной симметричной матрицы"""
        return RandomGenerator.generate_random_matrix(size)

    def _handle_large_matrix(self, matrix):
        """Обработка большой матрицы"""
        self.large_matrix = matrix.copy()
        self.show_large_matrix(matrix)

    def _handle_small_matrix(self, matrix):
        """Обработка маленькой матрицы"""
        self.create_matrix_table()
        self._update_matrix_display(matrix)

    def _update_matrix_display(self, matrix):
        """Обновление отображения матрицы"""
        size = matrix.shape[0]
        for i in range(size):
            for j in range(i + 1, size):
                val = matrix[i][j]
                btn = self.entries[i][j]
                btn.config(text=str(val))
                if self.labels[j][i]:
                    self.labels[j][i].config(text=str(val))

    def create_graph(self):
        """Создание графа из матрицы"""
        size = self.size_var.get()
        matrix = self._get_matrix_for_graph(size)
        if matrix is not None:
            self.master.update_graph(matrix)

    def _get_matrix_for_graph(self, size):
        """Получение матрицы для создания графа"""
        if size > 15 and hasattr(self, 'large_matrix'):
            return self.large_matrix.copy()
        else:
            return self._build_matrix_from_ui(size)

    def _build_matrix_from_ui(self, size):
        """Построение матрицы из пользовательского интерфейса"""
        matrix = np.zeros((size, size), dtype=int)
        try:
            for i in range(size):
                for j in range(i + 1, size):
                    val = self._get_cell_value(i, j)
                    validated_val = Validator.validate_cell_value(val)
                    if validated_val is None:
                        return None
                    matrix[i][j] = matrix[j][i] = validated_val
            return matrix
        except Exception:
            UIManager.show_error("Input error", "Matrix values must be 0 or 1")
            return None

    def _get_cell_value(self, i, j):
        """Получение значения ячейки"""
        btn = self.entries[i][j]
        return int(btn["text"])

    def show_large_matrix(self, matrix):
        """Отображение большой матрицы в текстовом виде"""
        self._clear_table_frame()
        text_content = self._matrix_to_text(matrix)
        self._create_text_widget_with_scrollbars(text_content, matrix.shape[0])

    def _matrix_to_text(self, matrix):
        """Преобразование матрицы в текстовый формат"""
        return Formatter.matrix_to_text(matrix)

    def _create_text_widget_with_scrollbars(self, text_content, size):
        """Создание текстового виджета с полосами прокрутки"""
        # Создаем текстовый виджет
        text_widget = tk.Text(self.table_frame, wrap='none', font=("Courier", 10),
                              height=min(20, size), width=min(80, size * 2))
        text_widget.insert('1.0', text_content)
        text_widget.config(state='disabled')
        text_widget.pack(fill=tk.BOTH, expand=True)

        # Создаем вертикальную полосу прокрутки
        yscroll = tk.Scrollbar(self.table_frame, orient='vertical', command=text_widget.yview)
        yscroll.pack(side=tk.RIGHT, fill=tk.Y)
        text_widget.config(yscrollcommand=yscroll.set)

        # Создаем горизонтальную полосу прокрутки
        xscroll = tk.Scrollbar(self.table_frame, orient='horizontal', command=text_widget.xview)
        xscroll.pack(side=tk.BOTTOM, fill=tk.X)
        text_widget.config(xscrollcommand=xscroll.set)