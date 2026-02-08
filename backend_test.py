#!/usr/bin/env python3
"""
Backend API Test Suite for Cotizador DTG
Tests all backend endpoints comprehensively
"""

import requests
import json
import os
from datetime import datetime

# Test configuration
BASE_URL = "https://mcc-query-tool.preview.emergentagent.com/api"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "206141"

class BackendTester:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.test_results = []
        
    def log_result(self, test_name, passed, details=""):
        """Log test result"""
        status = "PASS" if passed else "FAIL"
        result = {
            "test": test_name,
            "status": status,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        print(f"[{status}] {test_name}: {details}")
        
    def test_health_check(self):
        """Test GET /api/health endpoint"""
        try:
            response = self.session.get(f"{BASE_URL}/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if "status" in data and data["status"] == "healthy":
                    self.log_result("Health Check", True, f"Service healthy, status: {data['status']}")
                    return True
                else:
                    self.log_result("Health Check", False, f"Invalid response format: {data}")
                    return False
            else:
                self.log_result("Health Check", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_result("Health Check", False, f"Connection error: {str(e)}")
            return False
    
    def test_login_valid_credentials(self):
        """Test POST /api/auth/login with valid credentials"""
        try:
            payload = {
                "username": ADMIN_USERNAME,
                "password": ADMIN_PASSWORD
            }
            response = self.session.post(f"{BASE_URL}/auth/login", json=payload, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if "access_token" in data and "token_type" in data:
                    self.auth_token = data["access_token"]
                    self.log_result("Login Valid Credentials", True, f"Token received, type: {data['token_type']}")
                    return True
                else:
                    self.log_result("Login Valid Credentials", False, f"Missing token fields: {data}")
                    return False
            else:
                self.log_result("Login Valid Credentials", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_result("Login Valid Credentials", False, f"Request error: {str(e)}")
            return False
    
    def test_login_invalid_credentials(self):
        """Test POST /api/auth/login with invalid credentials"""
        try:
            payload = {
                "username": "admin",
                "password": "wrongpassword"
            }
            response = self.session.post(f"{BASE_URL}/auth/login", json=payload, timeout=10)
            
            if response.status_code == 401:
                self.log_result("Login Invalid Credentials", True, "Correctly rejected invalid credentials")
                return True
            else:
                self.log_result("Login Invalid Credentials", False, f"Expected 401, got HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_result("Login Invalid Credentials", False, f"Request error: {str(e)}")
            return False
    
    def test_login_missing_fields(self):
        """Test POST /api/auth/login with missing fields"""
        try:
            payload = {"username": "admin"}  # Missing password
            response = self.session.post(f"{BASE_URL}/auth/login", json=payload, timeout=10)
            
            if response.status_code in [400, 422]:  # Bad request or validation error
                self.log_result("Login Missing Fields", True, f"Correctly rejected incomplete data (HTTP {response.status_code})")
                return True
            else:
                self.log_result("Login Missing Fields", False, f"Expected 400/422, got HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_result("Login Missing Fields", False, f"Request error: {str(e)}")
            return False
    
    def test_get_sheet_config(self):
        """Test GET /api/config/sheets (public endpoint)"""
        try:
            response = self.session.get(f"{BASE_URL}/config/sheets", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ["comision_especial_url", "comisiones_por_giro_url"]
                
                if all(field in data for field in required_fields):
                    self.log_result("Get Sheet Config", True, f"Config retrieved with required fields")
                    return True
                else:
                    missing = [f for f in required_fields if f not in data]
                    self.log_result("Get Sheet Config", False, f"Missing fields: {missing}")
                    return False
            else:
                self.log_result("Get Sheet Config", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_result("Get Sheet Config", False, f"Request error: {str(e)}")
            return False
    
    def test_update_sheet_config_without_auth(self):
        """Test PUT /api/config/sheets without authentication"""
        try:
            payload = {
                "comision_especial_url": "https://example.com/sheet1",
                "comisiones_por_giro_url": "https://example.com/sheet2"
            }
            response = self.session.put(f"{BASE_URL}/config/sheets", json=payload, timeout=10)
            
            if response.status_code == 401:
                self.log_result("Update Sheet Config No Auth", True, "Correctly requires authentication")
                return True
            else:
                self.log_result("Update Sheet Config No Auth", False, f"Expected 401, got HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_result("Update Sheet Config No Auth", False, f"Request error: {str(e)}")
            return False
    
    def test_update_sheet_config_with_auth(self):
        """Test PUT /api/config/sheets with authentication"""
        if not self.auth_token:
            self.log_result("Update Sheet Config With Auth", False, "No auth token available")
            return False
        
        try:
            payload = {
                "comision_especial_url": "https://docs.google.com/spreadsheets/d/test1/edit?gid=123",
                "comisiones_por_giro_url": "https://docs.google.com/spreadsheets/d/test2/edit?gid=456"
            }
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            response = self.session.put(f"{BASE_URL}/config/sheets", json=payload, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("comision_especial_url") == payload["comision_especial_url"]:
                    self.log_result("Update Sheet Config With Auth", True, "Config updated successfully")
                    return True
                else:
                    self.log_result("Update Sheet Config With Auth", False, f"Config not updated properly: {data}")
                    return False
            else:
                self.log_result("Update Sheet Config With Auth", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_result("Update Sheet Config With Auth", False, f"Request error: {str(e)}")
            return False
    
    def test_sync_without_auth(self):
        """Test POST /api/sync without authentication"""
        try:
            response = self.session.post(f"{BASE_URL}/sync", timeout=10)
            
            if response.status_code == 401:
                self.log_result("Sync No Auth", True, "Correctly requires authentication")
                return True
            else:
                self.log_result("Sync No Auth", False, f"Expected 401, got HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_result("Sync No Auth", False, f"Request error: {str(e)}")
            return False
    
    def test_sync_with_auth(self):
        """Test POST /api/sync with authentication"""
        if not self.auth_token:
            self.log_result("Sync With Auth", False, "No auth token available")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            response = self.session.post(f"{BASE_URL}/sync", headers=headers, timeout=30)  # Longer timeout for sync
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ["success", "message", "records_synced", "last_sync"]
                
                if all(field in data for field in required_fields) and data["success"]:
                    self.log_result("Sync With Auth", True, f"Sync successful, {data['records_synced']} records")
                    return True
                else:
                    self.log_result("Sync With Auth", False, f"Sync failed or invalid response: {data}")
                    return False
            else:
                self.log_result("Sync With Auth", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_result("Sync With Auth", False, f"Request error: {str(e)}")
            return False
    
    def test_search_existing_ciu(self):
        """Test GET /api/search/{ciu} with existing CIU"""
        try:
            # Test with CIU 5411 as mentioned in the review request
            response = self.session.get(f"{BASE_URL}/search/5411", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ["ciu", "grupo", "subgrupo", "debito_campal", "credito_campal", 
                                 "debito_dinamica", "credito_dinamica", "debito_pizarra", "credito_pizarra"]
                
                if "ciu" in data and data["ciu"] == "5411":
                    missing_fields = [f for f in required_fields if f not in data]
                    if not missing_fields:
                        self.log_result("Search Existing CIU", True, f"CIU 5411 found with all fields")
                        return True
                    else:
                        self.log_result("Search Existing CIU", False, f"Missing fields: {missing_fields}")
                        return False
                else:
                    self.log_result("Search Existing CIU", False, f"Incorrect CIU returned: {data.get('ciu')}")
                    return False
            else:
                self.log_result("Search Existing CIU", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_result("Search Existing CIU", False, f"Request error: {str(e)}")
            return False
    
    def test_search_nonexistent_ciu(self):
        """Test GET /api/search/{ciu} with non-existent CIU"""
        try:
            # Use a CIU that shouldn't exist
            response = self.session.get(f"{BASE_URL}/search/9999", timeout=10)
            
            if response.status_code == 404:
                self.log_result("Search Non-existent CIU", True, "Correctly returned 404 for non-existent CIU")
                return True
            else:
                self.log_result("Search Non-existent CIU", False, f"Expected 404, got HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_result("Search Non-existent CIU", False, f"Request error: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all backend tests"""
        print("="*60)
        print("STARTING COTIZADOR DTG BACKEND API TESTS")
        print(f"Base URL: {BASE_URL}")
        print("="*60)
        
        # Test order matters - login must succeed first for authenticated tests
        test_methods = [
            self.test_health_check,
            self.test_login_valid_credentials,
            self.test_login_invalid_credentials,
            self.test_login_missing_fields,
            self.test_get_sheet_config,
            self.test_update_sheet_config_without_auth,
            self.test_update_sheet_config_with_auth,
            self.test_sync_without_auth,
            self.test_sync_with_auth,
            self.test_search_existing_ciu,
            self.test_search_nonexistent_ciu
        ]
        
        for test_method in test_methods:
            try:
                test_method()
            except Exception as e:
                self.log_result(test_method.__name__, False, f"Test execution error: {str(e)}")
        
        # Summary
        print("\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60)
        
        passed = sum(1 for result in self.test_results if result["status"] == "PASS")
        failed = sum(1 for result in self.test_results if result["status"] == "FAIL")
        total = len(self.test_results)
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        print(f"Success Rate: {passed/total*100:.1f}%")
        
        if failed > 0:
            print("\nFAILED TESTS:")
            for result in self.test_results:
                if result["status"] == "FAIL":
                    print(f"  - {result['test']}: {result['details']}")
        
        return passed, failed, self.test_results


if __name__ == "__main__":
    tester = BackendTester()
    passed, failed, results = tester.run_all_tests()
    
    # Exit with error code if any tests failed
    exit(1 if failed > 0 else 0)