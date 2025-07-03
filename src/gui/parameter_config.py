class ParameterConfig:
    DEFAULTS = {
        "population_size": "50",
        "max_generations": "100",
        "stagnation_limit": "10",
        "max_mutation_prob_gene": "0.05",
        "max_mutation_prob_chrom": "0.1",
        "fitness_scaling_percent": "80",
        "max_crossover_points": "3",
        "decrease_percent": "10",
        "decrease_step": "10",
    }

    FIELDS = [
        ("Population size", "population_size"),
        ("Max generations amount", "max_generations"),
        ("Stagnation_limit", "stagnation_limit"),
        ("Mutation rate", "max_mutation_prob_gene"),
        ("Gene mutation", "max_mutation_prob_chrom"),
        ("Fitness scale", "fitness_scaling_percent"),
        ("Max cut points", "max_crossover_points"),
        ("Reduce prob./cuts by", "decrease_percent"),
        ("Reduction step", "decrease_step"),
    ]

    # Добавляем поле для хранения размера графа
    graph_size = 0

    @classmethod
    def update_defaults_based_on_graph_size(cls, graph_size):
        """Обновляет значения по умолчанию на основе размера графа"""
        cls.graph_size = graph_size

        # Вычисляем новые значения
        population_size = max(5, min(30, graph_size // 10))
        max_generations = max(150, min(500, graph_size * 3))
        stagnation_limit = max(20, min(50, max_generations // 10))
        max_mutation_prob_gene = 0.1
        max_mutation_prob_chrom = 0.4 if population_size < 8 else 0.3
        fitness_scaling_percent = 40
        max_crossover_points = max(3, min(graph_size, graph_size // 5))
        decrease_percent = 20
        decrease_step = 20

        # Обновляем словарь DEFAULTS
        cls.DEFAULTS = {
            "population_size": str(population_size),
            "max_generations": str(max_generations),
            "stagnation_limit": str(stagnation_limit),
            "max_mutation_prob_gene": str(max_mutation_prob_chrom),
            "max_mutation_prob_chrom": str(max_mutation_prob_gene),
            "fitness_scaling_percent": str(fitness_scaling_percent),
            "max_crossover_points": str(max_crossover_points),
            "decrease_percent": str(decrease_percent),
            "decrease_step": str(decrease_step),
        }

    @classmethod
    def get_default(cls, key):
        return cls.DEFAULTS.get(key, "")

    @classmethod
    def get_all_defaults(cls):
        return cls.DEFAULTS.copy()