#!/usr/bin/env python3
"""
Additional tests to verify sync functionality with real sheet URLs
"""

import requests
import json

BASE_URL = "https://tasa-lookup.preview.emergentagent.com/api"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "206141"

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

def test_current_config():
    """Check current sheet configuration"""
    print("=== Current Sheet Configuration ===")
    response = requests.get(f"{BASE_URL}/config/sheets", timeout=10)
    if response.status_code == 200:
        config = response.json()
        print("Comisión especial URL:", config.get("comision_especial_url"))
        print("Comisiones por giro URL:", config.get("comisiones_por_giro_url"))
        print("Last sync:", config.get("last_sync"))
        return config
    else:
        print(f"Error getting config: {response.status_code} - {response.text}")
        return None

def test_sync_with_real_urls():
    """Test sync with the real/current URLs"""
    print("\n=== Testing Sync with Current URLs ===")
    
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

def test_search_after_sync():
    """Test search functionality after sync"""
    print("\n=== Testing Search After Sync ===")
    
    # Test multiple CIUs
    test_cius = ["5411", "7999", "1234"]
    
    for ciu in test_cius:
        response = requests.get(f"{BASE_URL}/search/{ciu}", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"CIU {ciu}: Found - Grupo: {data.get('grupo')}, Subgrupo: {data.get('subgrupo')}")
        elif response.status_code == 404:
            print(f"CIU {ciu}: Not found (404)")
        else:
            print(f"CIU {ciu}: Error {response.status_code} - {response.text}")

if __name__ == "__main__":
    config = test_current_config()
    if config:
        sync_success = test_sync_with_real_urls()
        if sync_success:
            test_search_after_sync()