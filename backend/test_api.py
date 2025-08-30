"""
🧪 Script de Testing para API de Microbioma
==========================================

Este script prueba todos los endpoints de la API y verifica que funcionen correctamente.

Uso:
    python test_api.py

Autor: Proyecto Microorganismos
Fecha: 2025
"""

import requests
import json
import time
from datetime import datetime
import sys


class MicrobiomeAPITester:
    """
    Clase para testear la API de microbioma.
    """
    
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results = []
        
    def log_test(self, test_name: str, success: bool, message: str = "", data: dict = None):
        """
        Registrar resultado de un test.
        """
        result = {
            'test': test_name,
            'success': success,
            'message': message,
            'timestamp': datetime.now().isoformat(),
            'data': data
        }
        
        self.test_results.append(result)
        
        # Mostrar resultado inmediatamente
        status = "✅" if success else "❌"
        print(f"{status} {test_name}: {message}")
        
        if data and success:
            # Mostrar algunos datos interesantes
            if isinstance(data, dict):
                for key, value in list(data.items())[:3]:  # Solo primeros 3
                    print(f"   📊 {key}: {value}")
    
    def test_server_health(self):
        """
        Test 1: Verificar que el servidor está corriendo.
        """
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                self.log_test(
                    "Servidor funcionando",
                    True,
                    f"Status: {data.get('status', 'unknown')}",
                    data
                )
                return True
            else:
                self.log_test(
                    "Servidor funcionando",
                    False,
                    f"HTTP {response.status_code}"
                )
                return False
                
        except requests.exceptions.ConnectionError:
            self.log_test(
                "Servidor funcionando", 
                False,
                "No se puede conectar al servidor. ¿Está corriendo?"
            )
            return False
        except Exception as e:
            self.log_test(
                "Servidor funcionando",
                False, 
                f"Error: {str(e)}"
            )
            return False
    
    def test_home_endpoint(self):
        """
        Test 2: Probar endpoint principal.
        """
        try:
            response = self.session.get(f"{self.base_url}/")
            
            if response.status_code == 200:
                data = response.json()
                
                # Verificar campos esperados
                expected_fields = ['message', 'version', 'endpoints', 'total_environments']
                missing_fields = [field for field in expected_fields if field not in data]
                
                if not missing_fields:
                    self.log_test(
                        "Endpoint principal (/)",
                        True,
                        f"Versión: {data.get('version', 'N/A')}",
                        {
                            'total_environments': data.get('total_environments', 0),
                            'endpoints_count': len(data.get('endpoints', []))
                        }
                    )
                    return data
                else:
                    self.log_test(
                        "Endpoint principal (/)",
                        False,
                        f"Campos faltantes: {missing_fields}"
                    )
                    return None
            else:
                self.log_test(
                    "Endpoint principal (/)",
                    False,
                    f"HTTP {response.status_code}"
                )
                return None
                
        except Exception as e:
            self.log_test(
                "Endpoint principal (/)",
                False,
                f"Error: {str(e)}"
            )
            return None
    
    def test_environments_endpoint(self):
        """
        Test 3: Probar endpoint de ambientes.
        """
        try:
            response = self.session.get(f"{self.base_url}/environments")
            
            if response.status_code == 200:
                data = response.json()
                
                environments = data.get('environments', [])
                if environments:
                    # Verificar estructura de un ambiente
                    first_env = environments[0]
                    required_fields = ['name', 'sample_count']
                    
                    if all(field in first_env for field in required_fields):
                        self.log_test(
                            "Lista de ambientes (/environments)",
                            True,
                            f"Encontrados {len(environments)} ambientes",
                            {
                                'total_environments': data.get('total_environments', 0),
                                'total_samples': data.get('total_samples', 0),
                                'top_environment': first_env['name']
                            }
                        )
                        return environments
                    else:
                        self.log_test(
                            "Lista de ambientes (/environments)",
                            False,
                            "Estructura de ambiente inválida"
                        )
                        return None
                else:
                    self.log_test(
                        "Lista de ambientes (/environments)",
                        False,
                        "No se encontraron ambientes"
                    )
                    return None
            else:
                self.log_test(
                    "Lista de ambientes (/environments)",
                    False,
                    f"HTTP {response.status_code}"
                )
                return None
                
        except Exception as e:
            self.log_test(
                "Lista de ambientes (/environments)",
                False,
                f"Error: {str(e)}"
            )
            return None
    
    def test_composition_endpoint(self, environments):
        """
        Test 4: Probar endpoint de composición.
        """
        if not environments:
            self.log_test(
                "Composición de ambiente",
                False,
                "No hay ambientes para probar"
            )
            return
        
        # Probar con el ambiente más común
        test_env = environments[0]['name']
        
        try:
            # URL encode para espacios y caracteres especiales
            import urllib.parse
            encoded_env = urllib.parse.quote(test_env)
            
            response = self.session.get(f"{self.base_url}/composition/{encoded_env}")
            
            if response.status_code == 200:
                data = response.json()
                
                required_fields = ['environment', 'total_samples', 'composition']
                if all(field in data for field in required_fields):
                    composition = data['composition']
                    
                    if composition:
                        # Verificar estructura de composición
                        first_taxon = composition[0]
                        taxon_fields = ['taxon', 'abundance']
                        
                        if all(field in first_taxon for field in taxon_fields):
                            self.log_test(
                                f"Composición de '{test_env}'",
                                True,
                                f"Encontrados {len(composition)} filos",
                                {
                                    'total_samples': data['total_samples'],
                                    'most_abundant': first_taxon['taxon'],
                                    'abundance': f"{first_taxon['abundance']}%"
                                }
                            )
                        else:
                            self.log_test(
                                f"Composición de '{test_env}'",
                                False,
                                "Estructura de taxón inválida"
                            )
                    else:
                        self.log_test(
                            f"Composición de '{test_env}'",
                            False,
                            "No se encontró composición"
                        )
                else:
                    self.log_test(
                        f"Composición de '{test_env}'",
                        False,
                        f"Campos faltantes: {[f for f in required_fields if f not in data]}"
                    )
            elif response.status_code == 404:
                self.log_test(
                    f"Composición de '{test_env}'",
                    False,
                    "Ambiente no encontrado"
                )
            else:
                self.log_test(
                    f"Composición de '{test_env}'",
                    False,
                    f"HTTP {response.status_code}"
                )
                
        except Exception as e:
            self.log_test(
                f"Composición de '{test_env}'",
                False,
                f"Error: {str(e)}"
            )
    
    def test_stats_endpoint(self):
        """
        Test 5: Probar endpoint de estadísticas.
        """
        try:
            response = self.session.get(f"{self.base_url}/stats")
            
            if response.status_code == 200:
                data = response.json()
                
                required_sections = ['dataset_info', 'top_environments', 'sample_distribution']
                if all(section in data for section in required_sections):
                    dataset_info = data['dataset_info']
                    
                    self.log_test(
                        "Estadísticas generales (/stats)",
                        True,
                        "Estadísticas completas obtenidas",
                        {
                            'total_environments': dataset_info.get('total_environments', 0),
                            'total_samples': dataset_info.get('total_samples', 0),
                            'unique_phyla': dataset_info.get('unique_phyla', 0)
                        }
                    )
                else:
                    missing = [s for s in required_sections if s not in data]
                    self.log_test(
                        "Estadísticas generales (/stats)",
                        False,
                        f"Secciones faltantes: {missing}"
                    )
            else:
                self.log_test(
                    "Estadísticas generales (/stats)",
                    False,
                    f"HTTP {response.status_code}"
                )
                
        except Exception as e:
            self.log_test(
                "Estadísticas generales (/stats)",
                False,
                f"Error: {str(e)}"
            )
    
    def test_error_handling(self):
        """
        Test 6: Probar manejo de errores.
        """
        # Test ambiente inexistente
        try:
            response = self.session.get(f"{self.base_url}/composition/ambiente_inexistente")
            
            if response.status_code == 404:
                self.log_test(
                    "Manejo de errores (404)",
                    True,
                    "Error 404 manejado correctamente"
                )
            else:
                self.log_test(
                    "Manejo de errores (404)",
                    False,
                    f"Esperaba 404, obtuvo {response.status_code}"
                )
        except Exception as e:
            self.log_test(
                "Manejo de errores (404)",
                False,
                f"Error: {str(e)}"
            )
        
        # Test endpoint inexistente
        try:
            response = self.session.get(f"{self.base_url}/endpoint_inexistente")
            
            if response.status_code == 404:
                self.log_test(
                    "Manejo de errores (endpoint inexistente)",
                    True,
                    "Endpoint inexistente manejado correctamente"
                )
            else:
                self.log_test(
                    "Manejo de errores (endpoint inexistente)",
                    False,
                    f"Esperaba 404, obtuvo {response.status_code}"
                )
        except Exception as e:
            self.log_test(
                "Manejo de errores (endpoint inexistente)",
                False,
                f"Error: {str(e)}"
            )
    
    def run_all_tests(self):
        """
        Ejecutar todos los tests en secuencia.
        """
        print("🧪 Iniciando tests de la API de Microbioma")
        print("=" * 60)
        
        start_time = time.time()
        
        # Test 1: Verificar servidor
        if not self.test_server_health():
            print("\n❌ Servidor no está disponible. Abortando tests.")
            return False
        
        # Esperar un poco para que los datos se carguen
        print("\n⏳ Esperando que los datos se carguen...")
        time.sleep(2)
        
        # Test 2: Endpoint principal
        home_data = self.test_home_endpoint()
        
        # Test 3: Lista de ambientes
        environments = self.test_environments_endpoint()
        
        # Test 4: Composición específica
        self.test_composition_endpoint(environments)
        
        # Test 5: Estadísticas
        self.test_stats_endpoint()
        
        # Test 6: Manejo de errores
        self.test_error_handling()
        
        # Resumen
        end_time = time.time()
        duration = round(end_time - start_time, 2)
        
        successful_tests = sum(1 for result in self.test_results if result['success'])
        total_tests = len(self.test_results)
        
        print("\n" + "=" * 60)
        print("📋 RESUMEN DE TESTS")
        print(f"✅ Tests exitosos: {successful_tests}/{total_tests}")
        print(f"⏱️  Tiempo total: {duration} segundos")
        
        if successful_tests == total_tests:
            print("🎉 ¡Todos los tests pasaron! La API está funcionando correctamente.")
            return True
        else:
            print("⚠️  Algunos tests fallaron. Revisa los detalles arriba.")
            return False
    
    def save_results(self, filename="test_results.json"):
        """
        Guardar resultados en archivo JSON.
        """
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.test_results, f, indent=2, ensure_ascii=False)
            print(f"📄 Resultados guardados en: {filename}")
        except Exception as e:
            print(f"❌ Error guardando resultados: {e}")


def main():
    """
    Función principal para ejecutar los tests.
    """
    # Verificar argumentos
    base_url = "http://localhost:5000"
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    
    print(f"🔗 Testeando API en: {base_url}")
    
    # Crear tester y ejecutar
    tester = MicrobiomeAPITester(base_url)
    success = tester.run_all_tests()
    
    # Guardar resultados
    tester.save_results()
    
    # Exit code para scripts
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
