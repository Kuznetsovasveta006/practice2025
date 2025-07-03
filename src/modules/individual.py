class Individual:
    def __init__(self, chromosome: list[int]):
        self.chromosome = chromosome    # Бинарный вектор, задающий хромосому
        self.fitness: float = 0         # Размер клики


    def evaluate(self):
        """Вычисление приспособленности как размера клики,
        считая, что заданная хромосома всегда задает клику"""
        self.fitness = sum(int(i) for i in self.chromosome)
        return self.fitness