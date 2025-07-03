from right_widgets import *
from matrix_window import *
from left_panel import LeftPanel
from graph_visualizer import GraphVisualizer
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
        self._create_main_container()
        self._create_left_panel()
        self._create_graph_area()
        self._create_right_panel()
        self._load_icons()
        self._create_control_panel()

    def _create_main_container(self):
        self.main_frame = tk.Frame(self)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

    def _create_left_panel(self):
        self.entries = {}
        self.left_panel = LeftPanel(self.main_frame, self.open_matrix_window)

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
        self.graph_visualizer = GraphVisualizer(parent, self.reset_graph_zoom)

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
        self.end_img = tk.PhotoImage(file="./icons/end.png")
        self.reset_img = tk.PhotoImage(file="./icons/reset.png")

    def _create_control_panel(self):
        """Создает панель управления с кнопками операций и информационными метками"""
        # Создаем основной фрейм для панели управления
        control_frame = UIManager.create_frame(self.graph_frame, bg=Colors.GRAPH_BG)
        control_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=5)

        # Левая часть: кнопки управления алгоритмом
        play_btn = UIManager.create_button(control_frame,
                                           image=self.play_img,
                                           command=self.run_algorithm,
                                           **Styles.CONTROL_BTN_STYLE)
        play_btn.pack(side=tk.LEFT, padx=5)

        step_btn = UIManager.create_button(control_frame,
                                           image=self.step_img,
                                           command=self.step_algorithm,
                                           **Styles.CONTROL_BTN_STYLE)
        step_btn.pack(side=tk.LEFT, padx=5)

        end_btn = UIManager.create_button(control_frame,
                                           image=self.end_img,
                                           command=self.step_algorithm,
                                           **Styles.CONTROL_BTN_STYLE)
        end_btn.pack(side=tk.LEFT, padx=5)
        reset_btn = UIManager.create_button(control_frame,
                                            image=self.reset_img,
                                          command=self.step_algorithm,
                                          **Styles.CONTROL_BTN_STYLE)
        reset_btn.pack(side=tk.LEFT, padx=5)

        # Центральный разделитель
        UIManager.create_label(control_frame, bg=Colors.GRAPH_BG).pack(side=tk.LEFT, expand=True)

        # Центральная часть: информационные метки
        info_frame = UIManager.create_frame(control_frame, bg=Colors.GRAPH_BG)
        info_frame.pack(side=tk.LEFT)

        self.generation_label = UIManager.create_label(info_frame,
                                                       text="Generations: 0",
                                                       width=18,
                                                       anchor="center",
                                                       bg=Colors.GRAPH_BG)
        self.generation_label.pack(side=tk.TOP)

        self.best_clique_label = UIManager.create_label(info_frame,
                                                        text="Max Clique: -",
                                                        width=18,
                                                        anchor="center",
                                                        bg=Colors.GRAPH_BG)
        self.best_clique_label.pack(side=tk.TOP)

        # Правый разделитель
        UIManager.create_label(control_frame, bg=Colors.GRAPH_BG).pack(side=tk.LEFT, expand=True)

        # Правая часть: кнопки сохранения/загрузки
        right_btns = UIManager.create_frame(control_frame, bg=Colors.GRAPH_BG)
        right_btns.pack(side=tk.RIGHT)

        load_btn = UIManager.create_button(right_btns,
                                           text="📎",
                                           image=self.attach_img,
                                           command=self.load_adjacency_matrix,
                                           **Styles.CONTROL_BTN_STYLE)
        load_btn.pack(side=tk.LEFT, padx=5)

        save_btn = UIManager.create_button(right_btns,
                                           image=self.save_img,
                                           command=self.save_graph,
                                           **Styles.CONTROL_BTN_STYLE)
        save_btn.pack(side=tk.LEFT, padx=5)


        return control_frame

    def open_matrix_window(self):
        MatrixWindow(self)

    def on_resize(self, event):
        """Обработка изменения размера окна"""
        self._update_main_frame_padding()
        self._update_left_panel_padding()

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

    def set_adj_matrix(self, adj_matrix):
        self.adj_matrix = adj_matrix

    def get_adj_matrix(self):
        print(self.ndarray_to_list(self.adj_matrix))

    def ndarray_to_list(self, matrix_ndarray):
        """Преобразует np.ndarray в двумерный список целых чисел."""
        return matrix_ndarray.tolist()

    def update_graph(self, adj_matrix):
        self.get_adj_matrix()
        self.graph = nx.from_numpy_array(adj_matrix)
        self.graph_layout = nx.spring_layout(self.graph, seed=42)
        self.graph_visualizer.update_graph(self.graph, self.graph_layout)
        self.graph_visualizer.save_limits()
        self._reset_algorithm_state()

    def draw_graph_with_clique(self):
        if self.graph and self.graph_layout and self.current_clique:
            self.graph_visualizer.update_graph(self.graph, self.graph_layout, self.current_clique)

    def _reset_algorithm_state(self):
        """Сброс состояния алгоритма"""
        self.graph_visualizer.save_limits()
        self.best_clique_label.config(text="Max Clique: -")
        self.solution_list.listbox.delete(0, tk.END)
        self.current_clique = None
        self.generation_counter = 0
        self.generation_label.config(text="Generations: 0")

    def _update_ui_after_algorithm(self):
        """Обновляет UI после выполнения алгоритма"""
        clique_size = sum(self.current_clique)
        self.best_clique_label.config(text=f"Max Clique: {clique_size}")
        self.generation_counter += 1
        self.generation_label.config(text=f"Generations: {self.generation_counter}")

    def _reset_generation_counter(self):
        """Сбрасывает счетчик поколений"""
        self.generation_counter = 0
        self.generation_label.config(text="Generations: 0")

    def reset_graph_zoom(self):
        self.graph_visualizer.reset_zoom()

    def run_algorithm(self):
        """Основной метод запуска алгоритма"""
        if not self._validate_graph_exists():
            return

        if self.left_panel.has_parameters_changed():
            self._reset_generation_counter()
            self.left_panel.reset_parameters_changed_flag()

        params = self.left_panel.validate_and_get_parameters()
        if params is None:
            return

        self.fitness_widget.update_fitness_plot(params)
        population = [[0,1], [0,2]]
        best_solution = self.solution_list.get_and_process_solutions(population)

        self.current_clique = best_solution
        self.draw_graph_with_clique()
        self._update_ui_after_algorithm()

    def step_algorithm(self):
        """Пошаговое выполнение алгоритма (заглушка)"""
        UIManager.show_info("Step", "Step (заглушка)")

    def _validate_graph_exists(self):
        """Проверяет, создан ли граф"""
        return Validator.validate_graph_exists(self.graph)

    def _get_open_filename(self, title, filetypes=[("All files", "*.*")]):
        """Получение имени файла для открытия"""
        return FileManager.get_open_filename(title, filetypes)

    def _get_save_filename(self):
        """Получение имени файла для сохранения"""
        return FileManager.get_save_filename()

    def _validate_graph_for_save(self):
        """Проверка наличия графа для сохранения"""
        return Validator.validate_graph_for_save(self.adj_matrix)

    def _load_matrix_from_file(self, filename):
        """Загрузка матрицы из файла"""
        matrix, message = FileManager.load_matrix_from_file(filename)
        if matrix is not None:
            self.update_graph(matrix)
            UIManager.show_info("Успех", message)
        return matrix is not None

    def _save_matrix_to_file(self, filename):
        """Сохранение матрицы в файл"""
        return FileManager.save_matrix_to_file(filename, self.adj_matrix)

    def load_adjacency_matrix(self):
        """Загрузка матрицы смежности из файла"""
        filename = self._get_open_filename("Выберите файл с матрицей смежности",
                                           filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if filename:
            self._load_matrix_from_file(filename)

    def save_graph(self):
        """Сохранение графа в файл"""
        if not self._validate_graph_for_save():
            return

        filename = self._get_save_filename()
        if filename:
            self._save_matrix_to_file(filename)