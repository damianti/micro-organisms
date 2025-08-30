"""
🧪 Testing Script for Microbiome API
=====================================

This script tests all API endpoints and verifies they work correctly.

Usage:
    python test_api.py

Author: Microorganisms Project
Date: 2025
"""

import requests
import json
import time
from datetime import datetime
import sys


class MicrobiomeAPITester:
    """
    Class for testing the microbiome API.
    """
    
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results = []
        
    def log_test(self, test_name: str, success: bool, message: str = "", data: dict = None):
        """
        Log test result.
        """
        result = {
            'test': test_name,
            'success': success,
            'message': message,
            'timestamp': datetime.now().isoformat(),
            'data': data
        }
        
        self.test_results.append(result)
        
        # Show result immediately
        status = "✅" if success else "❌"
        print(f"{status} {test_name}: {message}")
        
        if data and success:
            # Show some interesting data
            if isinstance(data, dict):
                for key, value in list(data.items())[:3]:  # Only first 3
                    print(f"   📊 {key}: {value}")
    
    def test_server_health(self):
        """
        Test 1: Verify server is running.
        """
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                self.log_test(
                    "Server working",
                    True,
                    f"Status: {data.get('status', 'unknown')}",
                    data
                )
                return True
            else:
                self.log_test(
                    "Server working",
                    False,
                    f"HTTP {response.status_code}"
                )
                return False
                
        except requests.exceptions.ConnectionError:
            self.log_test(
                "Server working", 
                False,
                "Cannot connect to server. Is it running?"
            )
            return False
        except Exception as e:
            self.log_test(
                "Server working",
                False, 
                f"Error: {str(e)}"
            )
            return False
    
    def test_home_endpoint(self):
        """
        Test 2: Test main endpoint.
        """
        try:
            response = self.session.get(f"{self.base_url}/")
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify expected fields
                expected_fields = ['message', 'version', 'endpoints', 'total_environments']
                missing_fields = [field for field in expected_fields if field not in data]
                
                if not missing_fields:
                    self.log_test(
                        "Main endpoint (/)",
                        True,
                        f"Version: {data.get('version', 'N/A')}",
                        {
                            'total_environments': data.get('total_environments', 0),
                            'endpoints_count': len(data.get('endpoints', []))
                        }
                    )
                    return data
                else:
                    self.log_test(
                        "Main endpoint (/)",
                        False,
                        f"Missing fields: {missing_fields}"
                    )
                    return None
            else:
                self.log_test(
                    "Main endpoint (/)",
                    False,
                    f"HTTP {response.status_code}"
                )
                return None
                
        except Exception as e:
            self.log_test(
                "Main endpoint (/)",
                False,
                f"Error: {str(e)}"
            )
            return None
    
    def test_environments_endpoint(self):
        """
        Test 3: Test environments endpoint.
        """
        try:
            response = self.session.get(f"{self.base_url}/environments")
            
            if response.status_code == 200:
                data = response.json()
                
                environments = data.get('environments', [])
                if environments:
                    # Verify structure of an environment
                    first_env = environments[0]
                    required_fields = ['name', 'sample_count']
                    
                    if all(field in first_env for field in required_fields):
                        self.log_test(
                            "Environment list (/environments)",
                            True,
                            f"Found {len(environments)} environments",
                            {
                                'total_environments': data.get('total_environments', 0),
                                'total_samples': data.get('total_samples', 0),
                                'top_environment': first_env['name']
                            }
                        )
                        return environments
                    else:
                        self.log_test(
                            "Environment list (/environments)",
                            False,
                            "Invalid environment structure"
                        )
                        return None
                else:
                    self.log_test(
                        "Environment list (/environments)",
                        False,
                        "No environments found"
                    )
                    return None
            else:
                self.log_test(
                    "Environment list (/environments)",
                    False,
                    f"HTTP {response.status_code}"
                )
                return None
                
        except Exception as e:
            self.log_test(
                "Environment list (/environments)",
                False,
                f"Error: {str(e)}"
            )
            return None
    
    def test_composition_endpoint(self, environments):
        """
        Test 4: Test composition endpoint.
        """
        if not environments:
            self.log_test(
                "Environment composition",
                False,
                "No environments to test"
            )
            return
        
        # Test with most common environment
        test_env = environments[0]['name']
        
        try:
            # URL encode for spaces and special characters
            import urllib.parse
            encoded_env = urllib.parse.quote(test_env)
            
            response = self.session.get(f"{self.base_url}/composition/{encoded_env}")
            
            if response.status_code == 200:
                data = response.json()
                
                required_fields = ['environment', 'total_samples', 'composition']
                if all(field in data for field in required_fields):
                    composition = data['composition']
                    
                    if composition:
                        # Verify composition structure
                        first_taxon = composition[0]
                        taxon_fields = ['taxon', 'abundance']
                        
                        if all(field in first_taxon for field in taxon_fields):
                            self.log_test(
                                f"Composition of '{test_env}'",
                                True,
                                f"Found {len(composition)} phyla",
                                {
                                    'total_samples': data['total_samples'],
                                    'most_abundant': first_taxon['taxon'],
                                    'abundance': f"{first_taxon['abundance']}%"
                                }
                            )
                        else:
                            self.log_test(
                                f"Composition of '{test_env}'",
                                False,
                                "Invalid taxon structure"
                            )
                    else:
                        self.log_test(
                            f"Composition of '{test_env}'",
                            False,
                            "No composition found"
                        )
                else:
                    self.log_test(
                        f"Composition of '{test_env}'",
                        False,
                        f"Missing fields: {[f for f in required_fields if f not in data]}"
                    )
            elif response.status_code == 404:
                self.log_test(
                    f"Composition of '{test_env}'",
                    False,
                    "Environment not found"
                )
            else:
                self.log_test(
                    f"Composition of '{test_env}'",
                    False,
                    f"HTTP {response.status_code}"
                )
                
        except Exception as e:
            self.log_test(
                f"Composition of '{test_env}'",
                False,
                f"Error: {str(e)}"
            )
    
    def test_stats_endpoint(self):
        """
        Test 5: Test statistics endpoint.
        """
        try:
            response = self.session.get(f"{self.base_url}/stats")
            
            if response.status_code == 200:
                data = response.json()
                
                required_sections = ['dataset_info', 'top_environments', 'sample_distribution']
                if all(section in data for section in required_sections):
                    dataset_info = data['dataset_info']
                    
                    self.log_test(
                        "General statistics (/stats)",
                        True,
                        "Complete statistics obtained",
                        {
                            'total_environments': dataset_info.get('total_environments', 0),
                            'total_samples': dataset_info.get('total_samples', 0),
                            'unique_phyla': dataset_info.get('unique_phyla', 0)
                        }
                    )
                else:
                    missing = [s for s in required_sections if s not in data]
                    self.log_test(
                        "General statistics (/stats)",
                        False,
                        f"Missing sections: {missing}"
                    )
            else:
                self.log_test(
                    "General statistics (/stats)",
                    False,
                    f"HTTP {response.status_code}"
                )
                
        except Exception as e:
            self.log_test(
                "General statistics (/stats)",
                False,
                f"Error: {str(e)}"
            )
    
    def test_error_handling(self):
        """
        Test 6: Test error handling.
        """
        # Test non-existent environment
        try:
            response = self.session.get(f"{self.base_url}/composition/nonexistent_environment")
            
            if response.status_code == 404:
                self.log_test(
                    "Error handling (404)",
                    True,
                    "404 error handled correctly"
                )
            else:
                self.log_test(
                    "Error handling (404)",
                    False,
                    f"Expected 404, got {response.status_code}"
                )
        except Exception as e:
            self.log_test(
                "Error handling (404)",
                False,
                f"Error: {str(e)}"
            )
        
        # Test non-existent endpoint
        try:
            response = self.session.get(f"{self.base_url}/nonexistent_endpoint")
            
            if response.status_code == 404:
                self.log_test(
                    "Error handling (non-existent endpoint)",
                    True,
                    "Non-existent endpoint handled correctly"
                )
            else:
                self.log_test(
                    "Error handling (non-existent endpoint)",
                    False,
                    f"Expected 404, got {response.status_code}"
                )
        except Exception as e:
            self.log_test(
                "Error handling (non-existent endpoint)",
                False,
                f"Error: {str(e)}"
            )
    
    def run_all_tests(self):
        """
        Execute all tests in sequence.
        """
        print("🧪 Starting Microbiome API tests")
        print("=" * 60)
        
        start_time = time.time()
        
        # Test 1: Verify server
        if not self.test_server_health():
            print("\n❌ Server not available. Aborting tests.")
            return False
        
        # Wait a bit for data to load
        print("\n⏳ Waiting for data to load...")
        time.sleep(2)
        
        # Test 2: Main endpoint
        home_data = self.test_home_endpoint()
        
        # Test 3: Environment list
        environments = self.test_environments_endpoint()
        
        # Test 4: Specific composition
        self.test_composition_endpoint(environments)
        
        # Test 5: Statistics
        self.test_stats_endpoint()
        
        # Test 6: Error handling
        self.test_error_handling()
        
        # Summary
        end_time = time.time()
        duration = round(end_time - start_time, 2)
        
        successful_tests = sum(1 for result in self.test_results if result['success'])
        total_tests = len(self.test_results)
        
        print("\n" + "=" * 60)
        print("📋 TEST SUMMARY")
        print(f"✅ Successful tests: {successful_tests}/{total_tests}")
        print(f"⏱️  Total time: {duration} seconds")
        
        if successful_tests == total_tests:
            print("🎉 All tests passed! API is working correctly.")
            return True
        else:
            print("⚠️  Some tests failed. Check details above.")
            return False
    
    def save_results(self, filename="test_results.json"):
        """
        Save results to JSON file.
        """
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.test_results, f, indent=2, ensure_ascii=False)
            print(f"📄 Results saved to: {filename}")
        except Exception as e:
            print(f"❌ Error saving results: {e}")


def main():
    """
    Main function to run tests.
    """
    # Check arguments
    base_url = "http://localhost:5000"
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    
    print(f"🔗 Testing API at: {base_url}")
    
    # Create tester and run
    tester = MicrobiomeAPITester(base_url)
    success = tester.run_all_tests()
    
    # Save results
    tester.save_results()
    
    # Exit code for scripts
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()