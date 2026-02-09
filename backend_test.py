#!/usr/bin/env python3
"""
Comprehensive backend API testing for Cotizador DTG - UPDATED VERSION
Tests the new search functionality with CODE and NAME-based search
"""

import requests
import json
import sys
from datetime import datetime

# Backend URL from frontend .env
BASE_URL = "https://tasa-lookup.preview.emergentagent.com/api"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_test_header(test_name):
    print(f"\n{Colors.BLUE}{Colors.BOLD}=== {test_name} ==={Colors.ENDC}")

def print_success(message):
    print(f"{Colors.GREEN}✅ {message}{Colors.ENDC}")

def print_failure(message):
    print(f"{Colors.RED}❌ {message}{Colors.ENDC}")

def print_warning(message):
    print(f"{Colors.YELLOW}⚠️  {message}{Colors.ENDC}")

def print_info(message):
    print(f"ℹ️  {message}")

# Global variables for test state
jwt_token = None
test_results = {
    'passed': 0,
    'failed': 0,
    'total': 0
}

def run_test(test_name, test_func):
    """Run a test and track results"""
    print_test_header(test_name)
    test_results['total'] += 1
    
    try:
        success = test_func()
        if success:
            test_results['passed'] += 1
            print_success(f"{test_name} - PASSED")
        else:
            test_results['failed'] += 1
            print_failure(f"{test_name} - FAILED")
        return success
    except Exception as e:
        test_results['failed'] += 1
        print_failure(f"{test_name} - ERROR: {str(e)}")
        return False

def test_authentication():
    """Test JWT authentication endpoints"""
    global jwt_token
    
    print_info("Testing authentication with valid credentials...")
    
    # Test valid credentials
    response = requests.post(f"{BASE_URL}/auth/login", json={
        "username": "admin",
        "password": "206141"
    })
    
    if response.status_code != 200:
        print_failure(f"Login failed. Status: {response.status_code}, Response: {response.text}")
        return False
    
    data = response.json()
    if 'access_token' not in data:
        print_failure("No access token in response")
        return False
    
    jwt_token = data['access_token']
    print_success(f"Valid login successful. Token received: {jwt_token[:20]}...")
    
    # Test invalid credentials
    print_info("Testing invalid credentials...")
    response = requests.post(f"{BASE_URL}/auth/login", json={
        "username": "admin",
        "password": "wrong"
    })
    
    if response.status_code != 401:
        print_warning(f"Expected 401 for invalid credentials, got {response.status_code}")
    else:
        print_success("Invalid credentials properly rejected")
    
    # Test missing fields
    print_info("Testing missing fields...")
    response = requests.post(f"{BASE_URL}/auth/login", json={
        "username": "admin"
    })
    
    if response.status_code not in [422, 400]:
        print_warning(f"Expected 422/400 for missing fields, got {response.status_code}")
    else:
        print_success("Missing fields properly handled")
    
    return True

def test_sheet_configuration():
    """Test sheet configuration endpoints"""
    
    # Test GET endpoint (no auth required)
    print_info("Testing GET /config/sheets (public)...")
    response = requests.get(f"{BASE_URL}/config/sheets")
    
    if response.status_code != 200:
        print_failure(f"GET config failed. Status: {response.status_code}")
        return False
    
    config = response.json()
    required_fields = ['comision_especial_url', 'comisiones_por_giro_url']
    
    for field in required_fields:
        if field not in config:
            print_failure(f"Missing field '{field}' in config")
            return False
    
    print_success(f"Config retrieved: {len(config)} fields")
    print_info(f"Comision especial URL: {config['comision_especial_url'][:50]}...")
    print_info(f"Comisiones por giro URL: {config['comisiones_por_giro_url'][:50]}...")
    
    # Test PUT endpoint without auth (should fail)
    print_info("Testing PUT /config/sheets without auth...")
    response = requests.put(f"{BASE_URL}/config/sheets", json={
        "comision_especial_url": "https://test.com",
        "comisiones_por_giro_url": "https://test.com"
    })
    
    if response.status_code not in [401, 403]:
        print_warning(f"Expected 401/403 without auth, got {response.status_code}")
    else:
        print_success("Unauthorized PUT properly rejected")
    
    # Test PUT endpoint with auth (if we have token)
    if jwt_token:
        print_info("Testing PUT /config/sheets with auth...")
        headers = {"Authorization": f"Bearer {jwt_token}"}
        
        # Keep original URLs for restoration
        original_config = config.copy()
        
        response = requests.put(f"{BASE_URL}/config/sheets", 
                               json=original_config, 
                               headers=headers)
        
        if response.status_code != 200:
            print_warning(f"Authorized PUT failed: {response.status_code}")
        else:
            print_success("Authorized PUT successful")
    
    return True

