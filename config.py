"""Configuración global de la aplicación."""
import os

class Config:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    CACHE_DIR = os.path.join(BASE_DIR, 'cache_graphs')
    OSMNX_TIMEOUT = 300

    # ⚠️ PON AQUÍ TU API KEY DE GOOGLE MAPS
    GMAPS_KEY = "aqui tu api key"


    