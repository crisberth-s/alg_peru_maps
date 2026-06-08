import os
import pickle
import logging
from config import Config
import osmnx as ox

logger = logging.getLogger(__name__)

class GraphLoader:
    def __init__(self):
        ox.config(log_console=False, use_cache=True, timeout=Config.OSMNX_TIMEOUT)
        os.makedirs(Config.CACHE_DIR, exist_ok=True)

    def get_graph_by_bbox(self, north, south, east, west, simplify=True):
        key = f"bbox_{north:.5f}_{south:.5f}_{east:.5f}_{west:.5f}_{simplify}"
        cache_path = os.path.join(Config.CACHE_DIR, key + '.pkl')
        if os.path.exists(cache_path):
            logger.info(f"Cargando grafo desde caché: {cache_path}")
            with open(cache_path, 'rb') as f:
                return pickle.load(f)
        logger.info("Descargando grafo de OSM...")
        G = ox.graph_from_bbox(north, south, east, west,
                               network_type='drive', simplify=simplify)
        with open(cache_path, 'wb') as f:
            pickle.dump(G, f)
        logger.info(f"Grafo guardado en caché: {cache_path}")
        return G

    @staticmethod
    def build_adjacency(G):
        adj = {}
        for u, v, data in G.edges(data=True):
            w = data.get('length', 1)
            adj.setdefault(u, []).append((v, w))
            if not data.get('oneway', False):
                adj.setdefault(v, []).append((u, w))
        return adj

    @staticmethod
    def node_coordinates(G):
        return {node: (data['y'], data['x']) for node, data in G.nodes(data=True)}