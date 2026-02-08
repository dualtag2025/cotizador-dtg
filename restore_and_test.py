#!/usr/bin/env python3
"""
Restore original sheet URLs and test sync functionality
"""

import requests
import json

BASE_URL = "https://mcc-query-tool.preview.emergentagent.com/api"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "206141"

# Original URLs from the code
ORIGINAL_URLS = {
    "comision_especial_url": "https://docs.google.com/spreadsheets/d/1El9bDW28oNVvbc1rxI7xIgA8oSlMjbbviHHz2r6kJ1A/edit?gid=505615848#gid=505615848",
    "comisiones_por_giro_url": "https://docs.google.com/spreadsheets/d/11lN-AjTmgKrriRHbnyyZ6gewlSvgVcVgx5kQh54nqps/edit?gid=820797387#gid=820797387"
}

def get_auth_token():
    """Get authentication token"""
    payload = {
        "username": ADMIN_USERNAME,
        "password": ADMIN_PASSWORD
    }
    response = requests.post(f"{BASE_URL}/auth/login", json=payload, timeout=10)
    if response.status_code == 200:
        return response.json()["access_token"]
    return None

def restore_original_urls():
    """Restore original sheet URLs"""
    print("=== Restoring Original Sheet URLs ===")
    
    token = get_auth_token()
    if not token:
        print("Failed to get auth token")
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.put(f"{BASE_URL}/config/sheets", json=ORIGINAL_URLS, headers=headers, timeout=10)
    
    if response.status_code == 200:
        print("Original URLs restored successfully")
        return True
    else:
        print(f"Failed to restore URLs: {response.status_code} - {response.text}")
        return False

def test_sync_with_original_urls():
    """Test sync with the original URLs"""
    print("\n=== Testing Sync with Original URLs ===")
    
    token = get_auth_token()
    if not token:
        print("Failed to get auth token")
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(f"{BASE_URL}/sync", headers=headers, timeout=45)
    
    print(f"Sync response status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Success: {data.get('success')}")
        print(f"Message: {data.get('message')}")
        print(f"Records synced: {data.get('records_synced')}")
        print(f"Last sync: {data.get('last_sync')}")
        return True
    else:
        print(f"Sync failed: {response.text}")
        return False

def test_comprehensive_search():
    """Test search with multiple CIUs to verify data quality"""
    print("\n=== Comprehensive Search Test ===")
    
    # Test CIUs that should exist based on the review request
    test_cius = ["5411", "7999", "1234", "0000"]
    found_count = 0
    
    for ciu in test_cius:
        response = requests.get(f"{BASE_URL}/search/{ciu}", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✓ CIU {ciu}: Found")
            print(f"  - Grupo: {data.get('grupo')}")
            print(f"  - Subgrupo: {data.get('subgrupo')}")
            print(f"  - Débito Campal: {data.get('debito_campal')}")
            print(f"  - Crédito Campal: {data.get('credito_campal')}")
            print(f"  - Débito Dinámica: {data.get('debito_dinamica')}")
            print(f"  - Crédito Dinámica: {data.get('credito_dinamica')}")
            print(f"  - Débito Pizarra: {data.get('debito_pizarra')}")
            print(f"  - Crédito Pizarra: {data.get('credito_pizarra')}")
            found_count += 1
        elif response.status_code == 404:
            print(f"✗ CIU {ciu}: Not found")
        else:
            print(f"✗ CIU {ciu}: Error {response.status_code} - {response.text}")
    
    print(f"\nFound {found_count} out of {len(test_cius)} test CIUs")
    return found_count

if __name__ == "__main__":
    # Restore original URLs
    if restore_original_urls():
        # Test sync with original URLs
        if test_sync_with_original_urls():
            # Test search functionality
            test_comprehensive_search()
        else:
            print("Sync failed, skipping search tests")
    else:
        print("Failed to restore URLs, cannot proceed with tests")