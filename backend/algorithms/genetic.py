"""
Algoritmo Genético para búsqueda de rutas en grafos.
Incluye TSP con waypoints predefinidos y pathfinding directo sobre el grafo.
"""
import random
import numpy as np
import math
from backend.algorithms.dijkstra import find_path as dijkstra_find

# ------------------------------------------------------------
# 1. TSP con waypoints predefinidos (versión original mejorada)
# ------------------------------------------------------------
def pairwise_distances(adj, coordinates, nodes_list):
    """Calcula la matriz de distancias (metros) entre todos los pares de la lista."""
    n = len(nodes_list)
    dist_matrix = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            if i == j:
                dist_matrix[i][j] = 0
            else:
                _, _, d = dijkstra_find(adj, coordinates, nodes_list[i], nodes_list[j])
                dist_matrix[i][j] = d * 1000 if d is not None else float('inf')
    return dist_matrix

def total_distance(order, dist_matrix):
    return sum(dist_matrix[order[i]][order[i+1]] for i in range(len(order)-1))

def order_crossover(p1, p2):
    size = len(p1)
    start, end = sorted(random.sample(range(size), 2))
    child = [None] * size
    child[start:end] = p1[start:end]
    ptr = 0
    for gene in p2:
        if gene not in child:
            while child[ptr] is not None:
                ptr += 1
            child[ptr] = gene
    return child

def mutate(order, mutation_rate):
    if random.random() < mutation_rate:
        i, j = random.sample(range(len(order)), 2)
        order[i], order[j] = order[j], order[i]