def test_sync_functionality():
    """Test Google Sheets synchronization"""
    
    if not jwt_token:
        print_failure("No JWT token available for sync test")
        return False
    
    # Test sync without auth (should fail)
    print_info("Testing POST /sync without auth...")
    response = requests.post(f"{BASE_URL}/sync")
    
    if response.status_code not in [401, 403]:
        print_warning(f"Expected 401/403 without auth, got {response.status_code}")
    else:
        print_success("Unauthorized sync properly rejected")
    
    # Test sync with auth
    print_info("Testing POST /sync with auth...")
    headers = {"Authorization": f"Bearer {jwt_token}"}
    
    response = requests.post(f"{BASE_URL}/sync", headers=headers)
    
    if response.status_code != 200:
        print_failure(f"Sync failed. Status: {response.status_code}, Response: {response.text}")
        return False
    
    data = response.json()
    required_fields = ['success', 'message', 'records_synced', 'last_sync']
    
    for field in required_fields:
        if field not in data:
            print_failure(f"Missing field '{field}' in sync response")
            return False
    
    records_count = data['records_synced']
    print_success(f"Sync completed: {records_count} records")
    
    # Check if we got expected count (38 códigos + 282 nombres = 320 total)
    if records_count == 320:
        print_success(f"Expected record count achieved: {records_count}")
    else:
        print_warning(f"Expected 320 records, got {records_count}")
    
    print_info(f"Sync message: {data['message']}")
    print_info(f"Last sync: {data['last_sync']}")
    
    return True

def test_autocomplete():
    """Test autocomplete endpoint"""
    
    # Test with valid query "grifo"
    print_info('Testing autocomplete with query "grifo"...')
    response = requests.get(f"{BASE_URL}/autocomplete?q=grifo")
    
    if response.status_code != 200:
        print_failure(f"Autocomplete failed. Status: {response.status_code}")
        return False
    
    data = response.json()
    if 'suggestions' not in data:
        print_failure("No 'suggestions' field in autocomplete response")
        return False
    
    suggestions = data['suggestions']
    print_success(f"Autocomplete returned {len(suggestions)} suggestions for 'grifo'")
    
    # Check if expected suggestion is present
    expected_suggestion = "Grifos y estaciones de servicio"
    if expected_suggestion in suggestions:
        print_success(f"Expected suggestion found: {expected_suggestion}")
    else:
        print_warning(f"Expected suggestion not found. Got: {suggestions}")
    
    # Test with "tienda" query
    print_info('Testing autocomplete with query "tienda"...')
    response = requests.get(f"{BASE_URL}/autocomplete?q=tienda")
    
    if response.status_code == 200:
        data = response.json()
        tienda_suggestions = data.get('suggestions', [])
        print_success(f"Autocomplete returned {len(tienda_suggestions)} suggestions for 'tienda'")
        
        # Print first few suggestions
        for i, suggestion in enumerate(tienda_suggestions[:3]):
            print_info(f"  {i+1}. {suggestion}")
    
    # Test with 1 character (should return empty)
    print_info('Testing autocomplete with 1 character...')
    response = requests.get(f"{BASE_URL}/autocomplete?q=g")
    
    if response.status_code == 200:
        data = response.json()
        if len(data.get('suggestions', [])) == 0:
            print_success("1 character query properly returns empty")
        else:
            print_warning(f"Expected empty for 1 char, got {len(data['suggestions'])} suggestions")
    
    # Test with empty query
    print_info('Testing autocomplete with empty query...')
    response = requests.get(f"{BASE_URL}/autocomplete?q=")
    
    if response.status_code == 200:
        data = response.json()
        if len(data.get('suggestions', [])) == 0:
            print_success("Empty query properly returns empty")
        else:
            print_warning(f"Expected empty for empty query, got {len(data['suggestions'])} suggestions")
    
    return True

