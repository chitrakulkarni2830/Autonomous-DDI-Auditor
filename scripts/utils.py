import os
import json

# Define path to the cache folder and file
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE_DIR = os.path.join(BASE_DIR, "outputs")
CACHE_FILE = os.path.join(CACHE_DIR, "audit_cache.json")

def _load_cache():
    """Loads the interaction cache from disk."""
    if not os.path.exists(CACHE_DIR):
        os.makedirs(CACHE_DIR)
        
    if not os.path.exists(CACHE_FILE):
        return {}
    
    try:
        with open(CACHE_FILE, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}

def _save_cache(cache_data):
    """Saves the interaction cache to disk."""
    if not os.path.exists(CACHE_DIR):
        os.makedirs(CACHE_DIR)
        
    try:
        with open(CACHE_FILE, 'w') as f:
            json.dump(cache_data, f, indent=4)
    except IOError as e:
        print(f"Error saving cache: {e}")

def get_cached_result(drug1, drug2):
    """
    Checks if an interaction between drug1 and drug2 has already been audited.
    Returns (lit_status, chem_status) or (None, None).
    """
    # Sort names to ensure consistency (A+B is same as B+A)
    pair = tuple(sorted([drug1, drug2]))
    key = f"{pair[0]}|{pair[1]}"
    
    cache = _load_cache()
    result = cache.get(key)
    
    if result:
        return result.get('lit_status'), result.get('chem_status')
    return None, None

def save_cached_result(drug1, drug2, lit_status, chem_status):
    """
    Saves the audit result for a drug pair.
    """
    pair = tuple(sorted([drug1, drug2]))
    key = f"{pair[0]}|{pair[1]}"
    
    cache = _load_cache()
    cache[key] = {
        'lit_status': lit_status,
        'chem_status': chem_status
    }
    _save_cache(cache)
