import os
import json
import logging
import datetime
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from config import Config
from backend.core.graph_loader import GraphLoader
from backend.core.comparator import AlgorithmComparator
from backend.core.path_builder import path_to_coordinates
import osmnx as ox
from math import radians, sin, cos, sqrt, asin

app = Flask(__name__, template_folder='templates')
CORS(app)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

graph_loader = GraphLoader()

# ==================== GRAFO DE PROVINCIAS ====================
def haversine(lat1, lon1, lat2, lon2):
    R = 6371000
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    return R * 2 * asin(sqrt(a))

with open('data/provincias.json', 'r', encoding='utf-8') as f:
    PROVINCE_DATA = json.load(f)

def build_province_graph(data):
    adj = {}
    coordinates = {}
    for prov in data:
        node = prov['name']
        coordinates[node] = (prov['lat'], prov['lon'])
        adj[node] = []
    for prov in data:
        u = prov['name']
        for v_name in prov['neighbors']:
            if v_name in adj:
                w = haversine(*coordinates[u], *coordinates[v_name])
                adj[u].append((v_name, w))
                # Asegurar bidireccionalidad
                if not any(n == u for n, _ in adj[v_name]):
                    adj[v_name].append((u, w))
    return adj, coordinates

PROVINCE_ADJ, PROVINCE_COORDS = build_province_graph(PROVINCE_DATA)

@app.route('/api/provinces', methods=['GET'])
def get_provinces():
    return jsonify(sorted([p['name'] for p in PROVINCE_DATA]))

# ==================== RUTA PRINCIPAL ====================
@app.route('/')
def index():
    return render_template('index.html', gmaps_key=Config.GMAPS_KEY)

@app.route('/api/routes', methods=['POST'])
def compare_routes():
    data = request.get_json()
    logger.info(f"Solicitud recibida: {data}")

    mode = data.get('mode', 'osm')

    if mode == 'province':
        # --- MODO PROVINCIAS ---
        origin_name = data.get('origin_name')
        dest_name = data.get('dest_name')
        waypoint_names = [wp['name'] for wp in data.get('waypoints', [])]

        if not origin_name or not dest_name:
            return jsonify({'error': 'Faltan provincia de origen y/o destino'}), 400
        if origin_name not in PROVINCE_ADJ or dest_name not in PROVINCE_ADJ:
            return jsonify({'error': 'Una de las provincias no existe en el grafo'}), 400

        start_node = origin_name
        end_node = dest_name
        waypoints_for_genetic = [{'name': name, 'lat': PROVINCE_COORDS[name][0], 'lon': PROVINCE_COORDS[name][1]} for name in waypoint_names]
        adj = PROVINCE_ADJ
        coords = PROVINCE_COORDS
        comparator = AlgorithmComparator(None, adj, coords, start_node, end_node)
        algorithms = data.get('algorithms', ['dijkstra'])
        genetic_config = data.get('genetic_config', {})
        results = comparator.compare(algorithms, waypoints=waypoints_for_genetic, genetic_config=genetic_config)

        # Convertir paths a coordenadas
        for algo, res in results.items():
            if 'path' in res and res['path']:
                res['coordinates'] = [list(PROVINCE_COORDS[node]) for node in res['path']]

        # --- Guardar comparación (modo provincias) ---
        stats_dir = 'estadisticas'
        os.makedirs(stats_dir, exist_ok=True)
        filename = f"comp_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S_%f')}.json"
        filepath = os.path.join(stats_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump({
                "fecha": datetime.datetime.now().isoformat(),
                "modo": mode,
                "origen": origin_name,
                "destino": dest_name,
                "algoritmos": results
            }, f, ensure_ascii=False, indent=2)
        # --- Fin guardado ---

        return jsonify({
            'success': True,
            'algorithms': results,
            'origin_name': origin_name,
            'dest_name': dest_name
        })

    else:
        # --- MODO OSM ---
        if not data.get('origin_lat') or not data.get('dest_lat'):
            return jsonify({'error': 'Coordenadas incompletas'}), 400

        lats = [data['origin_lat'], data['dest_lat']] + [wp['lat'] for wp in data.get('waypoints', [])]
        lons = [data['origin_lon'], data['dest_lon']] + [wp['lon'] for wp in data.get('waypoints', [])]
        north, south = max(lats) + 0.5, min(lats) - 0.5
        east, west = max(lons) + 0.5, min(lons) - 0.5

        try:
            G = graph_loader.get_graph_by_bbox(north, south, east, west)
        except Exception as e:
            logger.exception("Error al obtener grafo OSM")
            return jsonify({'error': f'Error al descargar grafo: {str(e)}'}), 500

        adj = graph_loader.build_adjacency(G)
        coords = graph_loader.node_coordinates(G)

        origin_node = ox.nearest_nodes(G, X=data['origin_lon'], Y=data['origin_lat'])
        dest_node = ox.nearest_nodes(G, X=data['dest_lon'], Y=data['dest_lat'])

        waypoints_osm = data.get('waypoints', [])
        comparator = AlgorithmComparator(G, adj, coords, origin_node, dest_node)
        algorithms = data.get('algorithms', ['dijkstra'])
        genetic_config = data.get('genetic_config', {})
        results = comparator.compare(algorithms, waypoints=waypoints_osm, genetic_config=genetic_config)

        for algo, res in results.items():
            if 'path' in res and res['path']:
                res['coordinates'] = path_to_coordinates(G, res['path'])

        # --- Guardar comparación (modo OSM) ---
        stats_dir = 'estadisticas'
        os.makedirs(stats_dir, exist_ok=True)
        filename = f"comp_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S_%f')}.json"
        filepath = os.path.join(stats_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump({
                "fecha": datetime.datetime.now().isoformat(),
                "modo": mode,
                "origen": data.get('origin_name', ''),
                "destino": data.get('dest_name', ''),
                "algoritmos": results
            }, f, ensure_ascii=False, indent=2)
        # --- Fin guardado ---

        return jsonify({
            'success': True,
            'algorithms': results,
            'origin_name': data.get('origin_name', ''),
            'dest_name': data.get('dest_name', '')
        })

# ==================== ESTADÍSTICAS ====================
@app.route('/api/stats')
def get_stats():
    stats_dir = 'estadisticas'
    if not os.path.exists(stats_dir):
        return jsonify([])
    files = [f for f in os.listdir(stats_dir) if f.endswith('.json')]
    all_data = []
    for fname in sorted(files, reverse=True):    # más reciente primero
        with open(os.path.join(stats_dir, fname), 'r', encoding='utf-8') as f:
            all_data.append(json.load(f))
    return jsonify(all_data)

@app.route('/stats')
def stats_page():
    return render_template('stats.html')

if __name__ == '__main__':
    os.makedirs(Config.CACHE_DIR, exist_ok=True)
    app.run(host='0.0.0.0', port=5000, debug=True)