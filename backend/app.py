"""
🌐 Microbiome API - Part 1
==========================

Simple REST API serving microbial composition data.

Available endpoints:
- GET / - API information
- GET /environments - List of available environments
- GET /composition/<environment> - Composition of an environment
- GET /stats - General statistics

Author: Microorganisms Project  
Date: 2025
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import sys
from datetime import datetime
import traceback

# Import our processor
from data_processor import MicrobiomeDataProcessor

# Create Flask application
app = Flask(__name__)

# Configure CORS to allow requests from frontend
CORS(app, origins=["http://localhost:3000", "http://localhost:8080"])

# Global variables for processed data
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
    Initialize and process all data when starting the server.
    """
    global processor, environments_data, processing_status
    
    try:
        processing_status['loading'] = True
        processing_status['error'] = None
        
        print("🚀 Initializing microbiome data...")
        print("-" * 50)
        
        # Path to data (adjust according to your configuration)
        data_path = "../Microbe-vis-data"
        
        if not os.path.exists(data_path):
            raise FileNotFoundError(f"Data directory not found: {data_path}")
        
        # Create processor and load data
        processor = MicrobiomeDataProcessor(data_path)
        success = processor.process_all_data(min_samples=100)
        
        if not success:
            raise Exception("Error during data processing")
        
        # Convert to JSON-friendly format
        environments_data = {}
        available_envs = processor.get_available_environments()
        
        print(f"📊 Preparing {len(available_envs)} environments for API...")
        
        for env_info in available_envs:
            env_name = env_info['name']
            try:
                composition = processor.get_composition_for_environment(env_name, min_abundance=0.5)
                environments_data[env_name] = composition
            except Exception as e:
                print(f"⚠️  Error processing {env_name}: {e}")
                continue
        
        processing_status['loaded'] = True
        processing_status['loading'] = False
        processing_status['last_update'] = datetime.now().isoformat()
        
        print("-" * 50)
        print(f"✅ API initialized with {len(environments_data)} environments")
        print("🌐 Server ready to receive requests")
        
        return True
        
    except Exception as e:
        processing_status['loading'] = False
        processing_status['error'] = str(e)
        print(f"❌ Error initializing data: {e}")
        traceback.print_exc()
        return False


# ========================================
# API ENDPOINTS
# ========================================

@app.route('/')
def home():
    """
    Main endpoint with API information.
    """
    return jsonify({
        "message": "🧬 Microbiome API - Part 1",
        "version": "1.0.0",
        "description": "API for analyzing microbial composition by environment",
        "status": processing_status,
        "endpoints": [
            {
                "method": "GET",
                "path": "/",
                "description": "API information"
            },
            {
                "method": "GET", 
                "path": "/environments",
                "description": "List of available environments"
            },
            {
                "method": "GET",
                "path": "/composition/<environment>",
                "description": "Microbial composition of a specific environment"
            },
            {
                "method": "GET",
                "path": "/stats", 
                "description": "General dataset statistics"
            }
        ],
        "total_environments": len(environments_data) if processing_status['loaded'] else 0
    })


@app.route('/environments')
def get_environments():
    """
    Get list of all available environments.
    """
    if not processing_status['loaded']:
        return jsonify({
            'error': 'Data not loaded',
            'status': processing_status
        }), 503
    
    try:
        # Create list of environments with information
        env_list = []
        for env_name, data in environments_data.items():
            env_list.append({
                'name': env_name,
                'sample_count': data['total_samples'],
                'phyla_count': len(data['composition'])
            })
        
        # Sort by sample count (descending)
        env_list.sort(key=lambda x: x['sample_count'], reverse=True)
        
        return jsonify({
            'environments': env_list,
            'total_environments': len(env_list),
            'total_samples': sum(env['sample_count'] for env in env_list)
        })
        
    except Exception as e:
        return jsonify({
            'error': f'Error getting environments: {str(e)}'
        }), 500


@app.route('/composition/<environment>')
def get_composition(environment):
    """
    Get microbial composition of a specific environment.
    
    Args:
        environment (str): Environment name
    """
    if not processing_status['loaded']:
        return jsonify({
            'error': 'Data not loaded',
            'status': processing_status
        }), 503
    
    # Verify environment exists
    if environment not in environments_data:
        available_envs = list(environments_data.keys())[:10]  # Show only 10
        return jsonify({
            'error': f'Environment "{environment}" not found',
            'available_environments': available_envs,
            'total_available': len(environments_data)
        }), 404
    
    try:
        # Get environment data
        composition_data = environments_data[environment].copy()
        
        # Add additional metadata
        composition_data['request_timestamp'] = datetime.now().isoformat()
        composition_data['data_source'] = 'GTDB taxonomy'
        
        return jsonify(composition_data)
        
    except Exception as e:
        return jsonify({
            'error': f'Error getting composition: {str(e)}'
        }), 500


@app.route('/stats')
def get_stats():
    """
    Get general dataset statistics.
    """
    if not processing_status['loaded']:
        return jsonify({
            'error': 'Data not loaded',
            'status': processing_status
        }), 503
    
    try:
        # Calculate statistics
        total_environments = len(environments_data)
        total_samples = sum(data['total_samples'] for data in environments_data.values())
        
        # Top 5 environments by sample count
        top_environments = []
        env_items = list(environments_data.items())
        env_items.sort(key=lambda x: x[1]['total_samples'], reverse=True)
        
        for env_name, data in env_items[:5]:
            top_environments.append({
                'name': env_name,
                'samples': data['total_samples'],
                'phyla_detected': len(data['composition'])
            })
        
        # Phyla statistics
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
            'error': f'Error calculating statistics: {str(e)}'
        }), 500


# ========================================
# UTILITY ENDPOINTS
# ========================================

@app.route('/health')
def health_check():
    """
    Endpoint to verify API is working.
    """
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'data_loaded': processing_status['loaded']
    })


@app.route('/reload')
def reload_data():
    """
    Reload data (useful for development).
    """
    if processing_status['loading']:
        return jsonify({
            'message': 'Data is already being loaded...',
            'status': processing_status
        }), 409
    
    success = initialize_data()
    
    if success:
        return jsonify({
            'message': 'Data reloaded successfully',
            'environments_loaded': len(environments_data),
            'status': processing_status
        })
    else:
        return jsonify({
            'error': 'Error reloading data',
            'status': processing_status
        }), 500


# ========================================
# ERROR HANDLING
# ========================================

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'error': 'Endpoint not found',
        'message': 'Check URL and HTTP method'
    }), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'error': 'Internal server error',
        'message': 'Contact administrator if problem persists'
    }), 500


# ========================================
# RUN SERVER
# ========================================

if __name__ == '__main__':
    print("🧬 Starting Microbiome API...")
    print("=" * 60)
    
    # Initialize data when starting
    if not initialize_data():
        print("❌ Could not load data. Server started in limited mode.")
    
    print("=" * 60)
    print("🌐 Server available at:")
    print("   • http://localhost:5000")
    print("   • http://127.0.0.1:5000")
    print("\n📋 Main endpoints:")
    print("   • GET /environments")
    print("   • GET /composition/<environment>")
    print("   • GET /stats")
    print("\n🛑 To stop: Ctrl+C")
    print("=" * 60)
    
    # Run server
    app.run(
        debug=True,           # Debug mode for development
        host='0.0.0.0',      # Allow external connections
        port=5000,           # Standard port
        threaded=True        # Allow multiple simultaneous requests
    )