from core.Genetic import GeneticAlgorithm
from modules.parameters import Parameters
from modules.graph import Graph


def print_chromosome(chromosome):
    """Форматирует хромосому для красивого вывода"""
    return ''.join(str(g) for g in chromosome)

def test_genetic_algorithm():
    graph = Graph.load_from_file("graph1.json")
    
    params = Parameters(
        population_size=5,
        max_generations=100,
        stagnation_limit=30,
        max_mutation_prob_gene=0.1,
        decrease_percent=10,
        max_mutation_prob_chrom=0.3,
        fitness_scaling_percent=30,
        max_crossover_points=5,
        decrease_step=10
    )
    
    solver = GeneticAlgorithm(graph, params)
    
    print("Начало работы генетического алгоритма")
    print(f"Размер графа: {graph.n} вершин")
    print(f"Параметры алгоритма:")
    print(f"  Размер популяции: {params.population_size}")
    print(f"  Макс. поколений: {params.max_generations}")
    print(f"  Лимит застоя: {params.stagnation_limit}")
    print(f"  Начальные точки кроссовера: {params.max_crossover_points}")
    print()
    
    print("Начальная популяция:")
    for i, ind in enumerate(solver.population.individuals):
        print(f"  Особа {i+1}: {print_chromosome(ind.chromosome)} (размер: {ind.fitness})")
    print()
    
    while not solver.should_stop():
        solver.next_generation()
        
        best_fitness = solver.best_fitness
        stagnation = solver.stagnation_count
        gen = solver.generation
        cross_points = solver.current_crossover_points
        mut_chrom = solver.current_mutation_prob_chrom
        mut_gene = solver.current_mutation_prob_gene
        
        print(f"Поколение {gen}:")
        print(f"  Лучший размер клики: {best_fitness}")
        print(f"  Застой: {stagnation} / {params.stagnation_limit}")
        print(f"  Параметры: точки={cross_points}, мутация хромосомы={mut_chrom:.3f}, мутация гена={mut_gene:.3f}")
        
        print("  Текущая популяция:")
        for i, ind in enumerate(solver.population.individuals):
            print(f"    Особа {i+1}: {print_chromosome(ind.chromosome)} (размер: {ind.fitness})")
        
        if solver.best_chromosome:
            best_original = solver.graph.transform_to_original(solver.best_chromosome)
            clique_vertices = [i for i, val in enumerate(best_original) if val == 1]
            print(f"  Лучшая клика: вершины {clique_vertices}")
        
        print()
    
    size, original_clique = solver.get_best_solution()
    clique_vertices = [i for i, val in enumerate(original_clique) if val == 1]
    
    print("\nРезультат работы алгоритма:")
    print(f"Найдена клика размера {size}")
    print(f"Вершины в клике: {clique_vertices}")
    print(f"Всего поколений: {solver.generation}")
    
    is_valid = graph.is_clique(solver.best_chromosome)
    print(f"Клика {'валидна' if is_valid else 'НЕВАЛИДНА'}")
    
    print(f"Причина остановки: ", end="")
    if solver.best_fitness >= solver.max_degree_original + 1:
        print("Достигнут теоретический максимум")
    elif solver.stagnation_count >= params.stagnation_limit:
        print("Превышен лимит застоя")
    else:
        print("Достигнуто максимальное число поколений")

if __name__ == "__main__":
    test_genetic_algorithm()