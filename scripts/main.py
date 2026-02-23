import database_agent
import literature_agent
import biochem_agent
import itertools
import sqlite3
import utils

# ==========================================
# MAIN ORCHESTRATOR
# ==========================================
# This script coordinates the team of agents to perform the audit.
# ==========================================

def main():
    print("="*50)
    print("🏥  AUTONOMOUS DDI AUDITOR STARTED")
    print("="*50)
    
    # --- STEP 1: Database Agent ---
    print("\n🔍 STEP 1: Identifying At-Risk Patients (Database Agent)")
    at_risk_patients = database_agent.get_at_risk_patients()
    
    if not at_risk_patients:
        print("No high-risk patients found.")
        return

    # Process ALL patients found
    total_patients = len(at_risk_patients)
    print(f"\nProcessing all {total_patients} patients. Saving results to 'audit_results.db'...\n")
    
    # Connect to Audit Database (Creates it if it doesn't exist) in 'outputs/'
    import os
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    AUDIT_DB_PATH = os.path.join(BASE_DIR, "outputs", "audit_results.db")
    
    audit_conn = sqlite3.connect(AUDIT_DB_PATH)
    audit_cursor = audit_conn.cursor()
    
    # --- OPTIMIZATION: Identify unique drug pairs across all patients ---
    all_drug_pairs = set()
    for patient in at_risk_patients:
        drugs = patient['medications']
        drug_pairs = list(itertools.combinations(drugs, 2))
        for d1, d2 in drug_pairs:
            # Sort names to treat (A, B) and (B, A) as the same pair
            pair = tuple(sorted([d1, d2]))
            all_drug_pairs.add(pair)
            
    total_pairs = len(all_drug_pairs)
    print(f"Total unique drug pairs to audit: {total_pairs}")
    
    # Audit unique pairs first (leveraging cache)
    for i, (d1, d2) in enumerate(all_drug_pairs):
        print(f"Auditing unique pair [{i+1}/{total_pairs}]: {d1} + {d2}")
        literature_agent.check_drug_interaction(d1, d2)
        
        biologicals = ["Insulin", "Monoclonal", "Vaccine"]
        if not any(bio in d1 or bio in d2 for bio in biologicals):
            biochem_agent.analyze_structure_risk(d1, d2)

    cleared_tables = set()

    # Now populate the database using cached results
    for i, patient in enumerate(at_risk_patients):
        print(f"[{i+1}/{total_patients}] Recording results for {patient['name']}...")
        
        # Format department name for SQL table (e.g., General Medicine -> General_Medicine)
        table_name = patient['department'].replace(" ", "_").replace("-", "_")
        
        if table_name not in cleared_tables:
            # Clear old data to avoid duplicates
            audit_cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
            audit_cursor.execute(f'''
                CREATE TABLE {table_name} (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    patient_name TEXT,
                    age INTEGER,
                    diagnosis TEXT,
                    medication_list TEXT,
                    drug_1 TEXT,
                    drug_2 TEXT,
                    literature_risk TEXT,
                    biochem_risk TEXT
                )
            ''')
            cleared_tables.add(table_name)
        
        drugs = patient['medications']
        med_list_str = ", ".join(drugs)
        drug_pairs = list(itertools.combinations(drugs, 2))
        
        for d1, d2 in drug_pairs:
            # Fetch from cache (guaranteed to be there now)
            lit_status, chem_status = utils.get_cached_result(d1, d2)
            
            # Handle special cases (Biologicals)
            biologicals = ["Insulin", "Monoclonal", "Vaccine"]
            if any(bio in d1 or bio in d2 for bio in biologicals):
                chem_status = "🧬 Biological Agent (Structure Skipped)"
            
            # Insert record into department-specific table
            audit_cursor.execute(f'''
                INSERT INTO {table_name} 
                (patient_name, age, diagnosis, medication_list, drug_1, drug_2, literature_risk, biochem_risk)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                patient['name'], 
                patient['age'], 
                patient['diagnosis'], 
                med_list_str,
                d1, 
                d2, 
                lit_status or "✅ No obvious flag in literature.", 
                chem_status or "⚪ Data Unavailable"
            ))

    audit_conn.commit()
    audit_conn.close()

    print("\n" + "="*50)
    print("✅  AUDIT COMPLETE. Results saved to 'audit_results.db'")
    print("="*50)

if __name__ == "__main__":
    main()
