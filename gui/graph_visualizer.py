import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from zoom import ZoomableWidget
from utils import *

class GraphVisualizer:
    def __init__(self, parent, reset_callback):
        self.parent = parent
        self.reset_callback = reset_callback
        self.graph = None
        self.layout = None
        self.current_clique = None

        self._build_graph_area()

    def _build_graph_area(self):
        self.graph_area = tk.Frame(self.parent, bg=Colors.GRAPH_BG)
        self.graph_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.fig, self.ax = plt.subplots(figsize=(5, 4))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.graph_area)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.zoom_widget = ZoomableWidget(self.canvas, self.ax, zoom_type="graph")

        self.reset_graph_btn = tk.Button(self.graph_area, text="Reset",
                                         command=self.reset_zoom, **Styles.RESET_BTN_STYLE)
        self.reset_graph_btn.place(relx=0.95, rely=0.03, anchor="ne")

    def reset_zoom(self):
        self.zoom_widget.reset_zoom()

    def save_limits(self):
        self.zoom_widget.save_original_limits()

    def update_graph(self, graph, layout, clique=None):
        self.graph = graph
        self.layout = layout
        self.current_clique = clique
        self._draw(highlight_clique=bool(clique))

    def _draw(self, highlight_clique=False):
        if self.graph is None:
            return

        if highlight_clique and self.current_clique:
            node_colors = self._get_clique_node_colors()
            edge_colors = self._get_clique_edge_colors()
        else:
            node_colors = [Colors.NODE_COLOR] * len(self.graph.nodes)
            edge_colors = [Colors.EDGE_COLOR] * len(self.graph.edges)

        self.ax.clear()
        nx.draw(self.graph, ax=self.ax, with_labels=True,
                node_color=node_colors, edge_color=edge_colors, pos=self.layout)

        if highlight_clique and self.current_clique:
            self._draw_clique_labels()

        self.canvas.draw()

    def _get_clique_node_colors(self):
        return [
            Colors.CLIQUE_NODE_COLOR if self.current_clique and self.current_clique[i] else Colors.NODE_COLOR
            for i in range(len(self.graph.nodes))
        ]

    def _get_clique_edge_colors(self):
        clique_set = {i for i, v in enumerate(self.current_clique) if v}
        return [
            Colors.CLIQUE_EDGE_COLOR if u in clique_set and v in clique_set else Colors.EDGE_COLOR
            for u, v in self.graph.edges
        ]

    def _draw_clique_labels(self):
        for i, (node, pos) in enumerate(self.layout.items()):
            if self.current_clique and self.current_clique[node]:
                self.ax.text(pos[0], pos[1], str(node), ha='center', va='center',
                             color='white', fontweight='bold', fontsize=12)