def test_search_by_code():
    """Test search by code functionality"""
    
    # Test with code 8510
    print_info('Testing search with code "8510"...')
    response = requests.get(f"{BASE_URL}/search/8510")
    
    if response.status_code != 200:
        print_failure(f"Search by code failed. Status: {response.status_code}, Response: {response.text}")
        return False
    
    data = response.json()
    required_fields = ['tipo', 'valor', 'debito_campal', 'credito_campal', 
                      'debito_dinamica', 'credito_dinamica', 'debito_pizarra', 'credito_pizarra']
    
    for field in required_fields:
        if field not in data:
            print_failure(f"Missing field '{field}' in search response")
            return False
    
    # Verify this is a code-type result
    if data['tipo'] != 'codigo':
        print_failure(f"Expected tipo='codigo', got '{data['tipo']}'")
        return False
    
    if data['valor'] != '8510':
        print_failure(f"Expected valor='8510', got '{data['valor']}'")
        return False
    
    # Code searches should have campal data, but null dinamica/pizarra
    campal_fields_present = data['debito_campal'] is not None or data['credito_campal'] is not None
    dinamica_pizarra_null = (data['debito_dinamica'] is None and data['credito_dinamica'] is None and 
                            data['debito_pizarra'] is None and data['credito_pizarra'] is None)
    
    if not campal_fields_present:
        print_warning("No campal data present for code search")
    else:
        print_success("Campal data present for code search")
    
    if not dinamica_pizarra_null:
        print_warning("Dinamica/Pizarra data should be null for code search")
    else:
        print_success("Dinamica/Pizarra properly null for code search")
    
    print_success(f"Code search successful: {data['valor']}")
    print_info(f"Débito campal: {data['debito_campal']}")
    print_info(f"Crédito campal: {data['credito_campal']}")
    
    return True

def test_search_by_name():
    """Test search by business name functionality"""
    
    # Test with "Grifos y estaciones de servicio"
    business_name = "Grifos y estaciones de servicio"
    print_info(f'Testing search with name "{business_name}"...')
    
    response = requests.get(f"{BASE_URL}/search/{business_name}")
    
    if response.status_code != 200:
        print_failure(f"Search by name failed. Status: {response.status_code}, Response: {response.text}")
        return False
    
    data = response.json()
    required_fields = ['tipo', 'valor', 'debito_campal', 'credito_campal', 
                      'debito_dinamica', 'credito_dinamica', 'debito_pizarra', 'credito_pizarra']
    
    for field in required_fields:
        if field not in data:
            print_failure(f"Missing field '{field}' in search response")
            return False
    
    # Verify this is a name-type result
    if data['tipo'] != 'nombre':
        print_failure(f"Expected tipo='nombre', got '{data['tipo']}'")
        return False
    
    if data['valor'] != business_name:
        print_failure(f"Expected valor='{business_name}', got '{data['valor']}'")
        return False
    
    # Name searches should have dinamica/pizarra data, but null campal
    dinamica_pizarra_present = (data['debito_dinamica'] is not None or data['credito_dinamica'] is not None or
                               data['debito_pizarra'] is not None or data['credito_pizarra'] is not None)
    campal_null = data['debito_campal'] is None and data['credito_campal'] is None
    
    if not dinamica_pizarra_present:
        print_warning("No dinamica/pizarra data present for name search")
    else:
        print_success("Dinamica/Pizarra data present for name search")
    
    if not campal_null:
        print_warning("Campal data should be null for name search")
    else:
        print_success("Campal properly null for name search")
    
    print_success(f"Name search successful: {data['valor']}")
    print_info(f"Débito dinámica: {data['debito_dinamica']}")
    print_info(f"Crédito dinámica: {data['credito_dinamica']}")
    print_info(f"Débito pizarra: {data['debito_pizarra']}")
    print_info(f"Crédito pizarra: {data['credito_pizarra']}")
    
    return True

