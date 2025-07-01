from population import Population
import matplotlib.pyplot as plt
import json

class History:
    def __init__(self):
        self.generations: list[int] = []            # Список номеров поколений
        self.best_fitness: list[float] = []         # Лучшие приспособленности на каждом поколении
        self.avg_fitness: list[float] = []          # Средние приспособленности на каждом поколении
        self.best_solutions: list[list[int]] = []   # Лучшие решения на каждом поколении (хромосомы)


    def record(self, generation: int, population: Population):
        """Пересчитывает параметры популяции и сохраняет их в историю"""
        population.update_stats()
        self.generations.append(generation)
        self.best_fitness.append(population.best.fitness)
        self.avg_fitness.append(population.avg_fitness)
        self.best_solutions.append(population.best.chromosome.copy())


    def plot_fitness(self):
        """Строит график динамики лучшей и средней приспособленности по поколениям."""
        plt.figure()
        plt.plot(self.generations, self.best_fitness, label='Best Fitness')
        plt.plot(self.generations, self.avg_fitness, label='Average Fitness')
        plt.xlabel('Generation')
        plt.ylabel('Fitness')
        plt.legend()
        plt.grid(True)
        plt.show()


    def save_to_json(self, path: str):
        """ Сохраняет историю работы алгоритма в результирующий json-файл"""
        data = {
            'generations': self.generations,
            'best_fitness': self.best_fitness,
            'avg_fitness': self.avg_fitness,
            'best_solutions': self.best_solutions
        }
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
