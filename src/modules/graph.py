import random
import json

class Graph:
    def __init__(self, adj_list: list[set[int]]):
        self.adj_list: list[set[int]] = adj_list    # Граф до преобразования (список смежности)
        self.n: int = len(adj_list)                 # Количество вершин в графе
        self.transformed_adj: list[set[int]] = []   # Граф с переназначенными вершинами
        self.old_to_new: list = []                  # Список для преобразования старых индексов в новые
        self.new_to_old: list = []                  # Список для преобразования новых индексов в старые


    @staticmethod
    def from_adj_matrix(matrix: list[list[int]]) -> 'Graph':
        """Строит граф в виде списка смежности из матрицы смежности"""
        n = len(matrix)
        adj_list = [set() for _ in range(n)]
        for i in range(n):
            for j in range(n):
                if matrix[i][j] == 1:
                    adj_list[i].add(j)

        return Graph(adj_list)


    def to_adj_matrix(self) -> list[list[int]]:
        """
        Преобразует текущий граф в матрицу смежности 0–1
        """
        n = self.n
        matrix = [[0 for _ in range(n)] for _ in range(n)]

        # Заполняем единицами
        for i, neighs in enumerate(self.adj_list):
            for j in neighs:
                matrix[i][j] = 1

        return matrix


    @staticmethod
    def load_from_matrix_file(file_path: str) -> 'Graph':
        """
        Загружает граф из JSON-файла, в котором он представлен
        как матрица смежности (список списков 0/1)
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Parameters file not found: {file_path}")

        # Проверка структуры
        if not isinstance(data, list):
            raise ValueError("JSON must contain list of lists 0/1")
        n = len(data)
        for row in data:
            if not isinstance(row, list) or len(row) != n:
                raise ValueError("The matrix must be square and consist of lists length n")
            for val in row:
                if val not in (0, 1):
                    raise ValueError(f"Invalid value in matrix: {val}. Only 0 or 1.")

        # Построение списка смежности
        adjacency = [set() for _ in range(n)]
        for i in range(n):
            for j, val in enumerate(data[i]):
                if val == 1:
                    adjacency[i].add(j)

        # Проверка симметричности
        for u in range(n):
            for v in adjacency[u]:
                # Проверяем наличие обратного ребра
                if u != v and u not in adjacency[v]:
                    raise ValueError(f"Graph is not undirected. Missing reverse edge: {v} -> {u}")

        return Graph(adjacency)


    def save_to_matrix_file(self, file_path: str) -> None:
        """
        Сохраняет граф в JSON-файл как матрицу смежности 0/1
        """
        # Генерация матрицы
        matrix = self.to_adj_matrix()

        # Запись в JSON
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(matrix, f, ensure_ascii=False, indent=4)


    @staticmethod
    def random_graph(n: int, p: float) -> 'Graph':
        """
        Генерирует случайный список смежности размера n
        с вероятностью p для каждого ребра i - j и строит по нему граф
        """
        adj = [set() for _ in range(n)]
        for i in range(n):
            for j in range(i + 1, n):
                if random.random() < p:
                    adj[i].add(j)
                    adj[j].add(i)
        return Graph(adj)


    def transform_by_degree(self):
        """
        Преобразует граф, переупорядочивая вершины по убыванию степени
        Создает списки для отображения старых индексов в новые, новых в старые
        """
        # Сортируем вершины по степени по убыванию
        degs = [len(neighbors) for neighbors in self.adj_list]
        sorted_idxs = sorted(range(self.n), key=lambda i: degs[i], reverse=True)

        # Создаем списки для преобразования индексов
        self.old_to_new = [0] * self.n
        for new_index, old_index in enumerate(sorted_idxs):
            self.old_to_new[old_index] = new_index
        self.new_to_old = sorted_idxs

        # Строим новый граф (с переназначенными вершинами)
        new_adj = [set() for _ in range(self.n)]
        for old_u, neighbors in enumerate(self.adj_list):
            new_u = self.old_to_new[old_u]
            for old_v in neighbors:
                new_v = self.old_to_new[old_v]
                new_adj[new_u].add(new_v)

        self.transformed_adj = new_adj


    def transform_to_original(self, sorted_chromosome: list[int]) -> list[int]:
        """Преобразует хромосому из преобразованной нумерации в исходную нумерацию вершин графа"""
        original_chromosome = [0] * self.n
        for new_index, value in enumerate(sorted_chromosome):
            if value == 1:
                # Преобразование нового индекса в старый
                old_index = self.new_to_old[new_index]
                original_chromosome[old_index] = 1

        return original_chromosome


    def transform_to_sorted(self, original_chromosome: list[int]) -> list[int]:
        """Преобразует хромосому из исходной нумерации в преобразованную"""
        sorted_chromosome = [0] * self.n
        for old_index, value in enumerate(original_chromosome):
            if value == 1:
                # Преобразование старого индекса в новый
                new_index = self.old_to_new[old_index]
                sorted_chromosome[new_index] = 1

        return sorted_chromosome


    def get_subgraph(self, chromosome: list[int]) -> list[set[int]]:
        """Строит подграф на основе хромосомы (для исходного графа)"""
        subgraph = [set() for _ in range(self.n)]
        included = [i for i in range(self.n) if chromosome[i] == 1]

        # Строим список смежности для включенных в хромосому вершин
        for v in included:
            for neighbor in self.adj_list[v]:
                if chromosome[neighbor] == 1:
                    subgraph[v].add(neighbor)

        return subgraph


    def all_neighbors(self, v: int) -> list[int]:
        """Возвращает список соседей вершины v в преобразованном графе"""
        return list(self.transformed_adj[v])


    def has_edge(self, u: int, v: int) -> bool:
        """Проверяет наличие ребра между u и v в преобразованном графе"""
        return v in self.transformed_adj[u]


    def degree_in_subgraph(self, included: list[int]):
        """Вычисляет степени вершин в подграфе (в преобразованном графе)"""
        degs = []
        for v in included:
            deg = 0
            for u in included:
                if u != v and self.has_edge(u, v):
                    deg += 1
            degs.append(deg)

        return degs


    def is_clique(self, chromosome: list[int]) -> bool:
        """Проверяет, задают ли включенные в хромосому вершины клику в преобразованном графе"""
        included = [v for v, flag in enumerate(chromosome) if flag]
        k = len(included)
        if k <= 1:
            return True

        # Вычисляем степени вершин подграфа, заданного хромосомой
        degs = self.degree_in_subgraph(included)

        # Проверяем степень каждой вершины
        for v in range(k):
            if degs[v] != k - 1:
                return False

        return True


    def repair_chromosome(self, chromosome: list[int]) -> list[int]:
        """
        Пока включенные вершины не образуют клику,
        удаляет случайную вершину минимальной степени в подграфе
        Возвращает новую хромосому
        """
        chrom = chromosome.copy()
        while not self.is_clique(chrom):
            # Включенные в рассматриваемый подграф вершины
            included = [v for v, flag in enumerate(chrom) if flag]
            degs = self.degree_in_subgraph(included)

            # Находим вершины с минимальной степенью
            min_deg = min(degs)
            candidate_idxs = [i for i, d in enumerate(degs) if d == min_deg]

            # Случайно выбираем из этих вершин одну и удаляем ее из подграфа
            idx_to_remove = random.choice(candidate_idxs)
            v_to_remove = included[idx_to_remove]
            chrom[v_to_remove] = 0

        return chrom
