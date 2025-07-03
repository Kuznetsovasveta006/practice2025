class ParameterConfig:
    DEFAULTS = {
        "population_size": "50",
        "max_generations": "100",
        "mutation_rate": "0.05",
        "gene_mutation": "0.1",
        "fitness_scale": "80",
        "max_cut_points": "3",
        "decr_m_prob_step": "10",
        "reduce_cuts_step": "10",
    }

    FIELDS = [
        ("Population size", "population_size"),
        ("Max generations amount", "max_generations"),
        ("Mutation rate", "mutation_rate"),
        ("Gene mutation", "gene_mutation"),
        ("Fitness scale", "fitness_scale"),
        ("Max cut points", "max_cut_points"),
        ("Reduce prob./cuts by", "decr_m_prob_step"),
        ("Reduction step", "reduce_cuts_step"),
    ]

    @classmethod
    def get_default(cls, key):
        return cls.DEFAULTS.get(key, "")

    @classmethod
    def get_all_defaults(cls):
        return cls.DEFAULTS.copy()