from population import Population
from individual import Individual
import matplotlib.pyplot as plt
import json

class History:
    def __init__(self):
        self.best_fitness: list[float] = []         # Лучшие приспособленности на каждом поколении
        self.avg_fitness: list[float] = []          # Средние приспособленности на каждом поколении


    def record(self, population: Population):
        """Пересчитывает параметры популяции и сохраняет их в историю"""
        population.update_stats()
        self.best_fitness.append(population.best.fitness)
        self.avg_fitness.append(population.avg_fitness)


    def plot_fitness(self) -> plt.Figure:
        """Строит и возвращает график динамики лучшей и средней приспособленности по поколениям"""
        generations = list(range(len(self.best_fitness)))
        fig, ax = plt.subplots()

        ax.plot(generations, self.best_fitness, label='Best Fitness')
        ax.plot(generations, self.avg_fitness, label='Average Fitness')
        ax.set_xlabel('Generation')
        ax.set_ylabel('Fitness')
        ax.legend()
        ax.grid(True)

        return fig


    def save_to_json(self, path: str):
        """Сохраняет историю работы алгоритма в результирующий json-файл"""
        data = {
            'best_fitness': self.best_fitness,
            'avg_fitness': self.avg_fitness
        }
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
