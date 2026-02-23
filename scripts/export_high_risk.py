import sqlite3
import datetime

# ==========================================
# HIGH RISK EXPORT CAPABILITY
# ==========================================
# This script reads the audit_results.db and creates
# a separate file containing ONLY High-Risk patients.
# High Risk is defined as a KNOWN RISK in literature
# or HIGH STRUCTURAL SIMILARITY in chemistry.
# ==========================================

def export_high_risk_patients():
    import os
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    INPUT_DB = os.path.join(BASE_DIR, "outputs", "audit_results.db")
    OUTPUT_DB = os.path.join(BASE_DIR, "outputs", "high_risk_patients.db")
    
    try:
        conn = sqlite3.connect(INPUT_DB)
        cursor = conn.cursor()
        # Get all tables in the database
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall() if row[0] != "sqlite_sequence"]
        
        print(f"Connecting to output database '{OUTPUT_DB}'...")
        hr_conn = sqlite3.connect(OUTPUT_DB)
        hr_cursor = hr_conn.cursor()
        
        total_high_risk = 0
        
        for table in tables:
            print(f"Scanning department: {table}...")
            
            # Query for high risk interactions in this specific table
            query = f'''
                SELECT 
                    patient_name, 
                    age, 
                    diagnosis, 
                    drug_1, 
                    drug_2, 
                    literature_risk, 
                    biochem_risk
                FROM {table}
                WHERE literature_risk LIKE '%KNOWN RISK%'
                   OR biochem_risk LIKE '%HIGH STRUCTURAL SIMILARITY%'
            '''
            
            cursor.execute(query)
            high_risk_results = cursor.fetchall()
            
            if high_risk_results:
                total_high_risk += len(high_risk_results)
                
                # Drop old table to avoid duplicates
                hr_cursor.execute(f"DROP TABLE IF EXISTS {table}")
                
                # Create corresponding table in the new DB
                hr_cursor.execute(f'''
                    CREATE TABLE {table} (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        patient_name TEXT,
                        age INTEGER,
                        diagnosis TEXT,
                        drug_1 TEXT,
                        drug_2 TEXT,
                        literature_risk TEXT,
                        biochem_risk TEXT,
                        detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Insert the data
                for row in high_risk_results:
                    hr_cursor.execute(f'''
                        INSERT INTO {table} 
                        (patient_name, age, diagnosis, drug_1, drug_2, literature_risk, biochem_risk)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', row)
        
        hr_conn.commit()
        hr_conn.close()
        
        if total_high_risk == 0:
            print("No high-risk patients found in any department. Awesome!")
        else:
            print(f"\nSuccessfully generated {OUTPUT_DB} with data separated by department tables.")
            print(f"Total High-Risk Interactions Found: {total_high_risk}")
                
    except sqlite3.Error as e:
        print(f"Database Error: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    export_high_risk_patients()
