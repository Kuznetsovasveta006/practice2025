import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from zoom import ZoomableWidget
from utils import *

class FitnessPlotWidget(tk.Frame):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.fig, self.ax = plt.subplots(figsize=(4, 5))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Инициализируем зум
        self.zoom_widget = ZoomableWidget(self.canvas, self.ax, zoom_type="fitness")

        # Кнопка reset для fitness графика
        self.reset_btn = tk.Button(self, text="Reset", command=self.reset_zoom, **Styles.RESET_BTN_STYLE)
        self.reset_btn.place(relx=0.95, rely=0.02, anchor="ne")

        # Инициализируем пустой график
        self.draw_empty()

    def reset_zoom(self):
        self.zoom_widget.reset_zoom()

    def draw_empty(self):
        self.draw_fitness()

    def draw_fitness(self, generations=[], best=[], avg=[]):
        self.ax.clear()
        self.fig.clear()
        self.ax = self.fig.add_subplot(111)
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


class SolutionListWidget(tk.Frame):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)

        listbox_frame = tk.Frame(self)
        listbox_frame.pack(fill=tk.BOTH, expand=True)

        self.v_scrollbar = tk.Scrollbar(listbox_frame, orient=tk.VERTICAL)
        self.v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.h_scrollbar = tk.Scrollbar(listbox_frame, orient=tk.HORIZONTAL)
        self.h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)

        self.listbox = tk.Listbox(listbox_frame,
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