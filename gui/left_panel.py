from utils import *
from parameter_config import ParameterConfig


class LeftPanel(tk.Frame):
    def __init__(self, master, open_matrix_callback):
        super().__init__(master)
        self.pack(side=tk.LEFT, fill=tk.Y)
        self.entries = {}
        self.parameters_changed = False

        self._create_parameter_fields()
        self._create_parameter_buttons(open_matrix_callback)

    def _create_parameter_fields(self):
        for label_text, key in ParameterConfig.FIELDS:
            label = tk.Label(self, text=label_text)
            label.pack(anchor="w", padx=5, pady=(5, 0))

            entry = tk.Entry(self)
            entry.pack(fill=tk.X, padx=5, pady=(0, 5))
            entry.insert(0, ParameterConfig.get_default(key))
            entry.bind("<KeyRelease>", self.mark_parameters_changed)

            self.entries[key] = entry

    def _create_parameter_buttons(self, open_matrix_callback):
        buttons_frame = tk.Frame(self)
        buttons_frame.pack(side=tk.BOTTOM, fill=tk.X)

        default_btn = tk.Button(buttons_frame, text="Set default",
                                command=self.set_default_values)
        default_btn.pack(fill=tk.X, padx=5, pady=(0, 2))

        matrix_btn = tk.Button(buttons_frame, text="Enter matrix",
                               command=open_matrix_callback)
        matrix_btn.pack(fill=tk.X, padx=5)

    def validate_and_get_parameters(self):
        params, error = Validator.validate_parameters(self.entries)
        if error:
            UIManager.show_error("Ошибка", error)
            return None
        return params

    def set_default_values(self):
        for key, entry in self.entries.items():
            default_value = ParameterConfig.get_default(key)
            entry.delete(0, tk.END)
            entry.insert(0, default_value)
        self.parameters_changed = True

    def mark_parameters_changed(self, event=None):
        self.parameters_changed = True

    def reset_parameters_changed_flag(self):
        self.parameters_changed = False

    def has_parameters_changed(self):
        return self.parameters_changed