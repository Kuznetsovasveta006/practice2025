import json

class Parameters:
    def __init__(
        self,
        population_size: int = 0,           # Размер популяции
        max_generations: int = 0,           # Максимальное количество итераций
        stagnation_limit: int = 0,          # Количество итераций в застое
        max_mutation_prob_gene: float = 0,  # Максимальная вероятность мутации 1 гена
        max_mutation_prob_chrom: float = 0, # Максимальная вероятность мутации хромосомы
        fitness_scaling_percent: float = 0, # Масштабирование приспособленности хромосом при селекции родителей (в процентах)
        max_crossover_points: int = 0,      # Максимальное количество точек разреза
        decrease_percent: float = 0,        # Процент уменьшения вероятности мутации и точек разреза
        decrease_step: int = 0,             # Шаг (количество поколений) уменьшения точек разреза, вероятности мутации гена и хромосомы
    ):
        self.population_size = population_size
        self.max_generations = max_generations
        self.stagnation_limit = stagnation_limit
        self.max_mutation_prob_gene = max_mutation_prob_gene
        self.max_mutation_prob_chrom = max_mutation_prob_chrom
        self.fitness_scaling_percent = fitness_scaling_percent
        self.max_crossover_points = max_crossover_points
        self.decrease_percent = decrease_percent
        self.decrease_step = decrease_step


    @staticmethod
    def load_parameters_from_json(file_path: str) -> 'Parameters':
        """
        Загружает параметры генетического алгоритма из JSON-файла.
            FileNotFoundError: Если файл не существует
            ValueError: Если неверные значения параметров или отсутствуют ключи
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Parameters file not found: {file_path}")

        # Список обязательных параметров и их типов
        required_params: dict[str, type] = {
            'population_size': int,
            'max_generations': int,
            'stagnation_limit': int,
            'max_mutation_prob_gene': float,
            'max_mutation_prob_chrom': float,
            'fitness_scaling_percent': float,
            'max_crossover_points': int,
            'decrease_percent': float,
            'decrease_step': int
        }

        # Проверка наличия всех ключей
        missing_keys = [key for key in required_params if key not in data]
        if missing_keys:
            raise ValueError(f"Missing required parameters: {', '.join(missing_keys)}")

        # Проверка типов и значений
        for key, expected_type in required_params.items():
            value = data[key]

            # Проверка типа
            if not isinstance(value, expected_type):
                raise ValueError(f"Wrong type. Parameter '{key}': must be {expected_type.__name__}")

            # Проверка на корректность значений параметров
            if expected_type in (int, float):
                if key == 'decrease_percent' or key == 'fitness_scaling_percent':
                    if not (0.0 <= value <= 100.0):
                        raise ValueError(f"Parameter '{key}': must be between 0.0 and 100.0, got {value}")
                elif key == 'max_mutation_prob_gene' or key == 'max_mutation_prob_chrom':
                    if not (0.0 <= value <= 1.0):
                        raise ValueError(f"Parameter '{key}': must be between 0.0 and 1.0, got {value}")
                elif value < 0:
                    raise ValueError(f"Parameter '{key}': must be >= 0, got {value}")

        return Parameters(
            population_size=data['population_size'],
            max_generations=data['max_generations'],
            stagnation_limit=data['stagnation_limit'],
            max_mutation_prob_gene=data['max_mutation_prob_gene'],
            max_mutation_prob_chrom=data['max_mutation_prob_chrom'],
            fitness_scaling_percent=data['fitness_scaling_percent'],
            max_crossover_points=data['max_crossover_points'],
            decrease_percent=data['decrease_percent'],
            decrease_step=data['decrease_step']
        )
