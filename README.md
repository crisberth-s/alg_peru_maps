# 🌎 Perú Route Lab — Plataforma de Comparación de Algoritmos de Ruta

![Flask](https://img.shields.io/badge/Backend-Flask-blue?logo=flask)
![Python](https://img.shields.io/badge/Python-3.8+-yellow?logo=python)
![Google Maps](https://img.shields.io/badge/Map-Google%20Maps-green)
![License](https://img.shields.io/badge/License-MIT-lightgrey)

Plataforma universitaria y profesional para comparar visual y estadísticamente algoritmos de búsqueda de rutas sobre **redes viales reales** (OpenStreetMap) y sobre el **grafo abstracto de las 196 provincias peruanas**.

Incluye **siete algoritmos** (Dijkstra, A*, Greedy, BFS, DFS, Bellman-Ford y Algoritmo Genético), un **dashboard interactivo** con mapa de Google Maps y un panel de resultados con métricas de rendimiento.

---

# 📦 Características

## Dos modos de entrada

### 🚗 Calles reales (OSM)

Descarga el grafo vial real con OSMnx, calcula rutas sobre la red de carreteras y muestra las polilíneas sobre el mapa.

### 🏛 Provincias del Perú

Grafo de 196 provincias donde cada nodo es una provincia y las aristas conectan provincias vecinas.

Los pesos se calculan usando distancia Haversine entre capitales provinciales.

No requiere descargas adicionales.

---

## 🧠 Siete algoritmos implementados

| Algoritmo         | Tipo           | Óptimo | Descripción                                            |
| ----------------- | -------------- | ------ | ------------------------------------------------------ |
| Dijkstra          | Clásico        | ✅      | Cola de prioridad y pesos positivos.                   |
| A*                | Informado      | ✅      | Usa heurística Haversine para expandir menos nodos.    |
| Greedy Best-First | Informado      | ❌      | Solo heurística; rápido pero subóptimo.                |
| BFS               | No informado   | ❌*     | Menor número de aristas, ignora pesos.                 |
| DFS               | No informado   | ❌      | Exploración profunda; puede producir rutas muy largas. |
| Bellman-Ford      | Clásico        | ✅      | Relajación V-1 veces; soporta pesos negativos.         |
| Genético (AG)     | Metaheurístico | ❌**    | Evolución de población; soporta TSP con waypoints.     |

* BFS encuentra el camino con menos saltos, no necesariamente el más corto en distancia.
** El algoritmo genético converge a soluciones cercanas a la óptima dependiendo de sus parámetros.

---

## 📊 Comparación interactiva

* Comparación simultánea de múltiples algoritmos.
* Visualización de rutas sobre el mapa.
* Colores distintos por algoritmo.
* Activar/desactivar rutas haciendo clic en el círculo de color.
* Tabla estadística con:

  * Distancia total
  * Tiempo de ejecución
  * Nodos visitados
  * Estado/Eficiencia

---

## ⚙️ Parámetros configurables del Algoritmo Genético

Incluye sliders interactivos para:

* Generaciones
* Tamaño de población
* Tasa de mutación
* Elitismo

Valores por defecto:

* 1000 generaciones
* 300 individuos
* 10% mutación
* 15 élite

---

## 💾 Caché de grafos OSM

Los grafos descargados se almacenan automáticamente en:

```text
cache_graphs/
```

Esto evita descargas repetidas y acelera ejecuciones posteriores.

---

## 🌑 Frontend moderno

* Tema oscuro profesional
* Google Maps integrado
* Diseño responsive
* Ideal para presentaciones académicas
* Tipografías:

  * Space Mono
  * DM Sans

---

# 📸 Captura de pantalla

*(Agregar aquí una imagen del dashboard mostrando múltiples rutas y métricas.)*

---

# 🚀 Instalación y ejecución

## Requisitos previos

* Python 3.8+
* pip
* API Key de Google Maps

Debes habilitar en Google Cloud:

* Maps JavaScript API
* Places API

Sin API Key el mapa no se visualizará, aunque los algoritmos seguirán funcionando.

---

# 📥 Clonar el repositorio

```bash
git clone https://github.com/tuusuario/peru-route-lab.git
cd peru-route-lab
```

---

# 📦 Instalar dependencias

```bash
pip install -r requirements.txt
```

Dependencias principales:

* Flask
* Flask-CORS
* OSMnx
* NetworkX
* NumPy
* Geopy

---

# 🔑 Dónde colocar la API Key de Google Maps

Solo necesitas modificar:

```text
config.py
```

Dentro del archivo:

```python
GMAPS_KEY = "TU_API_KEY_REAL"
```

Reemplaza:

```python
TU_API_KEY_REAL
```

por tu clave real.

No necesitas modificar ningún otro archivo.

Flask inyecta automáticamente la clave al frontend usando Jinja2.

---

## ⚠️ Configuración recomendada en Google Cloud

Si restringes dominios agrega:

```text
http://localhost:5000/*
```

Debes tener habilitadas:

* Maps JavaScript API
* Places API

---

# 🗺 Generar el grafo completo de provincias

El archivo:

```text
data/provincias.json
```

incluye un ejemplo reducido.

Para generar las 196 provincias reales:

1. Descarga un shapefile o GeoJSON oficial del Perú.
2. Ejecuta:

```bash
python generar_provincias.py
```

Esto generará automáticamente:

```text
data/provincias.json
```

con provincias y vecinos calculados automáticamente.

---

# ▶️ Ejecutar el servidor

```bash
python main.py
```

Salida esperada:

```text
* Running on http://0.0.0.0:5000
```

Abrir:

```text
http://localhost:5000
```

---

# 🧭 Guía de uso

## 1. Seleccionar modo

### 🚗 Calles reales (OSM)

Usa autocompletado de Google Maps para origen y destino.

### 🏛 Provincias del Perú

Selecciona provincias desde listas desplegables.

---

## 2. Agregar waypoints (opcional)

Permite:

* Ordenar múltiples paradas
* Resolver TSP con algoritmo genético

---

## 3. Elegir algoritmos

Puedes seleccionar varios simultáneamente.

---

## 4. Configurar AG

Si activas Genético aparecerán sliders configurables.

---

## 5. Ejecutar comparación

Pulsa:

```text
🔍 Comparar algoritmos
```

---

## 6. Analizar resultados

Verás:

* Rutas coloreadas
* Tabla estadística
* Métricas de rendimiento

---

# 🧱 Estructura del proyecto

```text
peru-route-lab/
├── backend/
│   ├── algorithms/
│   │   ├── __init__.py
│   │   ├── dijkstra.py
│   │   ├── astar.py
│   │   ├── greedy.py
│   │   ├── bfs.py
│   │   ├── dfs.py
│   │   ├── bellman_ford.py
│   │   └── genetic.py
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── graph_loader.py
│   │   ├── path_builder.py
│   │   └── comparator.py
│   │
│   └── __init__.py
│
├── data/
│   └── provincias.json
│
├── templates/
│   └── index.html
│
├── cache_graphs/
│
├── config.py
├── main.py
├── requirements.txt
└── README.md
```

---

# 📈 Posibles mejoras futuras

## 📊 Persistencia de estadísticas

Guardar resultados históricos de algoritmos en:

* SQLite
* PostgreSQL
* JSON
* CSV

---

## 📉 Dashboard de análisis

Agregar gráficos comparativos:

* Tiempo vs nodos visitados
* Distancia vs precisión
* Consumo de memoria
* Heatmaps de expansión

---

## 🧠 Nuevos algoritmos

Posibles incorporaciones:

* Bidirectional Search
* Floyd-Warshall
* IDA*
* Simulated Annealing
* Ant Colony Optimization
* Particle Swarm Optimization

---

## ☁️ Despliegue en producción

Opciones recomendadas:

* Render
* Railway
* AWS
* Docker
* Nginx + Gunicorn

---

## 🛰 Integración avanzada

* Elevación real
* Tráfico en tiempo real
* Restricciones vehiculares
* Rutas multimodales

---

# 📜 Licencia

Proyecto académico bajo licencia MIT.

---

# 👨‍💻 Autor

Proyecto desarrollado para investigación, visualización y comparación avanzada de algoritmos de búsqueda y optimización sobre mapas del Perú.
