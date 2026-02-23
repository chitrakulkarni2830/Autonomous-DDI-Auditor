import requests
import time
import utils

# ==========================================
# LITERATURE AGENT
# ==========================================
# Role: Search scientific literature (PubMed/NCBI) for known interactions
# between pairs of drugs.
# ==========================================

# Base URL for NCBI E-utilities API (Public & Free)
BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"

def check_drug_interaction(drug1, drug2):
    """
    Queries PubMed to see if there are papers mentioning both drugs and 'interaction'.
    
    Args:
        drug1 (str): Name of first drug.
        drug2 (str): Name of second drug.
        
    Returns:
        str: A status message ("Known Risk", "Potential Risk", or "No obvious flag")
    """
    
    # Check cache first
    lit_res, _ = utils.get_cached_result(drug1, drug2)
    if lit_res:
        print(f"[Literature Agent] Using cached result for {drug1} + {drug2}")
        return lit_res

    # 1. Construct the search query
    # We look for: Drug1 AND Drug2 AND "Drug Interactions" matches in the title or abstract.
    query = f"{drug1}[Title/Abstract] AND {drug2}[Title/Abstract] AND Drug Interactions[MeSH]"
    
    params = {
        "db": "pubmed",       # Database to search
        "term": query,        # Our search term
        "retmode": "json",    # Return format
        "retmax": 5           # We only need to know if hits exist, not get all of them
    }
    
    print(f"[Literature Agent] Checking PubMed for: {drug1} + {drug2}...")
    
    try:
        # 2. Make the API Call
        response = requests.get(BASE_URL, params=params)
        
        if response.status_code == 200:
            data = response.json()
            
            # 'count' tells us how many papers matched the query
            count = int(data["esearchresult"]["count"])
            
            if count > 5:
                # Many papers found -> High probability of known interaction
                # SIMULATED LLM SUMMARY INTERVENTION
                summary = generate_simulated_llm_summary(drug1, drug2)
                result = f"⚠️ KNOWN RISK ({count} citations) - 🤖 LLM Summary: {summary}"
            elif count > 0:
                # A few papers - might be rare or emerging
                result = f"⚠️ POTENTIAL RISK ({count} citations) - Needs review."
            else:
                result = "✅ No obvious flag in literature."
            
            utils.save_cached_result(drug1, drug2, result, None)
            return result
        else:
            return "❌ API Error"
            
    except Exception as e:
        return f"Error connecting to NCBI: {e}"
        
    finally:
        # Be polite to the API server!
        # NCBI limits requests without API keys to 3 per second.
        time.sleep(0.5) 

def generate_simulated_llm_summary(drug1, drug2):
    """
    A portfolio-friendly 'simulator' that acts like an LLM (e.g., Gemini) processing
    the abstracts returned by PubMed. Instead of requiring the user to have an active
    API key, this returns realistic, context-aware clinical summaries based on known
    drug classes and interactions.
    """
    
    # Common interaction patterns
    d1_lower = drug1.lower()
    d2_lower = drug2.lower()
    
    # Blood pressure / Heart
    if ("amlodipine" in [d1_lower, d2_lower] or "losartan" in [d1_lower, d2_lower] or "lisinopril" in [d1_lower, d2_lower]):
        if ("furosemide" in [d1_lower, d2_lower] or "spironolactone" in [d1_lower, d2_lower]):
            return "Potential for severe hypotension and electrolyte imbalance (potassium fluctuation)."
    
    # Pain / NSAIDs combined with bleeding risks or kidney issues
    if ("aspirin" in [d1_lower, d2_lower] or "clopidogrel" in [d1_lower, d2_lower]):
        if ("ibuprofen" in [d1_lower, d2_lower] or "meloxicam" in [d1_lower, d2_lower] or "diclofenac" in [d1_lower, d2_lower] or "naproxen" in [d1_lower, d2_lower]):
            return "High risk of gastrointestinal bleeding; concurrent use diminishes antiplatelet efficacy of Aspirin."
            
    # Diabetes / Hypoglycemia
    if ("insulin" in [d1_lower, d2_lower] or "glipizide" in [d1_lower, d2_lower] or "metformin" in [d1_lower, d2_lower]):
        if ("carvedilol" in [d1_lower, d2_lower]):
            return "Beta-blocker masks symptoms of hypoglycemia (tachycardia); blood glucose monitoring required."
    
    # Antacids / Absorption
    if ("omeprazole" in [d1_lower, d2_lower] or "pantoprazole" in [d1_lower, d2_lower]):
         if ("clopidogrel" in [d1_lower, d2_lower]):
             return "PPI inhibits CYP2C19, significantly reducing the cardiovascular efficacy of Clopidogrel."
             
    # Neurology (Seizures/Nerve Pain)
    if ("valproate" in [d1_lower, d2_lower] or "carbamazepine" in [d1_lower, d2_lower]):
        return "Hepatic enzyme induction/inhibition affecting metabolism; requires dose titration and LFT monitoring."

    # Default fallback for unmapped but flagged interactions
    return "Increased risk of adverse pharmacological synergy. Monitor patient for combined side-effect profile." 

# Simple test block
if __name__ == "__main__":
    # Test a known interaction (e.g., Warfarin and Aspirin - bleeding risk)
    # Note: Using random drugs from our list for the test demo
    result = check_drug_interaction("Aspirin", "Warfarin")
    print(f"Result: {result}")
