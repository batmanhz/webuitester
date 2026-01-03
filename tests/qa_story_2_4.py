import requests
import json
import sys

BASE_URL = "http://127.0.0.1:19000/api"

def log(msg, status="INFO"):
    print(f"[{status}] {msg}")

def test_get_config():
    log("Testing GET /config...")
    try:
        resp = requests.get(f"{BASE_URL}/config")
        if resp.status_code == 200:
            data = resp.json()
            log(f"GET /config success. Keys: {list(data.keys())}", "PASS")
            return data
        else:
            log(f"GET /config failed: {resp.status_code} {resp.text}", "FAIL")
            return None
    except Exception as e:
        log(f"GET /config exception: {e}", "FAIL")
        return None

def test_update_config(original_config):
    log("Testing PUT /config...")
    
    # Modify temperature and headless
    new_config = original_config.copy()
    new_config['temperature'] = 0.7
    new_config['headless'] = not original_config.get('headless', False)
    new_config['thinking'] = not original_config.get('thinking', False)
    
    try:
        resp = requests.put(f"{BASE_URL}/config", json=new_config)
        if resp.status_code == 200:
            log("PUT /config success", "PASS")
            
            # Verify changes
            updated_config = test_get_config()
            
            if updated_config['temperature'] == 0.7:
                log("Temperature update verified", "PASS")
            else:
                log(f"Temperature update failed. Got {updated_config['temperature']}", "FAIL")
                
            if updated_config['headless'] == new_config['headless']:
                log("Headless update verified", "PASS")
            else:
                log(f"Headless update failed. Got {updated_config['headless']}", "FAIL")

            return True
        else:
            log(f"PUT /config failed: {resp.status_code} {resp.text}", "FAIL")
            return False
            
    except Exception as e:
        log(f"PUT /config exception: {e}", "FAIL")
        return False

def cleanup(original_config):
    log("Restoring original config...")
    try:
        requests.put(f"{BASE_URL}/config", json=original_config)
        log("Config restored", "INFO")
    except Exception as e:
        log(f"Failed to restore config: {e}", "WARN")

def main():
    log("Starting QA Validation for Story 2.4 - Settings Configuration")
    
    original_config = test_get_config()
    if not original_config:
        sys.exit(1)
        
    success = test_update_config(original_config)
    
    cleanup(original_config)
    
    if success:
        log("Story 2.4 Validation PASSED", "SUCCESS")
        sys.exit(0)
    else:
        log("Story 2.4 Validation FAILED", "FAIL")
        sys.exit(1)

if __name__ == "__main__":
    main()
