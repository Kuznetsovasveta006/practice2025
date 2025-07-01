from src.modules.individual import Individual

class Population:
    def __init__(self, individuals: list[Individual]):
        self.individuals = individuals      # Список особей
        self.best: Individual = None        # Лучшая особь в популяции
        self.avg_fitness: float = 0.0       # Средняя приспособленность
        self.update_stats()                 # Инициализация параметров

    def get_len(self):
        """Подсчет количества особоей в популяции"""
        return len(self.individuals)

    def update_stats(self):
        """Пересчитывает статистики популяции"""
        if not self.individuals:
            self.best = None
            self.avg_fitness = 0.0
            return

        # Обновляем и получаем значения приспособленности для всех особей
        fitnesses = [ind.evaluate() for ind in self.individuals]
        self.avg_fitness = sum(fitnesses) / len(fitnesses)
        self.best = max(self.individuals, key=lambda ind: ind.fitness)


    def select_best(self, n: int) -> list[Individual]:
        """Возвращает n лучших особей"""
        sorted_inds = sorted(self.individuals, key=lambda ind: ind.fitness, reverse=True)
        return sorted_inds[:n]


    def get_fitnesses(self) -> list[float]:
        """Возвращает список приспособленностей всех особей"""
        return [ind.fitness for ind in self.individuals]


    def add_individuals(self, new_individuals: list[Individual]):
        """Добавляет новых особей в популяцию"""
        self.individuals.extend(new_individuals)
        self.update_stats()
