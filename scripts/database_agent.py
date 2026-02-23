import sqlite3

# ==========================================
# DATABASE AGENT
# ==========================================
# Role: Identify patients who are at risk due to Polypharmacy.
# Polypharmacy here is defined as taking 3 or more medications.
# ==========================================

import os

def get_at_risk_patients():
    """
    Connects to the database and runs a SQL query to find
    patients taking more than 3 medications.
    
    Returns:
        list: A list of tuples, where each tuple contains (patient_id, patient_name, list_of_drugs)
    """
    
    print("[Database Agent] Connecting to patient records...")
    
    # Define path to the database in 'outputs' folder
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DB_PATH = os.path.join(BASE_DIR, "outputs", "patients.db")
    
    # 1. Connect to the database
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 2. SQL Query
    # We join patients with prescriptions, group by patient, 
    # and count the number of drugs.
    # HAVING COUNT(drug_name) >= 3 filters for our polypharmacy definition.
    query = '''
        SELECT 
            p.id, 
            p.name, 
            p.age,
            p.department,
            p.diagnosis,
            GROUP_CONCAT(pr.drug_name, ', ') as medication_list
        FROM patients p
        JOIN prescriptions pr ON p.id = pr.patient_id
        GROUP BY p.id
        HAVING COUNT(pr.drug_name) >= 3
        ORDER BY p.department
    '''
    
    try:
        cursor.execute(query)
        results = cursor.fetchall()
        
        # 3. Process results into a clean format
        # The query returns medication_list as a string "DrugA, DrugB". 
        # We'll split it into a proper Python list.
        at_risk_patients = []
        
        for row in results:
            p_id, p_name, age, dept, diagnosis, meds_str = row
            meds_list = meds_str.split(', ') # Convert "A, B" -> ["A", "B"]
            
            # Store in a dictionary for easy access later
            patient_data = {
                "id": p_id,
                "name": p_name,
                "age": age,
                "department": dept,
                "diagnosis": diagnosis,
                "medications": meds_list
            }
            at_risk_patients.append(patient_data)
            
        print(f"[Database Agent] Found {len(at_risk_patients)} patients with polypharmacy risk.")
        return at_risk_patients

    except Exception as e:
        print(f"[Database Agent] Error: {e}")
        return []
        
    finally:
        conn.close()

# Simple test block to run this agent independently
if __name__ == "__main__":
    patients = get_at_risk_patients()
    if patients:
        print(f"Example Patient: {patients[0]['name']} takes {patients[0]['medications']}")
