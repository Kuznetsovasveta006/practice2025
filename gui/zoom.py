class ZoomableWidget:
    """Базовый класс для виджетов с функциональностью зума"""

    def __init__(self, canvas, ax, zoom_type="fitness"):
        self.canvas = canvas
        self.ax = ax
        self.zoom_type = zoom_type
        self._zoom = 1.0
        self._original_xlim = None
        self._original_ylim = None

        # Привязываем события зума
        self.canvas.get_tk_widget().bind('<MouseWheel>', self._on_zoom)
        self.canvas.get_tk_widget().bind('<Button-4>', lambda e: self._on_zoom_linux(e, 1))
        self.canvas.get_tk_widget().bind('<Button-5>', lambda e: self._on_zoom_linux(e, -1))

    def _zoom_to_cursor(self, event, scale_factor):
        """Масштабирование с привязкой к позиции курсора"""
        # Получаем координаты курсора в системе координат данных
        if self.zoom_type == "fitness":
            y_widget = event.widget.winfo_height()
            y_inverted = y_widget - event.y
            x, y = event.x, y_inverted
        else:
            x, y = event.x, event.widget.winfo_height() - event.y

        inv = self.ax.transData.inverted()
        xdata, ydata = inv.transform((x, y))

        # Вычисляем новые границы
        xlim, ylim = self.ax.get_xlim(), self.ax.get_ylim()
        new_width = (xlim[1] - xlim[0]) * scale_factor
        new_height = (ylim[1] - ylim[0]) * scale_factor

        # Вычисляем относительное положение курсора
        relx = (xdata - xlim[0]) / (xlim[1] - xlim[0])
        rely = (ydata - ylim[0]) / (ylim[1] - ylim[0])

        # Устанавливаем новые границы с проверкой для fitness
        new_x0 = max(xdata - relx * new_width, 0) if self.zoom_type == "fitness" else xdata - relx * new_width
        new_x1 = new_x0 + new_width
        new_y0 = max(ydata - rely * new_height, 0) if self.zoom_type == "fitness" else ydata - rely * new_height
        new_y1 = new_y0 + new_height

        self.ax.set_xlim([new_x0, new_x1])
        self.ax.set_ylim([new_y0, new_y1])
        self.canvas.draw()

    def _on_zoom(self, event):
        """Обработка зума колесом мыши"""
        base_scale = 1.2
        if event.delta > 0:
            scale_factor = 1 / base_scale
        else:
            scale_factor = base_scale
        self._zoom *= scale_factor
        self._zoom_to_cursor(event, scale_factor)

    def _on_zoom_linux(self, event, direction):
        """Обработка зума на Linux"""
        base_scale = 1.2
        if direction > 0:
            scale_factor = 1 / base_scale
        else:
            scale_factor = base_scale
        self._zoom *= scale_factor
        self._zoom_to_cursor(event, scale_factor)

    def reset_zoom(self):
        """Сбросить приближение/отдаление"""
        if self._original_xlim and self._original_ylim:
            self.ax.set_xlim(self._original_xlim)
            self.ax.set_ylim(self._original_ylim)
            self._zoom = 1.0
            self.canvas.draw()

    def save_original_limits(self):
        """Сохранить оригинальные пределы для reset"""
        self._original_xlim = self.ax.get_xlim()
        self._original_ylim = self.ax.get_ylim()