import random
from modules.graph import Graph
from modules.parameters import Parameters
from modules.individual import Individual
from modules.population import Population
from modules.history import History
from core.genetic import GeneticAlgorithm
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
        

    def set_graph(self, graph: Graph) -> None:
        """Установка графа для алгоритма"""
        self.graph = graph
        self._check_initialization()
        

    def set_parameters(self, params: Parameters) -> None:
        """Установка параметров алгоритма"""
        self.params = params
        self._check_initialization()


    def _check_initialization(self) -> None:
        """Проверяет, можно ли инициализировать алгоритм"""
        if self.graph is not None and self.params is not None:
            self.initialize_algorithm()


    def initialize_algorithm(self) -> None:
        """Инициализирует алгоритм с текущими графом и параметрами"""
        if self.graph is None:
            raise RuntimeError("Для выполнения алгоритма должен быть введен граф")
        if self.params is None:
            raise RuntimeError("Для выполнения алгоритма должны быть установлены параметры")
        
        self.algorithm = GeneticAlgorithm(self.graph, self.params)
        self.history = History()
        self.is_initialized = True
        self.is_completed = False
        
        # Запись начального состояния
        self.history.record(self.algorithm.population)


    def _check_ready(self) -> None:
        """Проверяет, готов ли алгоритм к выполнению"""
        if not self.is_initialized:
            self.initialize_algorithm()
        if self.is_completed:
            raise RuntimeError("Алгоритм уже закончил работу")


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
            self.history.record(
                self.algorithm.generation,
                self.algorithm.population
            )
        
        self.is_completed = True
        return self._get_current_state()

    def _get_current_state(self) -> Tuple[List[int], List[List[int]]]:
        """Возвращает текущее состояние алгоритма"""
        # Получаем лучшее решение
        best_solution = self.algorithm.get_best_solution()
        
        # Получаем текущую популяцию в исходной нумерации
        population = self.algorithm.get_population_chromosomes()
        
        return best_solution, population
    