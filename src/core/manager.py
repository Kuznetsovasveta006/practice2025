import random
from modules.graph import Graph
from modules.parameters import Parameters
from modules.individual import Individual
from modules.population import Population
from modules.history import History
from core.genetic import GeneticAlgorithm
from gui.utils import RandomGenerator
import matplotlib.pyplot as plt
from typing import List, Tuple, Optional


class AlgorithmManager:
    def __init__(self):
        """Инициализация менеджера алгоритма без параметров"""
        self.graph: Optional[Graph] = None
        self.params: Optional[Parameters] = None
        self.algorithm: Optional[GeneticAlgorithm] = None
        self.history: Optional[History] = None
        self.is_initialized = False
        self.is_completed = False
        

    def load_graph_from_matrix(self, file_path: str) -> None:
        """
        Загружает граф из JSON-файла с матрицей смежности
        Вызывается при нажатии кнопки "Загрузить граф"
        """
        try:
            self.graph = Graph.load_from_matrix_file(file_path)
        except Exception as e:
            print(f"Graph loading error: {e}")
            raise


    def generate_random_graph(self, n: int) -> None:
        """
        Генерирует случайный неориентированный граф с n вершинами и вероятностью ребра p
        Вызывается при нажатии кнопки "Сгенерировать случайный граф"
        """
        try:
            matrix = RandomGenerator.generate_random_matrix(n)
            self.graph = Graph.from_adj_matrix(matrix)
        except Exception as e:
            print(f"Graph loading error: {e}")
            raise


    def save_graph_as_matrix(self, file_path: str) -> None:
        """
        Сохраняет текущий граф в JSON-файл как матрицу смежности
        Кнопка "Сохранить граф"
        """
        if not self.graph:
            raise RuntimeError("Graph not loaded")
        self.graph.save_to_matrix_file(file_path)


    def set_graph(self, graph: Graph) -> None:
        """Установка графа для алгоритма"""
        self.graph = graph
        self._check_initialization()
        

    def set_parameters(self, params: Parameters) -> None:
        """Установка параметров алгоритма"""
        self.params = params
        self._check_initialization()


    def load_and_validate_parameters(self, data: dict) -> None:
        """
        Проверяет параметры на корректность
        Использует graph.n для проверки параметров
        Кнопка "Загрузить параметры"
        """
        if not self.graph:
            raise RuntimeError("First, download or generate graph")

        self.params = Parameters.from_graph(self.graph.n)
        # Общая валидация
        Parameters.validate_parameters(data, self.graph.n)

        # Создание объекта Parameters
        self.params = Parameters(
            population_size=data['population_size'],
            max_generations=data['max_generations'],
            stagnation_limit=data['stagnation_limit'],
            max_mutation_prob_gene=float(data['max_mutation_prob_gene']),
            max_mutation_prob_chrom=float(data['max_mutation_prob_chrom']),
            fitness_scaling_percent=float(data['fitness_scaling_percent']),
            max_crossover_points=data['max_crossover_points'],
            decrease_percent=float(data['decrease_percent']),
            decrease_step=data['decrease_step'],
        )
        self.algorithm = GeneticAlgorithm(self.graph, self.params)


    def _check_initialization(self) -> None:
        """Проверяет, можно ли инициализировать алгоритм"""
        if self.graph is not None and self.params is not None:
            self.initialize_algorithm()


    def initialize_algorithm(self) -> None:
        """Инициализирует алгоритм с текущими графом и параметрами"""
        if self.graph is None:
            raise RuntimeError("To execute algorithm, a graph must be entered")
        if self.params is None:
            raise RuntimeError("To execute algorithm, the parameters must be set")
        
        self.algorithm = GeneticAlgorithm(self.graph, self.params)
        self.history = History()
        self.is_initialized = True
        self.is_completed = False
        
        # Запись начального состояния
        self.history.record(self.algorithm.population)


    def _check_ready(self) -> None:
        """Проверяет, готов ли алгоритм к выполнению"""
        if not self.is_initialized:
            self._check_initialization()
        if self.is_completed:
            raise RuntimeError("Algorithm has already finished")


    def step(self) -> Tuple[List[int], List[List[int]]]:
        """Выполняет одну итерацию алгоритма"""
        self._check_ready()
        
        # Выполняем итерацию
        self.algorithm.next_generation()
        self.history.record(self.algorithm.population)
        
        # Проверяем завершение
        if self.algorithm.should_stop():
            self.is_completed = True
        
        return self._get_current_state()


    def step_n(self, n: int = 5) -> Tuple[List[int], List[List[int]]]:
        """Выполняет N итераций алгоритма"""
        self._check_ready()
        
        for _ in range(n):
            self.algorithm.next_generation()
            self.history.record(self.algorithm.population)
            
            if self.algorithm.should_stop():
                self.is_completed = True
                break

        return self._get_current_state()


    def run_until_completion(self) -> Tuple[List[int], List[List[int]]]:
        """Выполняет алгоритм до завершения"""
        self._check_ready()
        
        while not self.algorithm.should_stop():
            self.algorithm.next_generation()
            self.history.record(self.algorithm.population)
        
        self.is_completed = True
        return self._get_current_state()


    def _get_current_state(self) -> Tuple[List[int], List[List[int]]]:
        """Возвращает текущее состояние алгоритма"""
        # Получаем лучшее решение
        best_solution = self.algorithm.get_best_solution()
        
        # Получаем текущую популяцию в исходной нумерации
        population = self.algorithm.get_population_chromosomes()
        
        return best_solution, population


    def plot_history(self) -> plt.Figure:
        """
        Строит график эволюции на основе истории.
        Предполагается, что History имеет метод plot(),
        возвращающий объект matplotlib.figure.Figure.
        """
        if self.history is None:
            raise RuntimeError("History is not initialized")
        try:
            fig = self.history.plot_fitness()
        except Exception as e:
            print(f"Error plotting history: {e}")
            raise
        return fig

    def reset_algorithm(self) -> None:
        """
        Сбрасывает алгоритм до начального состояния
        Сохраняет текущие граф и параметры
        """
        if self.graph is None or self.params is None:
            raise RuntimeError("Cannot reset algorithm: graph or parameters not set")
            
        # Пересоздаем алгоритм с текущими параметрами
        self.algorithm = GeneticAlgorithm(self.graph, self.params)
        self.history = History()
        self.is_completed = False
        
        # Запись начального состояния
        self.history.record(self.algorithm.population)   