def genetic_tsp(adj, coordinates, start_node, end_node, waypoint_nodes, config):
    """Optimiza el orden de waypoints predefinidos."""
    if not waypoint_nodes:
        return [], [], 0
    intermedios = waypoint_nodes
    all_points = [start_node] + intermedios + [end_node]
    dist_matrix = pairwise_distances(adj, coordinates, all_points)

    pop_size = config.get('population_size', 100)
    generations = config.get('generations', 200)
    mutation_rate = config.get('mutation_rate', 0.02)
    elite_size = config.get('elite_size', 10)

    n_inter = len(intermedios)
    population = []
    for _ in range(pop_size):
        perm = list(range(1, n_inter+1))
        random.shuffle(perm)
        population.append(perm)

    best_per_generation = []

    for gen in range(generations):
        fitnesses = []
        for ind in population:
            full_order = [0] + ind + [len(all_points)-1]
            fit = 1.0 / (total_distance(full_order, dist_matrix) + 1e-9)
            fitnesses.append(fit)

        best_idx = np.argmax(fitnesses)
        best_dist = total_distance([0] + population[best_idx] + [len(all_points)-1], dist_matrix)
        best_per_generation.append(best_dist)

        sorted_pop = [ind for _, ind in sorted(zip(fitnesses, population), key=lambda x: x[0], reverse=True)]
        new_pop = sorted_pop[:elite_size]
        while len(new_pop) < pop_size:
            p1, p2 = random.choices(sorted_pop[:pop_size//2], k=2)
            child = order_crossover(p1, p2)
            mutate(child, mutation_rate)
            new_pop.append(child)
        population = new_pop

    fitnesses = [1.0/(total_distance([0]+ind+[len(all_points)-1], dist_matrix)+1e-9) for ind in population]
    best_final = population[np.argmax(fitnesses)]
    best_full_order_indices = [0] + best_final + [len(all_points)-1]
    best_distance_m = total_distance(best_full_order_indices, dist_matrix)
    return best_full_order_indices, best_per_generation, best_distance_m


# ------------------------------------------------------------
# 2. NUEVO: Pathfinding directo con AG (sin waypoints predefinidos)
# ------------------------------------------------------------
def initial_valid_path(adj, start, end):
    """
    Genera un camino aleatorio válido desde start hasta end.
    Realiza un paseo aleatorio sesgado por la heurística Haversine,
    pero evitando ciclos. Si no se alcanza el destino en un número
    máximo de pasos, devuelve una ruta ficticia con penalización.
    """
    max_steps = len(adj)  # evitar bucles infinitos
    path = [start]
    current = start
    visited = {start}
    while current != end and len(path) < max_steps:
        neighbors = [v for v, _ in adj.get(current, [])]
        if not neighbors:
            break
        # Filtrar no visitados (a veces permitimos revistar para salir de callejones)
        unvisited = [n for n in neighbors if n not in visited]
        if not unvisited:
            unvisited = neighbors  # si no, forzar revísita
        # Heurística: elegir con probabilidad proporcional a 1/distancia al destino
        # No tenemos coordenadas aquí, así que elegimos al azar
        next_node = random.choice(unvisited)
        path.append(next_node)
        visited.add(next_node)
        current = next_node
    return path if path[-1] == end else None

def path_fitness(path, adj, coordinates):
    """
    Calcula la distancia total de un camino.
    Si un paso no es adyacente, añade una penalización enorme.
    Si el camino no empieza en start o no termina en end, penaliza.
    """
    if len(path) < 2:
        return float('inf')
    dist = 0
    penalty = 1e9  # 1 000 000 km
    for i in range(len(path)-1):
        u, v = path[i], path[i+1]
        # Buscar arista (u,v)
        found = False
        for neighbor, weight in adj.get(u, []):
            if neighbor == v:
                dist += weight
                found = True
                break
        if not found:
            dist += penalty
    return dist

def crossover_common_node(p1, p2):
    """
    Cruce por nodo común: busca un nodo que compartan ambas rutas
    (excluyendo start y end) y cruza allí.
    Si no hay coincidencia, devuelve una copia del padre 1.
    """
    # Buscar nodos comunes
    common = set(p1[1:-1]) & set(p2[1:-1])
    if not common:
        return p1[:]  # sin cruce
    node = random.choice(list(common))
    idx1 = p1.index(node)
    idx2 = p2.index(node)
    child = p1[:idx1] + p2[idx2:]
    # Evitar duplicados simples: si el hijo tiene bucles, se filtrarán en la aptitud
    return child

def mutate_subpath(path, adj, coordinates, mutation_rate):
    """
    Mutación inteligente: elige dos nodos aleatorios de la ruta
    y genera un sub‑camino válido entre ellos usando Dijkstra.
    """
    if random.random() > mutation_rate:
        return path
    if len(path) < 3:
        return path
    i, j = sorted(random.sample(range(len(path)), 2))
    # Si j == i+1, la mutación sería trivial
    if j - i <= 1:
        return path
    _, subpath_nodes, _ = dijkstra_find(adj, coordinates, path[i], path[j])
    if subpath_nodes is None:
        return path  # no se pudo encontrar sub‑ruta
    # Reemplazar segmento
    new_path = path[:i] + subpath_nodes + path[j+1:]
    # Eliminar posibles bucles inmediatos (p.ej., [A,B,B,C]) manteniendo orden
    final_path = [new_path[0]]
    for node in new_path[1:]:
        if node != final_path[-1]:
            final_path.append(node)
    return final_path

def genetic_pathfinding(adj, coordinates, start, end, config):
    """
    AG para encontrar un camino desde start hasta end en el grafo.
    No requiere waypoints intermedios.
    """
    pop_size = config.get('population_size', 300)
    generations = config.get('generations', 1000)
    mutation_rate = config.get('mutation_rate', 0.1)
    elite_size = config.get('elite_size', int(pop_size * 0.05))

    # Generar población inicial de caminos válidos (o con penalización)
    population = []
    attempts = 0
    while len(population) < pop_size and attempts < pop_size * 10:
        p = initial_valid_path(adj, start, end)
        if p:  # aunque no termine en end, se penaliza
            population.append(p)
        attempts += 1
    # Si no pudimos generar suficientes, rellenar con rutas directas Dijkstra
    while len(population) < pop_size:
        # Ruta directa usando Dijkstra como individuo inicial de alta calidad
        dijk_path, _, _ = dijkstra_find(adj, coordinates, start, end)
        if dijk_path:
            population.append(dijk_path)
        else:
            # Ruta dummy: solo start-end
            population.append([start, end])

    best_per_gen = []  # mejor distancia de cada generación

    for gen in range(generations):
        # Evaluar aptitud (menor es mejor → mayor fitness = 1/(dist+1))
        fitness = []
        for ind in population:
            d = path_fitness(ind, adj, coordinates)
            fitness.append(1.0 / (d + 1e-9))
        best_idx = np.argmax(fitness)
        best_path = population[best_idx]
        best_dist = path_fitness(best_path, adj, coordinates)
        best_per_gen.append(best_dist)

        # Elitismo
        sorted_pop = [ind for _, ind in sorted(zip(fitness, population), key=lambda x: x[0], reverse=True)]
        new_pop = sorted_pop[:elite_size]

        while len(new_pop) < pop_size:
            # Selección por torneo
            parent1 = random.choice(sorted_pop[:pop_size//2])
            parent2 = random.choice(sorted_pop[:pop_size//2])
            child = crossover_common_node(parent1, parent2)
            child = mutate_subpath(child, adj, coordinates, mutation_rate)
            new_pop.append(child)

        population = new_pop

    # Mejor individuo final
    fitness = [1.0/(path_fitness(ind, adj, coordinates)+1e-9) for ind in population]
    best = population[np.argmax(fitness)]
    final_dist = path_fitness(best, adj, coordinates)
    # Convertir la lista de nodos a camino final (puede contener pasos no válidos → lo arreglamos)
    # Construimos un camino válido uniendo segmentos con Dijkstra
    final_valid = []
    for i in range(len(best)-1):
        seg, _, _ = dijkstra_find(adj, coordinates, best[i], best[i+1])
        if seg is None:
            # Si no hay ruta entre dos nodos consecutivos, saltamos (raro)
            continue
        if final_valid and seg[0] == final_valid[-1]:
            final_valid.extend(seg[1:])
        else:
            final_valid.extend(seg)
    return final_valid, best_per_gen, final_dist

# ------------------------------------------------------------
# Interfaz común usada por el comparador
# ------------------------------------------------------------
def find_path(G, adj, coordinates, start_node, end_node, waypoints_list, config):
    """
    Si waypoints_list contiene al menos 2 elementos (start y end ya dados),
    se usa el TSP para ordenarlos. En caso contrario, se ejecuta el AG
    de pathfinding directo sobre el grafo.
    """
    # En modo provincias, start_node y end_node son strings.
    # waypoints_list es una lista de dicts {name, lat, lon} o simplemente strings.
    # Extraer solo los nombres
    if waypoints_list and isinstance(waypoints_list[0], dict):
        wp_names = [wp['name'] for wp in waypoints_list if wp['name'] != start_node and wp['name'] != end_node]
    else:
        wp_names = waypoints_list if waypoints_list else []

    # Si hay waypoints intermedios (>=1), usar TSP
    if len(wp_names) >= 1:
        # Modo OSM: se necesitan los nodos OSM, aquí asumimos que G no es None
        if G is not None:
            import osmnx as ox
            waypoint_nodes = [ox.nearest_nodes(G, X=wp['lon'], Y=wp['lat']) for wp in waypoints_list if wp['name'] != start_node]
            intermedios = waypoint_nodes
            best_order_indices, history, best_dist_m = genetic_tsp(adj, coordinates, start_node, end_node, intermedios, config)
            all_points = [start_node] + intermedios + [end_node]
            ordered_nodes = [all_points[i] for i in best_order_indices]
            ordered_dist_km = best_dist_m / 1000
            # Construir ruta concatenada
            full_path = []
            for i in range(len(ordered_nodes)-1):
                seg, _, _ = dijkstra_find(adj, coordinates, ordered_nodes[i], ordered_nodes[i+1])
                if seg is None:
                    return {'error': 'No se pudo construir ruta entre waypoints'}
                if full_path and seg[0] == full_path[-1]:
                    full_path.extend(seg[1:])
                else:
                    full_path.extend(seg)
            ordered_names = [start_node] + wp_names + [end_node]  # simplificado
            return {
                'path': full_path,
                'nodes_visited': len(full_path),
                'distance_km': round(ordered_dist_km, 3),
                'generations_run': config.get('generations', 200),
                'fitness_history': [d/1000 for d in history],
                'waypoints_order': ordered_names
            }
        else:
            # Modo provincias con waypoints (caso poco común)
            intermedios = wp_names
            best_order_indices, history, best_dist_m = genetic_tsp(adj, coordinates, start_node, end_node, intermedios, config)
            all_points = [start_node] + intermedios + [end_node]
            ordered_nodes = [all_points[i] for i in best_order_indices]
            ordered_dist_km = best_dist_m / 1000
            full_path = []
            for i in range(len(ordered_nodes)-1):
                seg, _, _ = dijkstra_find(adj, coordinates, ordered_nodes[i], ordered_nodes[i+1])
                if seg is None:
                    return {'error': 'No se pudo construir ruta entre waypoints'}
                if full_path and seg[0] == full_path[-1]:
                    full_path.extend(seg[1:])
                else:
                    full_path.extend(seg)
            return {
                'path': full_path,
                'nodes_visited': len(full_path),
                'distance_km': round(ordered_dist_km, 3),
                'generations_run': config.get('generations', 200),
                'fitness_history': [d/1000 for d in history],
                'waypoints_order': [start_node] + intermedios + [end_node]
            }
    else:
        # Sin waypoints → pathfinding puro
        final_path, history, final_dist = genetic_pathfinding(adj, coordinates, start_node, end_node, config)
        if not final_path:
            return {'error': 'No se encontró ruta válida'}
        dist_km = final_dist / 1000
        return {
            'path': final_path,
            'nodes_visited': len(final_path),
            'distance_km': round(dist_km, 3),
            'generations_run': config.get('generations', 1000),
            'fitness_history': [d/1000 for d in history],
            'waypoints_order': []  # no hay waypoints
        }