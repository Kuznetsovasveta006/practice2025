import random
from modules.graph import Graph
from modules.parameters import Parameters
from modules.individual import Individual
from modules.population import Population
from typing import List, Tuple


class GeneticAlgorithm:
    def __init__(self, graph: Graph,  params:Parameters):
        """Инициализация генетического алгоритма для поиска максимальной клики"""
        self.graph = graph
        self.params = params
        
        # Текущие значения параметров
        self.current_mutation_prob_chrom = params.max_mutation_prob_chrom   # Вероятность мутации хромосомы
        self.current_mutation_prob_gene = params.max_mutation_prob_gene     # Вероятность мутации гена
        self.current_crossover_points = params.max_crossover_points         # Количество точек кроссовера
        
        # Состояние алгоритма
        self.generation = 0             # Текущее поколение
        self.stagnation_count = 0       # Счетчик поколений без улучшения
        self.best_fitness = 0           # Лучшая найденная приспособленность
        self.best_chromosome = None     # Лучшая найденная хромосома
        
        # Инициализация графа
        self.n = graph.n                # Количество вершин в графе
        self.max_degree_original = max(len(adj) for adj in graph.adj_list)   # Максимальная степень вершины
        graph.transform_by_degree()     # Преобразование графа по степеням вершин
        
        # Генерация начальной популяции
        self.population = Population(self.generate_initial_population())
        self._update_best_solution()    # Обновление лучшего решения


    def scale_weights(self, weights: List[float]) -> List[float]:
        """
        Масштабирует веса так, чтобы максимальный вес был не более
        чем на scaling_percent больше минимального.
        """
        if not weights:
            return []
            
        w_min = min(weights)
        w_max = max(weights)
        
        # Если все веса равны, возвращаем единицы
        if w_min == w_max:
            return [1.0] * len(weights)
        
        # Вычисляем масштабированные веса
        K = self.params.fitness_scaling_percent / 100.0
        return [1 + K * (w - w_min) / (w_max - w_min) for w in weights]


    def generate_chromosome(self) -> List[int]:
        """Генерирует хромосому, представляющую клику в графе"""
        # Если граф пустой то хромосома тоже пуста
        if self.n == 0:
            return []
        
        degrees = [len(adj) for adj in self.graph.transformed_adj] # Степени вершин в отсортированном графе
        available = list(range(self.n))                            # Список номеров доступных вершин для добавления в клику
        weights = self.scale_weights(degrees)                      # Веса вершин для случайного выбора
        chosen = random.choices(available, weights=weights)[0]     # Случайно выбираем первую вершину для клики
        current_clique = [chosen]                                  # Теперь текущая клика состоит из этой ершины
        candidates = set(self.graph.transformed_adj[chosen])       # Множество кандидатов для добавления в клику
        
        # Расширяем клику, пока есть кандидаты
        while candidates:
            cand_list = list(candidates)                            
            cand_weights = self.scale_weights([degrees[c] for c in cand_list])  # Список весов для случайного выбора среди кандидатов
            next_vertex = random.choices(cand_list, weights=cand_weights)[0]    # Случайно выбираем следующщую вершину
            current_clique.append(next_vertex)                                  # Добавляем ее в клику
            candidates.discard(next_vertex)                                     # Удаляем ее из кандидатов
            candidates = candidates & self.graph.transformed_adj[next_vertex]   # Обновляем возможных кандидатов для добавления в клику
        
        # Заполняем хромосому в соответствие с выбранными для клики вершинами
        chromosome = [0] * self.n
        for v in current_clique:
            chromosome[v] = 1
        return chromosome


    def generate_initial_population(self) -> List[Individual]:
        """Генерирует начальную популяцию особей"""
        return [Individual(self.generate_chromosome()) for _ in range(self.params.population_size)]


    def select_parents(self) -> List[Individual]:
        """Выбирает родителей для скрещивания с использованием метода рулетки"""
        # Масштабируем рулетку
        fitnesses = self.population.get_fitnesses()
        scaled = self.scale_weights(fitnesses)
            
        # Возвращаем список родителей для новой популяции
        return random.choices(self.population.individuals, 
                              weights=scaled, 
                              k=self.params.population_size)


    def crossover(self, parent1: Individual, parent2: Individual) -> Tuple[List[int], List[int]]:
        """Выполняет кроссовер двух родителей с несколькими точками разрыва"""
        breaks = self.current_crossover_points
        chrom1 = parent1.chromosome
        chrom2 = parent2.chromosome
        
        # Если разрывов нет - возвращаем копии родителей
        if self.n <= 1:
            return chrom1[:], chrom2[:]
        
        # Выбираем точки разрыва
        breaks = min(breaks, self.n - 1)
        break_points = sorted(random.sample(range(1, self.n), k=breaks))
        
        # Строим потомков
        child1, child2 = [], []
        current = 0
        
        # Попеременное копирование сегментов от родителей
        for i, point in enumerate(break_points):
            if i % 2 == 0:
                child1.extend(chrom1[current:point])
                child2.extend(chrom2[current:point])
            else:
                child1.extend(chrom2[current:point])
                child2.extend(chrom1[current:point])
            current = point
        
        # Добавляем остаток хромосомы
        if len(break_points) % 2 == 0:
            child1.extend(chrom1[current:])
            child2.extend(chrom2[current:])
        else:
            child1.extend(chrom2[current:])
            child2.extend(chrom1[current:])
            
        return child1, child2


    def mutate_and_repair(self, chromosome: List[int]) -> List[int]:
        """Применяет мутацию и восстанавливает хромосому до валидной клики"""
        if random.random() < self.current_mutation_prob_chrom:
            mutated = [
                # Инвертируем ген с вероятностью current_mutation_prob_gene
                1 - gene if random.random() < self.current_mutation_prob_gene else gene 
                for gene in chromosome
            ]
        else:
            mutated = chromosome    # Без мутации
        
        # Восстанавливаем до клики
        return self.graph.repair_chromosome(mutated)
    

    def _hamming_distance(self, chrom1, chrom2):
        """Вычисляет нормализованное расстояние Хэмминга между двумя хромосомами"""
        matches = sum(g1 == g2 for g1, g2 in zip(chrom1, chrom2))
        return 1.0 - matches / len(chrom1)


    def select_new_population(self, current_pop: List[Individual], offspring: List[Individual]) -> List[Individual]:
        """Формирует новую популяцию, сохраняя разнообразие"""
        combined = offspring + current_pop
        combined.sort(key=lambda ind: ind.fitness, reverse=True)
        
        selected = []                   # Выбранные особи
        remaining = combined.copy()     # Оставшиеся особи
        
        # Всегда добавляем лучшую особь (случайную из лучших, если их несколько)
        if remaining:
            max_fitness = remaining[0].fitness
            best_candidates = [ind for ind in remaining if ind.fitness == max_fitness]
        
            # Случайно выбираем одну из лучших
            best = random.choice(best_candidates)
            remaining.remove(best)
            selected.append(best)
        
        # Добавляем особи, максимально отличающиеся от уже выбранных
        while len(selected) < self.params.population_size and remaining:
            best_candidates = []
            max_min_distance = -1
            
            for ind in remaining:
                # Вычисляем минимальное расстояние до уже выбранных особей
                min_distance = min(
                    self._hamming_distance(ind.chromosome, sel.chromosome)
                    for sel in selected
                ) if selected else 1.0
                
                if min_distance > max_min_distance:
                    max_min_distance = min_distance
                    best_candidates = [ind]
                elif min_distance == max_min_distance:
                    best_candidates.append(ind)
            
            # Добавляем лучшего кандидата
            if best_candidates:
                candidate = random.choice(best_candidates)
                remaining.remove(candidate)
                selected.append(candidate)
            else:
                # Если не нашли подходящего кандидата, добавляем случайно
                selected.append(remaining.pop(0))
        
        return selected


    def _update_best_solution(self):
        """Обновляет лучшее решение, если найдено улучшение"""
        current_best = self.population.best
        if current_best and current_best.fitness > self.best_fitness:
            # Найдено улучшение
            self.best_fitness = current_best.fitness
            self.best_chromosome = current_best.chromosome
            self.stagnation_count = 0
        else:
            # Улучшения нет - увеличиваем счетчик застоя
            self.stagnation_count += 1
            

    def _reduce_parameters(self):
        """Уменьшает параметры алгоритма на заданный процент от начальных значений"""
        # Уменьшаем количество точек разрыва
        reduction_amount = max(1, int(self.params.max_crossover_points * self.params.decrease_percent / 100))
        self.current_crossover_points = max(1, self.current_crossover_points - reduction_amount)
        
        # Уменьшаем вероятность мутации хромосомы
        new_mutation_prob_chrom = self.current_mutation_prob_chrom - self.params.max_mutation_prob_chrom * self.params.decrease_percent / 100.0
        if new_mutation_prob_chrom > 0.0:
            self.current_mutation_prob_chrom = new_mutation_prob_chrom
        
        # Уменьшаем вероятность мутации гена
        new_mutation_prob_gene = self.current_mutation_prob_gene  - self.params.max_mutation_prob_gene * self.params.decrease_percent / 100.0
        if new_mutation_prob_gene > 0.0:
            self.current_mutation_prob_gene = new_mutation_prob_gene
        

    def should_stop(self) -> bool:
        """Проверяет условия остановки алгоритма"""
        return (
            self.generation >= self.params.max_generations or           # Достигнуто максимальное число поколений
            self.stagnation_count >= self.params.stagnation_limit or    # Превышен лимит застоя
            self.best_fitness >= self.max_degree_original + 1           # Найдена максимально возможная клика
        )
    
    
    def next_generation(self):
        """Выполняет одну итерацию генетического алгоритма"""
        # Выбираем родителей
        parents = self.select_parents()
        
        # Генерируем потомков
        offspring = []
        for i in range(0, len(parents), 2):
            if i + 1 < len(parents):
                p1, p2 = parents[i], parents[i + 1]
                # Скрещивание
                child1, child2 = self.crossover(p1, p2)
                # Мутация и восстановление
                repaired1 = self.mutate_and_repair(child1)
                repaired2 = self.mutate_and_repair(child2)
                # Создание новых особей
                offspring.append(Individual(repaired1))
                offspring.append(Individual(repaired2))
        
        # Формируем новую популяцию
        new_individuals = self.select_new_population(
            self.population.individuals, offspring
        )
        self.population = Population(new_individuals)
        self.population.update_stats()  
        
        # Обновляем лучшее решение
        self._update_best_solution()
        
        # Увеличиваем счетчик поколений
        self.generation += 1
        
        # Периодически уменьшаем параметры
        if (self.params.decrease_step > 0 and 
            self.generation % self.params.decrease_step == 0):
            self._reduce_parameters()


    def get_population_chromosomes(self) -> List[List[int]]:
        """Возвращает хромосомы текущей популяции""" 
        return [self.graph.transform_to_original(ind.chromosome) 
                for ind in self.population.individuals]


    def get_best_solution(self) -> Tuple[int, List[int]]:
        """Возвращает лучшее решение в исходной нумерации вершин"""
        if self.best_chromosome is None:
            return []
        return self.graph.transform_to_original(self.best_chromosome)
