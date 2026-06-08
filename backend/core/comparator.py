"""
Comparador de algoritmos: ejecuta los algoritmos seleccionados y recolecta métricas.
"""
import time
import logging
from typing import List, Dict, Any
from backend.algorithms import (
    dijkstra,
    astar,
    greedy,
    bfs,
    dfs,
    bellman_ford,
    genetic
)

logger = logging.getLogger(__name__)

class AlgorithmComparator:
    def __init__(self, G, adj, coordinates, start_node, end_node):
        self.G = G
        self.adj = adj
        self.coordinates = coordinates
        self.start_node = start_node
        self.end_node = end_node

    def compare(self, algorithms: List[str], waypoints=None, genetic_config=None) -> Dict[str, Any]:
        results = {}
        # Asegurar que genetic_config sea un diccionario
        if genetic_config is None:
            genetic_config = {}

        # Mapa de algoritmos de ruta directa
        algo_map = {
            'dijkstra': dijkstra.find_path,
            'astar': astar.find_path,
            'greedy': greedy.find_path,
            'bfs': bfs.find_path,
            'dfs': dfs.find_path,
            'bellman_ford': bellman_ford.find_path,
        }

        for algo_name in algorithms:
            if algo_name == 'genetic':
                # El genético ahora soporta tanto waypoints como ruta directa
                start = time.time()
                try:
                    result = genetic.find_path(
                        self.G, self.adj, self.coordinates,
                        self.start_node, self.end_node,
                        waypoints if waypoints else [],
                        genetic_config
                    )
                except Exception as e:
                    logger.exception("Error en Algoritmo Genético")
                    result = {'error': str(e)}
                elapsed = time.time() - start
                result['time'] = round(elapsed, 4)
                results[algo_name] = result
                continue

            if algo_name not in algo_map:
                results[algo_name] = {'error': f'Algoritmo no implementado: {algo_name}'}
                continue

            start = time.time()
            try:
                path, nodes_visited, distance = algo_map[algo_name](
                    self.adj, self.coordinates, self.start_node, self.end_node
                )
                if path is None:
                    result = {'error': 'No se encontró ruta'}
                else:
                    result = {
                        'path': path,
                        'nodes_visited': nodes_visited,
                        'distance_km': round(distance, 3) if distance is not None else None,
                    }
            except Exception as e:
                logger.exception(f"Error en {algo_name}")
                result = {'error': str(e)}
            elapsed = time.time() - start
            result['time'] = round(elapsed, 4)
            results[algo_name] = result

        return results