def test_search_not_found():
    """Test search with non-existent data"""
    
    # Test with non-existent code
    print_info('Testing search with non-existent code "9999999"...')
    response = requests.get(f"{BASE_URL}/search/9999999")
    
    if response.status_code != 404:
        print_failure(f"Expected 404 for non-existent code, got {response.status_code}")
        return False
    
    print_success("Non-existent code properly returns 404")
    
    # Test with non-existent name
    print_info('Testing search with non-existent name "Non-existent Business"...')
    response = requests.get(f"{BASE_URL}/search/Non-existent Business")
    
    if response.status_code != 404:
        print_failure(f"Expected 404 for non-existent name, got {response.status_code}")
        return False
    
    print_success("Non-existent name properly returns 404")
    
    return True

def test_health_check():
    """Test health check endpoint"""
    
    print_info("Testing GET /health...")
    response = requests.get(f"{BASE_URL}/health")
    
    if response.status_code != 200:
        print_failure(f"Health check failed. Status: {response.status_code}")
        return False
    
    data = response.json()
    required_fields = ['status', 'timestamp']
    
    for field in required_fields:
        if field not in data:
            print_failure(f"Missing field '{field}' in health response")
            return False
    
    if data['status'] != 'healthy':
        print_failure(f"Expected status='healthy', got '{data['status']}'")
        return False
    
    print_success(f"Health check passed: {data['status']}")
    print_info(f"Timestamp: {data['timestamp']}")
    
    return True

def main():
    """Main test execution"""
    print(f"{Colors.BOLD}🚀 Starting Cotizador DTG Backend API Tests (UPDATED VERSION){Colors.ENDC}")
    print(f"Backend URL: {BASE_URL}")
    print(f"Test started: {datetime.now()}")
    
    # Run all tests in sequence
    tests = [
        ("JWT Authentication", test_authentication),
        ("Sheet Configuration", test_sheet_configuration), 
        ("Google Sheets Sync", test_sync_functionality),
        ("Autocomplete Search", test_autocomplete),
        ("Search by Code", test_search_by_code),
        ("Search by Name", test_search_by_name),
        ("Search Not Found", test_search_not_found),
        ("Health Check", test_health_check)
    ]
    
    for test_name, test_func in tests:
        run_test(test_name, test_func)
    
    # Print final results
    print(f"\n{Colors.BOLD}📊 TEST RESULTS SUMMARY{Colors.ENDC}")
    print(f"Total tests: {test_results['total']}")
    print(f"{Colors.GREEN}Passed: {test_results['passed']}{Colors.ENDC}")
    print(f"{Colors.RED}Failed: {test_results['failed']}{Colors.ENDC}")
    
    success_rate = (test_results['passed'] / test_results['total']) * 100 if test_results['total'] > 0 else 0
    print(f"Success rate: {success_rate:.1f}%")
    
    if test_results['failed'] == 0:
        print(f"{Colors.GREEN}{Colors.BOLD}🎉 ALL TESTS PASSED!{Colors.ENDC}")
        return 0
    else:
        print(f"{Colors.RED}{Colors.BOLD}❌ SOME TESTS FAILED{Colors.ENDC}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)