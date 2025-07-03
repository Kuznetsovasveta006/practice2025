import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from gui.zoom import ZoomableWidget
from gui.utils import *

class FitnessPlotWidget(tk.Frame):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self._create_plot()          # Создание графика
        self._create_zoom_widget()   # Инициализация зума
        self._create_reset_button()   # Создание кнопки сброса
        self.draw_empty()            # Инициализация пустого графика

    def _create_plot(self):
        """Создание фигуры и оси для графика"""
        self.fig, self.ax = plt.subplots(figsize=(4, 5))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def _create_zoom_widget(self):
        """Инициализация зума"""
        self.zoom_widget = ZoomableWidget(self.canvas, self.ax, zoom_type="fitness")

    def _create_reset_button(self):
        """Создание кнопки сброса для графика"""
        self.reset_btn = tk.Button(self, text="Reset", command=self.reset_zoom, **Styles.RESET_BTN_STYLE)
        self.reset_btn.place(relx=0.95, rely=0.02, anchor="ne")

    def draw_empty(self):
        self.draw_fitness()

    def draw_fitness(self, generations=[], best=[], avg=[]):
        self.ax.clear()
        self.zoom_widget.ax = self.ax

        if len(generations) > 0:
            self.ax.plot(generations, best, label="Best", color=Colors.BEST_LINE_COLOR)
            self.ax.plot(generations, avg, label="Average", color=Colors.AVG_LINE_COLOR)
        else:
            self.ax.set_xlim(0, 9)
            self.ax.set_ylim(0, 10)

        self.ax.set_xlabel("Generation")
        self.ax.set_ylabel("Fitness")
        self.ax.legend(loc='upper center', bbox_to_anchor=(0.42, 1.15), ncol=2)
        self.ax.grid(True)
        self.fig.subplots_adjust(left=0.15, right=0.94, top=0.90, bottom=0.2)
        self.zoom_widget.save_original_limits()
        self.canvas.draw()

    def update_fitness_plot(self, best_fitness: list[float], avg_fitness: list[float]):
        """Обновляет график фитнеса"""
        best_arr = np.array(best_fitness)
        avg_arr = np.array(avg_fitness)
    
        if best_arr.size > 0:
            generations = np.arange(best_arr.size)
        else:
            generations = np.array([])
    
        self.draw_fitness(generations, best_arr, avg_arr)

    def reset_zoom(self):
        self.zoom_widget.reset_zoom()



class SolutionListWidget(tk.Frame):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self._create_listbox_frame()
        self._create_scrollbars()
        self._create_listbox()

    def _create_listbox_frame(self):
        """Создание фрейма для списка"""
        self.listbox_frame = tk.Frame(self)
        self.listbox_frame.pack(fill=tk.BOTH, expand=True)

    def _create_scrollbars(self):
        """Создание полос прокрутки"""
        self.v_scrollbar = tk.Scrollbar(self.listbox_frame, orient=tk.VERTICAL)
        self.v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.h_scrollbar = tk.Scrollbar(self.listbox_frame, orient=tk.HORIZONTAL)
        self.h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)

    def _create_listbox(self):
        """Создание списка"""
        self.listbox = tk.Listbox(self.listbox_frame,
                                  yscrollcommand=self.v_scrollbar.set,
                                  xscrollcommand=self.h_scrollbar.set)
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.v_scrollbar.config(command=self.listbox.yview)
        self.h_scrollbar.config(command=self.listbox.xview)

    def set_example(self, size=5):
        self.listbox.delete(0, tk.END)
        pad = ' ' * max(2, int(self.winfo_screenwidth() * 0.03 // 8))
        for i in range(1, size + 1):
            s = ''.join(str(random.randint(0, 1)) for _ in range(size))
            self.listbox.insert(tk.END, f"{pad}{i}. {s}{pad}")

    def update_solution_list(self, solutions, best_index):
        """Обновляет список решений в UI"""
        self.listbox.delete(0, tk.END)
        formatted_solutions = Formatter.format_solution_list(solutions, self.winfo_screenwidth())
        for solution in formatted_solutions:
            self.listbox.insert(tk.END, solution)

        self.highlight_best_solution(best_index)

    def highlight_best_solution(self, best_index):
        # Выделяем лучшее решение
        self.listbox.selection_clear(0, tk.END)
        self.listbox.selection_set(best_index)
        self.listbox.activate(best_index)
        self.listbox.see(best_index)

