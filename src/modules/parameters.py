class Parameters:
    def __init__(
        self,
        population_size: int,           # Размер популяции
        max_generations: int,           # Максимальное количество итераций
        stagnation_limit: int,          # Количество итераций в застое
        max_mutation_prob_gene: float,  # Максимальная вероятность мутации 1 гена
        max_mutation_prob_chrom: float, # Максимальная вероятность мутации хромосомы
        fitness_scaling_percent: float, # Масштабирование приспособленности хромосом при селекции родителей (в процентах)
        max_crossover_points: int,      # Максимальное количество точек разреза
        decrease_percent: float,        # Процент уменьшения вероятности мутации и точек разреза
        decrease_step: int,             # Шаг (количество поколений) уменьшения точек разреза, вероятности мутации гена и хромосомы
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

    @classmethod
    def from_graph(n: int) -> 'Parameters':
        """
        Вычисляет и возвращает параметры по умолчанию для данного графа
        """
        # population_size – n/10, но не менее 5 и не более 30
        pop = max(5, min(30, n // 10))
        # max_generations – 3*n, но не менее 150 и не более 500
        mg = max(150, min(500, 3 * n))
        # stagnation_limit – mg/10, но не менее 10 и не более 50
        st = max(10, min(50, mg // 10))
        # max_mutation_prob_gene – 0.1
        mpg = 0.1
        # max_mutation_prob_chrom – 0.4 если pop<8, иначе 0.3
        mpc = 0.4 if pop < 8 else 0.3
        # fitness_scaling_percent – 50
        fsp = 50.0
        # max_crossover_points – n/10, но не менее 3
        mcp = max(3, n // 10)
        # decrease_percent – 20
        dp = 20.0
        # decrease_step – 20
        ds = 20

        return Parameters(
            population_size=pop,
            max_generations=mg,
            stagnation_limit=st,
            max_mutation_prob_gene=mpg,
            max_mutation_prob_chrom=mpc,
            fitness_scaling_percent=fsp,
            max_crossover_points=mcp,
            decrease_percent=dp,
            decrease_step=ds
        )

    def validate_parameters(data: dict, n: int) -> None:
        """
        Проверяет словарь параметров на наличие всех требуемых ключей, правильные типы и корректность значений
        """
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
                if key in ('population_size', 'max_generations'):
                    if not (value > 0):
                        raise ValueError(f"Parameter '{key}': must be > 0, got {value}")
                elif key in ('stagnation_limit', 'decrease_step'):
                    mg = data['max_generations']
                    if not (0 < value < mg):
                        raise ValueError(f"Parameter '{key}': must be between 0 and {mg} (max_generations), got {value}")
                elif key in 'fitness_scaling_percent':
                    if not (value > 0.0):
                        raise ValueError(f"Parameter '{key}': must be > 0.0, got {value}")
                elif key in 'max_crossover_points':
                    if not (0 < value < n):
                        raise ValueError(f"Parameter '{key}': must be between 0 and {n} (number of vertices), got {value}")
                elif key in 'decrease_percent':
                    if not (0.0 <= value < 100.0):
                        raise ValueError(f"Parameter '{key}': must be between 0.0 and 100.0, got {value}")
