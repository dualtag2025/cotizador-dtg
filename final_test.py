#!/usr/bin/env python3
"""
Final comprehensive backend test with corrected URLs
"""

import requests
import json

BASE_URL = "https://mcc-query-tool.preview.emergentagent.com/api"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "206141"

def final_endpoint_test():
    """Run a final test of all endpoints"""
    print("="*60)
    print("FINAL COMPREHENSIVE BACKEND API TEST")
    print("="*60)
    
    results = {
        "passed": 0,
        "failed": 0,
        "tests": []
    }
    
    def log_test(name, passed, details=""):
        status = "PASS" if passed else "FAIL"
        results["tests"].append({"name": name, "status": status, "details": details})
        if passed:
            results["passed"] += 1
        else:
            results["failed"] += 1
        print(f"[{status}] {name}: {details}")
    
    # 1. Health Check
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=10)
        log_test("Health Check", response.status_code == 200, f"Status: {response.status_code}")
    except Exception as e:
        log_test("Health Check", False, f"Error: {str(e)}")
    
    # 2. Login with valid credentials
    auth_token = None
    try:
        payload = {"username": ADMIN_USERNAME, "password": ADMIN_PASSWORD}
        response = requests.post(f"{BASE_URL}/auth/login", json=payload, timeout=10)
        if response.status_code == 200:
            data = response.json()
            auth_token = data.get("access_token")
            log_test("Admin Login", True, "Token received")
        else:
            log_test("Admin Login", False, f"HTTP {response.status_code}")
    except Exception as e:
        log_test("Admin Login", False, f"Error: {str(e)}")
    
    # 3. Login with invalid credentials
    try:
        payload = {"username": "admin", "password": "wrong"}
        response = requests.post(f"{BASE_URL}/auth/login", json=payload, timeout=10)
        log_test("Invalid Login Rejection", response.status_code == 401, f"Status: {response.status_code}")
    except Exception as e:
        log_test("Invalid Login Rejection", False, f"Error: {str(e)}")
    
    # 4. Get sheet configuration
    try:
        response = requests.get(f"{BASE_URL}/config/sheets", timeout=10)
        if response.status_code == 200:
            config = response.json()
            has_urls = "comision_especial_url" in config and "comisiones_por_giro_url" in config
            log_test("Get Sheet Config", has_urls, "URLs present" if has_urls else "Missing URLs")
        else:
            log_test("Get Sheet Config", False, f"HTTP {response.status_code}")
    except Exception as e:
        log_test("Get Sheet Config", False, f"Error: {str(e)}")
    
    # 5. Update sheet config (requires auth)
    if auth_token:
        try:
            headers = {"Authorization": f"Bearer {auth_token}"}
            # Use the correct original URLs
            payload = {
                "comision_especial_url": "https://docs.google.com/spreadsheets/d/1El9bDW28oNVvbc1rxI7xIgA8oSlMjbbviHHz2r6kJ1A/edit?gid=505615848#gid=505615848",
                "comisiones_por_giro_url": "https://docs.google.com/spreadsheets/d/11lN-AjTmgKrriRHbnyyZ6gewlSvgVcVgx5kQh54nqps/edit?gid=820797387#gid=820797387"
            }
            response = requests.put(f"{BASE_URL}/config/sheets", json=payload, headers=headers, timeout=10)
            log_test("Update Sheet Config", response.status_code == 200, f"Status: {response.status_code}")
        except Exception as e:
            log_test("Update Sheet Config", False, f"Error: {str(e)}")
    else:
        log_test("Update Sheet Config", False, "No auth token")
    
    # 6. Sync Google Sheets (requires auth)
    if auth_token:
        try:
            headers = {"Authorization": f"Bearer {auth_token}"}
            response = requests.post(f"{BASE_URL}/sync", headers=headers, timeout=45)
            if response.status_code == 200:
                data = response.json()
                success = data.get("success", False)
                records = data.get("records_synced", 0)
                log_test("Google Sheets Sync", success and records > 0, f"Synced {records} records")
            else:
                log_test("Google Sheets Sync", False, f"HTTP {response.status_code}")
        except Exception as e:
            log_test("Google Sheets Sync", False, f"Error: {str(e)}")
    else:
        log_test("Google Sheets Sync", False, "No auth token")
    
    # 7. Search existing CIU
    try:
        response = requests.get(f"{BASE_URL}/search/5411", timeout=10)
        if response.status_code == 200:
            data = response.json()
            has_all_fields = all(field in data for field in ["ciu", "grupo", "subgrupo", "debito_campal", "credito_campal", "debito_dinamica", "credito_dinamica", "debito_pizarra", "credito_pizarra"])
            log_test("Search Existing CIU", has_all_fields, f"CIU 5411 - All fields present")
        else:
            log_test("Search Existing CIU", False, f"HTTP {response.status_code}")
    except Exception as e:
        log_test("Search Existing CIU", False, f"Error: {str(e)}")
    
    # 8. Search non-existent CIU
    try:
        response = requests.get(f"{BASE_URL}/search/9999999", timeout=10)
        log_test("Search Non-existent CIU", response.status_code == 404, f"Status: {response.status_code}")
    except Exception as e:
        log_test("Search Non-existent CIU", False, f"Error: {str(e)}")
    
    # 9. Test authentication requirement for protected endpoints
    try:
        response = requests.post(f"{BASE_URL}/sync", timeout=10)
        log_test("Sync Auth Requirement", response.status_code in [401, 403], f"Status: {response.status_code}")
    except Exception as e:
        log_test("Sync Auth Requirement", False, f"Error: {str(e)}")
    
    try:
        payload = {"comision_especial_url": "test", "comisiones_por_giro_url": "test"}
        response = requests.put(f"{BASE_URL}/config/sheets", json=payload, timeout=10)
        log_test("Config Update Auth Requirement", response.status_code in [401, 403], f"Status: {response.status_code}")
    except Exception as e:
        log_test("Config Update Auth Requirement", False, f"Error: {str(e)}")
    
    # Summary
    print("\n" + "="*60)
    print("FINAL TEST SUMMARY")
    print("="*60)
    total = results["passed"] + results["failed"]
    print(f"Total Tests: {total}")
    print(f"Passed: {results['passed']}")
    print(f"Failed: {results['failed']}")
    print(f"Success Rate: {results['passed']/total*100:.1f}%")
    
    if results["failed"] > 0:
        print("\nFAILED TESTS:")
        for test in results["tests"]:
            if test["status"] == "FAIL":
                print(f"  - {test['name']}: {test['details']}")
    
    return results

if __name__ == "__main__":
    final_endpoint_test()