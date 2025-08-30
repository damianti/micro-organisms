"""
🌐 API de Microbioma - Parte 1
==============================

API REST simple que sirve datos de composición microbiana.

Endpoints disponibles:
- GET / - Información de la API
- GET /environments - Lista de ambientes disponibles
- GET /composition/<environment> - Composición de un ambiente
- GET /stats - Estadísticas generales

Autor: Proyecto Microorganismos  
Fecha: 2025
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import sys
from datetime import datetime
import traceback

# Importar nuestro procesador
from data_processor import MicrobiomeDataProcessor

# Crear aplicación Flask
app = Flask(__name__)

# Configurar CORS para permitir requests desde el frontend
CORS(app, origins=["http://localhost:3000", "http://localhost:8080"])

# Variables globales para datos procesados
processor = None
environments_data = {}
processing_status = {
    'loaded': False,
    'loading': False,
    'error': None,
    'last_update': None
}


def initialize_data():
    """
    Inicializar y procesar todos los datos al arrancar el servidor.
    """
    global processor, environments_data, processing_status
    
    try:
        processing_status['loading'] = True
        processing_status['error'] = None
        
        print("🚀 Inicializando datos del microbioma...")
        print("-" * 50)
        
        # Ruta a los datos (ajustar según tu configuración)
        data_path = "../Microbe-vis-data"
        
        if not os.path.exists(data_path):
            raise FileNotFoundError(f"Directorio de datos no encontrado: {data_path}")
        
        # Crear procesador y cargar datos
        processor = MicrobiomeDataProcessor(data_path)
        success = processor.process_all_data(min_samples=100)
        
        if not success:
            raise Exception("Error durante el procesamiento de datos")
        
        # Convertir a formato JSON-friendly
        environments_data = {}
        available_envs = processor.get_available_environments()
        
        print(f"📊 Preparando {len(available_envs)} ambientes para la API...")
        
        for env_info in available_envs:
            env_name = env_info['name']
            try:
                composition = processor.get_composition_for_environment(env_name, min_abundance=0.5)
                environments_data[env_name] = composition
            except Exception as e:
                print(f"⚠️  Error procesando {env_name}: {e}")
                continue
        
        processing_status['loaded'] = True
        processing_status['loading'] = False
        processing_status['last_update'] = datetime.now().isoformat()
        
        print("-" * 50)
        print(f"✅ API inicializada con {len(environments_data)} ambientes")
        print("🌐 Servidor listo para recibir requests")
        
        return True
        
    except Exception as e:
        processing_status['loading'] = False
        processing_status['error'] = str(e)
        print(f"❌ Error inicializando datos: {e}")
        traceback.print_exc()
        return False


# ========================================
# ENDPOINTS DE LA API
# ========================================

@app.route('/')
def home():
    """
    Endpoint principal con información de la API.
    """
    return jsonify({
        "message": "🧬 API de Microbioma - Parte 1",
        "version": "1.0.0",
        "description": "API para analizar composición microbiana por ambiente",
        "status": processing_status,
        "endpoints": [
            {
                "method": "GET",
                "path": "/",
                "description": "Información de la API"
            },
            {
                "method": "GET", 
                "path": "/environments",
                "description": "Lista de ambientes disponibles"
            },
            {
                "method": "GET",
                "path": "/composition/<environment>",
                "description": "Composición microbiana de un ambiente específico"
            },
            {
                "method": "GET",
                "path": "/stats", 
                "description": "Estadísticas generales del dataset"
            }
        ],
        "total_environments": len(environments_data) if processing_status['loaded'] else 0
    })


@app.route('/environments')
def get_environments():
    """
    Obtener lista de todos los ambientes disponibles.
    """
    if not processing_status['loaded']:
        return jsonify({
            'error': 'Datos no cargados',
            'status': processing_status
        }), 503
    
    try:
        # Crear lista de ambientes con información
        env_list = []
        for env_name, data in environments_data.items():
            env_list.append({
                'name': env_name,
                'sample_count': data['total_samples'],
                'phyla_count': len(data['composition'])
            })
        
        # Ordenar por número de muestras (descendente)
        env_list.sort(key=lambda x: x['sample_count'], reverse=True)
        
        return jsonify({
            'environments': env_list,
            'total_environments': len(env_list),
            'total_samples': sum(env['sample_count'] for env in env_list)
        })
        
    except Exception as e:
        return jsonify({
            'error': f'Error obteniendo ambientes: {str(e)}'
        }), 500


@app.route('/composition/<environment>')
def get_composition(environment):
    """
    Obtener composición microbiana de un ambiente específico.
    
    Args:
        environment (str): Nombre del ambiente
    """
    if not processing_status['loaded']:
        return jsonify({
            'error': 'Datos no cargados',
            'status': processing_status
        }), 503
    
    # Verificar que el ambiente existe
    if environment not in environments_data:
        available_envs = list(environments_data.keys())[:10]  # Mostrar solo 10
        return jsonify({
            'error': f'Ambiente "{environment}" no encontrado',
            'available_environments': available_envs,
            'total_available': len(environments_data)
        }), 404
    
    try:
        # Obtener datos del ambiente
        composition_data = environments_data[environment].copy()
        
        # Agregar metadatos adicionales
        composition_data['request_timestamp'] = datetime.now().isoformat()
        composition_data['data_source'] = 'GTDB taxonomy'
        
        return jsonify(composition_data)
        
    except Exception as e:
        return jsonify({
            'error': f'Error obteniendo composición: {str(e)}'
        }), 500


@app.route('/stats')
def get_stats():
    """
    Obtener estadísticas generales del dataset.
    """
    if not processing_status['loaded']:
        return jsonify({
            'error': 'Datos no cargados',
            'status': processing_status
        }), 503
    
    try:
        # Calcular estadísticas
        total_environments = len(environments_data)
        total_samples = sum(data['total_samples'] for data in environments_data.values())
        
        # Top 5 ambientes por número de muestras
        top_environments = []
        env_items = list(environments_data.items())
        env_items.sort(key=lambda x: x[1]['total_samples'], reverse=True)
        
        for env_name, data in env_items[:5]:
            top_environments.append({
                'name': env_name,
                'samples': data['total_samples'],
                'phyla_detected': len(data['composition'])
            })
        
        # Estadísticas de filos
        all_phyla = set()
        for data in environments_data.values():
            for taxon_info in data['composition']:
                all_phyla.add(taxon_info['taxon_full'])
        
        return jsonify({
            'dataset_info': {
                'total_environments': total_environments,
                'total_samples': total_samples,
                'unique_phyla': len(all_phyla),
                'processing_time': processing_status['last_update']
            },
            'top_environments': top_environments,
            'sample_distribution': {
                'min_samples': min(data['total_samples'] for data in environments_data.values()),
                'max_samples': max(data['total_samples'] for data in environments_data.values()),
                'avg_samples': round(total_samples / total_environments, 1)
            },
            'status': processing_status
        })
        
    except Exception as e:
        return jsonify({
            'error': f'Error calculando estadísticas: {str(e)}'
        }), 500


# ========================================
# ENDPOINTS DE UTILIDAD
# ========================================

@app.route('/health')
def health_check():
    """
    Endpoint para verificar que la API está funcionando.
    """
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'data_loaded': processing_status['loaded']
    })


@app.route('/reload')
def reload_data():
    """
    Recargar datos (útil para desarrollo).
    """
    if processing_status['loading']:
        return jsonify({
            'message': 'Ya se están cargando los datos...',
            'status': processing_status
        }), 409
    
    success = initialize_data()
    
    if success:
        return jsonify({
            'message': 'Datos recargados exitosamente',
            'environments_loaded': len(environments_data),
            'status': processing_status
        })
    else:
        return jsonify({
            'error': 'Error recargando datos',
            'status': processing_status
        }), 500


# ========================================
# MANEJO DE ERRORES
# ========================================

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'error': 'Endpoint no encontrado',
        'message': 'Verifica la URL y método HTTP'
    }), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'error': 'Error interno del servidor',
        'message': 'Contacta al administrador si el problema persiste'
    }), 500


# ========================================
# EJECUTAR SERVIDOR
# ========================================

if __name__ == '__main__':
    print("🧬 Iniciando API de Microbioma...")
    print("=" * 60)
    
    # Inicializar datos al arrancar
    if not initialize_data():
        print("❌ No se pudieron cargar los datos. Servidor iniciado en modo limitado.")
    
    print("=" * 60)
    print("🌐 Servidor disponible en:")
    print("   • http://localhost:5000")
    print("   • http://127.0.0.1:5000")
    print("\n📋 Endpoints principales:")
    print("   • GET /environments")
    print("   • GET /composition/<environment>")
    print("   • GET /stats")
    print("\n🛑 Para detener: Ctrl+C")
    print("=" * 60)
    
    # Ejecutar servidor
    app.run(
        debug=True,           # Modo debug para desarrollo
        host='0.0.0.0',      # Permitir conexiones externas
        port=5000,           # Puerto estándar
        threaded=True        # Permitir múltiples requests simultáneos
    )
