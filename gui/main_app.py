from right_widgets import *
from zoom import ZoomableWidget
from matrix_window import *
import numpy as np
import networkx as nx

class MainApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self._initialize_window()
        self._initialize_state()
        self.create_widgets()
        self._bind_events()

    def _initialize_window(self):
        """Инициализация окна приложения"""
        UIManager.initialize_window(self, "Genetic Algorithm Graph GUI", "1100x600")

    def _initialize_state(self):
        """Инициализация состояния приложения"""
        self.graph = None
        self.adj_matrix = None
        self.population = []
        self.current_clique = None
        self.graph_layout = None
        self.generation_counter = 0
        self.parameters_changed = False

    def _bind_events(self):
        """Привязка событий к окну"""
        UIManager.bind_resize_event(self, self.on_resize)

    def create_widgets(self):
        """Создание всех виджетов интерфейса"""
        self._create_main_container()
        self._create_left_panel()
        self._create_graph_area()
        self._create_right_panel()
        self._load_icons()
        self._create_control_panel()

    def _create_main_container(self):
        """Создание основного контейнера"""
        self.main_frame = tk.Frame(self)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

    def _create_left_panel(self):
        """Создание левой панели с параметрами"""
        self.left_panel = tk.Frame(self.main_frame)
        self.left_panel.pack(side=tk.LEFT, fill=tk.Y)
        self.entries = {}

        # Создаем поля параметров
        create_parameter_fields(self.left_panel, self.entries, self.mark_parameters_changed)

        # Создаем кнопки параметров
        self._create_parameter_buttons()

    def _create_parameter_buttons(self):
        """Создание кнопок для параметров"""
        self.buttons_frame = tk.Frame(self.left_panel)
        self.buttons_frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.default_btn = tk.Button(self.buttons_frame, text="Set default", 
                                   command=self.set_default_values, **Styles.PARAM_BTN_STYLE)
        self.default_btn.pack(fill=tk.X, padx=5, pady=(0, 2))
        
        self.matrix_btn = tk.Button(self.buttons_frame, text="Enter matrix", 
                                  command=self.open_matrix_window, **Styles.PARAM_BTN_STYLE)
        self.matrix_btn.pack(fill=tk.X, padx=5)

    def _create_graph_area(self):
        """Создание центральной области с графом"""
        self.graph_frame = tk.Frame(self.main_frame, bg=Colors.GRAPH_BG)
        self.graph_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Горизонтальный контейнер
        center_content = tk.Frame(self.graph_frame, bg=Colors.GRAPH_BG)
        center_content.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Создаем область графа
        self._create_graph_visualization(center_content)

    def _create_graph_visualization(self, parent):
        """Создание области визуализации графа"""
        graph_area = tk.Frame(parent, bg=Colors.GRAPH_BG)
        graph_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Создаем matplotlib фигуру
        self.fig, self.ax = plt.subplots(figsize=(5, 4))
        self.canvas = FigureCanvasTkAgg(self.fig, master=graph_area)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Инициализируем зум для графа
        self.graph_zoom_widget = ZoomableWidget(self.canvas, self.ax, zoom_type="graph")

        # Кнопка reset для графа
        self.reset_graph_btn = tk.Button(graph_area, text="Reset", 
                                       command=self.reset_graph_zoom, **Styles.RESET_BTN_STYLE)
        self.reset_graph_btn.place(relx=0.95, rely=0.03, anchor="ne")

    def _create_right_panel(self):
        """Создание правой панели с решениями и графиком фитнеса"""
        center_content = self.graph_frame.winfo_children()[0]  # Получаем center_content
        
        # Создаем контейнер для правых виджетов
        right_widgets = tk.Frame(center_content, width=320, bg=Colors.GRAPH_BG)
        right_widgets.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        right_widgets.pack_propagate(False)

        # Создаем фрейм для списка решений
        solution_frame = tk.Frame(right_widgets, bg=Colors.GRAPH_BG, height=175)
        solution_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=False, pady=(0, 5))
        solution_frame.pack_propagate(False)

        # Создаем фрейм для графика фитнеса
        fitness_frame = tk.Frame(right_widgets, bg=Colors.GRAPH_BG)
        fitness_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Создаем виджеты
        self.solution_list = SolutionListWidget(solution_frame)
        self.solution_list.pack(fill=tk.BOTH, expand=True)
        self.fitness_widget = FitnessPlotWidget(fitness_frame)
        self.fitness_widget.pack(fill=tk.BOTH, expand=True)

    def _load_icons(self):
        """Загрузка иконок для кнопок"""
        self.play_img = tk.PhotoImage(file="./icons/play.png")
        self.step_img = tk.PhotoImage(file="./icons/step.png")
        self.save_img = tk.PhotoImage(file="./icons/save.png")
        self.attach_img = tk.PhotoImage(file="./icons/attach_file.png")

    def _create_control_panel(self):
        """Создание панели управления"""
        _, self.generation_label, self.best_clique_label = create_control_panel(
            self.graph_frame, self.play_img, self.step_img, self.save_img, self.attach_img,
            self.run_algorithm, self.step_algorithm, self.save_graph, self.load_adjacency_matrix
        )

    def reset_graph_zoom(self):
        self.graph_zoom_widget.reset_zoom()

    def open_matrix_window(self):
        MatrixWindow(self)

    def update_graph(self, adj_matrix):
        """Обновление графа с новой матрицей смежности"""
        self.adj_matrix = adj_matrix
        self.graph = nx.from_numpy_array(adj_matrix)
        self.graph_layout = nx.spring_layout(self.graph, seed=42)
        self._draw_graph()
        self._reset_algorithm_state()

    def _draw_graph(self, highlight_clique=False):
        """Отрисовка графа с возможностью выделения клики"""
        if self.graph is None or self.adj_matrix is None:
            return
            
        if highlight_clique and self.current_clique:
            node_colors = self._get_clique_node_colors()
            edge_colors = self._get_clique_edge_colors()
        else:
            node_colors = [Colors.NODE_COLOR] * len(self.adj_matrix)
            edge_colors = [Colors.EDGE_COLOR] * len(self.graph.edges())
                
        self.ax.clear()
        nx.draw(self.graph, ax=self.ax, with_labels=True, node_color=node_colors, edge_color=edge_colors, pos=self.graph_layout)
        
        # Перекрашиваем текст для вершин клики в белый
        if highlight_clique and self.current_clique:
            self._draw_clique_labels()
            
        self.canvas.draw()

    def _get_clique_node_colors(self):
        """Получение цветов узлов с учетом клики"""
        node_colors = []
        for i in range(len(self.adj_matrix)):
            if self.current_clique and self.current_clique[i]:
                node_colors.append(Colors.CLIQUE_NODE_COLOR)
            else:
                node_colors.append(Colors.NODE_COLOR)
        return node_colors

    def _get_clique_edge_colors(self):
        """Получение цветов ребер с учетом клики"""
        edges = list(self.graph.edges())
        edge_colors = []
        clique_set = set(i for i, v in enumerate(self.current_clique) if v)
        for u, v in edges:
            if u in clique_set and v in clique_set:
                edge_colors.append(Colors.CLIQUE_EDGE_COLOR)
            else:
                edge_colors.append(Colors.EDGE_COLOR)
        return edge_colors

    def _draw_clique_labels(self):
        """Отрисовка меток для узлов клики"""
        for i, (node, pos) in enumerate(self.graph_layout.items()):
            if self.current_clique and self.current_clique[node]:
                self.ax.text(pos[0], pos[1], str(node), ha='center', va='center',
                             color='white', fontweight='bold', fontsize=12)

    def _reset_algorithm_state(self):
        """Сброс состояния алгоритма"""
        self.graph_zoom_widget.save_original_limits()
        self.best_clique_label.config(text="Max Clique: -")
        self.solution_list.listbox.delete(0, tk.END)
        self.current_clique = None
        self.generation_counter = 0
        self.generation_label.config(text="Generations: 0")

    def run_algorithm(self):
        """Основной метод запуска алгоритма"""
        if not self._validate_graph_exists():
            return

        if self.parameters_changed:
            self._reset_generation_counter()
            self.parameters_changed = False

        params = self._validate_and_get_parameters()
        if params is None:
            return

        print("Параметры алгоритма:", params)

        self._update_fitness_plot(params)
        self._generate_and_process_solutions(params)
        self._update_ui_after_algorithm()

    def _validate_graph_exists(self):
        """Проверяет, создан ли граф"""
        return Validator.validate_graph_exists(self.graph)

    def _reset_generation_counter(self):
        """Сбрасывает счетчик поколений"""
        self.generation_counter = 0
        self.generation_label.config(text="Generations: 0")

    def _validate_and_get_parameters(self):
        """Валидирует параметры и возвращает их"""
        params, error = Validator.validate_parameters(self.entries)
        if error:
            show_error("Ошибка", error)
            return None
        return params

    def _update_fitness_plot(self, params):
        """Обновляет график фитнеса"""
        generations = np.arange(params["max_generations"])
        best = np.random.randint(5, 10, size=params["max_generations"])
        avg = np.random.randint(2, 7, size=params["max_generations"])
        self.fitness_widget.draw_fitness(generations, best, avg)

    def _generate_and_process_solutions(self, params):
        """Генерирует и обрабатывает решения"""
        size = len(self.adj_matrix) if self.adj_matrix is not None else 5
        solutions = generate_random_solutions(params["population_size"], size)

        # Выбираем лучшее решение
        best_solution = max(solutions, key=sum)
        best_index = solutions.index(best_solution)
        self.current_clique = best_solution
        self.draw_graph_with_clique()

        # Обновляем список решений
        self._update_solution_list(solutions, best_index)

    def _update_solution_list(self, solutions, best_index):
        """Обновляет список решений в UI"""
        self.solution_list.listbox.delete(0, tk.END)
        formatted_solutions = Formatter.format_solution_list(solutions, self.solution_list.winfo_screenwidth())
        for solution in formatted_solutions:
            self.solution_list.listbox.insert(tk.END, solution)

        # Выделяем лучшее решение
        self.solution_list.listbox.selection_clear(0, tk.END)
        self.solution_list.listbox.selection_set(best_index)
        self.solution_list.listbox.activate(best_index)
        self.solution_list.listbox.see(best_index)

    def _update_ui_after_algorithm(self):
        """Обновляет UI после выполнения алгоритма"""
        clique_size = sum(self.current_clique)
        self.best_clique_label.config(text=f"Max Clique: {clique_size}")
        self.generation_counter += 1
        self.generation_label.config(text=f"Generations: {self.generation_counter}")

    def draw_graph_with_clique(self):
        """Отрисовка графа с выделенной кликой"""
        self._draw_graph(highlight_clique=True)

    def save_graph(self):
        """Сохранение графа в файл"""
        if not self._validate_graph_for_save():
            return
            
        filename = self._get_save_filename()
        if filename:
            self._save_matrix_to_file(filename)

    def load_graph(self):
        """Загрузка графа из файла (заглушка)"""
        filename = self._get_open_filename("Выберите файл для загрузки")
        if filename:
            show_info("Файл выбран", f"Выбран файл: {filename}")

    def load_adjacency_matrix(self):
        """Загрузка матрицы смежности из файла"""
        filename = self._get_open_filename("Выберите файл с матрицей смежности", 
                                         filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if filename:
            self._load_matrix_from_file(filename)

    def _validate_graph_for_save(self):
        """Проверка наличия графа для сохранения"""
        return Validator.validate_graph_for_save(self.adj_matrix)

    def _get_save_filename(self):
        """Получение имени файла для сохранения"""
        return FileManager.get_save_filename()

    def _get_open_filename(self, title, filetypes=[("All files", "*.*")]):
        """Получение имени файла для открытия"""
        return FileManager.get_open_filename(title, filetypes)

    def _save_matrix_to_file(self, filename):
        """Сохранение матрицы в файл"""
        return FileManager.save_matrix_to_file(filename, self.adj_matrix)

    def _load_matrix_from_file(self, filename):
        """Загрузка матрицы из файла"""
        matrix, message = FileManager.load_matrix_from_file(filename)
        if matrix is not None:
            self.update_graph(matrix)
            show_info("Успех", message)
        return matrix is not None

    def show_population(self):
        """Показать популяцию (заглушка)"""
        show_info("Population", "Population list (заглушка)")

    def step_algorithm(self):
        """Пошаговое выполнение алгоритма (заглушка)"""
        show_info("Step", "Step (заглушка)")

    def on_resize(self, event):
        """Обработка изменения размера окна"""
        self._update_main_frame_padding()
        self._update_left_panel_padding()

    def set_default_values(self):
        """Установка значений по умолчанию"""
        set_default_values(self.entries)
        self.parameters_changed = True

    def mark_parameters_changed(self, event):
        """Отметка изменения параметров"""
        self.parameters_changed = True

    def _update_main_frame_padding(self):
        """Обновление отступов основного фрейма"""
        w = self.winfo_width()
        h = self.winfo_height()
        left = max(10, int(w * 0.03))
        right = max(10, int(w * 0.03))
        top = max(10, int(h * 0.06))
        bottom = max(10, int(h * 0.08))
        self.main_frame.pack_configure(padx=(left, right), pady=(top, bottom))

    def _update_left_panel_padding(self):
        """Обновление отступов левой панели"""
        w = self.winfo_width()
        right_pad = max(10, int(w * 0.03))
        self.left_panel.pack_configure(padx=(0, right_pad))
