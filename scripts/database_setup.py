import sqlite3
import random

# ==========================================
# PART 1: DATA PREPARATION
# ==========================================

first_names = [
    "Aarav", "Vivaan", "Aditya", "Vihaan", "Arjun", "Sai", "Reyansh", "Ayaan", "Krishna", "Ishaan",
    "Diya", "Saanvi", "Ananya", "Aadhya", "Pari", "Kiara", "Myra", "Riya", "Aarya", "Anika",
    "Rohan", "Vikram", "Rahul", "Neha", "Pooja", "Suresh", "Ramesh", "Sita", "Gita", "Lakshmi",
    "Amit", "Sumit", "Karan", "Simran", "Preeti", "Sunil", "Anil", "Raj", "Rani", "Meera",
    "Kabir", "Zara", "Yash", "Nikhil", "Siddharth", "Gauri", "Shreya", "Sneha", "Tanvi", "Kavya"
]

last_names = [
    "Patel", "Sharma", "Singh", "Kumar", "Gupta", "Verma", "Mishra", "Reddy", "Nair", "Iyer",
    "Kulkarni", "Desai", "Joshi", "Mehta", "Shah", "Agarwal", "Malhotra", "Khanna", "Bhatia", "Saxena",
    "Chopra", "Das", "Sen", "Roy", "Banerjee", "Chatterjee", "Mukherjee", "Dutta", "Bose", "Ghosh",
    "Rao", "More", "Pawar", "Gaikwad", "Jadhav", "Shinde", "Kadam", "Chavan", "Suryavanshi", "Sawant"
]

# Department > Diagnosis > Medications Map
department_data = {
    "Cardiology": {
        "diagnoses": ["Hypertension", "Heart Failure", "Angina", "Arrhythmia", "Coronary Artery Disease"],
        "medications": ["Amlodipine", "Lisinopril", "Losartan", "Hydrochlorothiazide", "Furosemide", "Carvedilol", "Spironolactone", "Digoxin", "Atorvastatin", "Aspirin", "Clopidogrel"]
    },
    "Endocrinology": {
        "diagnoses": ["Type 2 Diabetes", "Hypothyroidism", "Hyperthyroidism", "PCOS"],
        "medications": ["Metformin", "Glipizide", "Insulin", "Sitagliptin", "Levothyroxine", "Pioglitazone", "Empagliflozin"]
    },
    "Neurology": {
        "diagnoses": ["Migraine", "Epilepsy", "Parkinson's Disease", "Stroke", "Neuropathy"],
        "medications": ["Sumatriptan", "Topiramate", "Levodopa", "Gabapentin", "Pregabalin", "Carbamazepine", "Valproate"]
    },
    "Gastroenterology": {
        "diagnoses": ["GERD", "IBS", "Peptic Ulcer", "Gastritis"],
        "medications": ["Omeprazole", "Pantoprazole", "Ranitidine", "Famotidine", "Ondansetron", "Loperamide"]
    },
    "Pediatrics": { # Special logic for age required here
        "diagnoses": ["Asthma", "Infection", "Allergy", "Fever"],
        "medications": ["Albuterol", "Amoxicillin", "Paracetamol", "Ibuprofen", "Cetirizine", "Azithromycin"]
    },
    "Orthopedics": {
        "diagnoses": ["Arthritis", "Lower Back Pain", "Fracture", "Osteoporosis"],
        "medications": ["Ibuprofen", "Naproxen", "Diclofenac", "Tramadol", "Calcium/Vit D", "Meloxicam"]
    }
}

department_list = list(department_data.keys())

import os

# ==========================================
# PART 2: DATABASE SETUP
# ==========================================

# Move up one level to project root, then into 'outputs'
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "outputs", "patients.db")

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

print("Creating database tables...")

cursor.execute("DROP TABLE IF EXISTS prescriptions")
cursor.execute("DROP TABLE IF EXISTS patients")

# Create 'patients' table with DEPARTMENT
cursor.execute('''
    CREATE TABLE patients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        age INTEGER,
        department TEXT,
        diagnosis TEXT
    )
''')

# Create 'prescriptions' table
cursor.execute('''
    CREATE TABLE prescriptions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id INTEGER,
        drug_name TEXT,
        FOREIGN KEY (patient_id) REFERENCES patients (id)
    )
''')

# ==========================================
# PART 3: GENERATING AND INSERTING DATA
# ==========================================

print("Generating synthetic patient data with departments...")

generated_names = set()
total_patients = 100
polypharmacy_count = 0

for i in range(total_patients):
    # 1. Unique Name
    while True:
        f_name = random.choice(first_names)
        l_name = random.choice(last_names)
        full_name = f"{f_name} {l_name}"
        if full_name not in generated_names:
            generated_names.add(full_name)
            break
    
    # 2. Select Department
    dept = random.choice(department_list)
    
    # 3. Age Logic based on Department
    if dept == "Pediatrics":
        age = random.randint(1, 17)
    else:
        age = random.randint(18, 90)
    
    # 4. Diagnosis Logic
    dept_info = department_data[dept]
    possible_diagnoses = dept_info["diagnoses"]
    primary_diagnosis = random.choice(possible_diagnoses)
    
    # Insert patient
    cursor.execute("INSERT INTO patients (name, age, department, diagnosis) VALUES (?, ?, ?, ?)", 
                   (full_name, age, dept, primary_diagnosis))
    patient_id = cursor.lastrowid
    
    # 5. Medications Logic (Polypharmacy enforcement)
    # We need ~50 patients with >= 3 drugs.
    
    target_drug_count = 0
    if polypharmacy_count < 55:
        target_drug_count = random.randint(3, 6)
        polypharmacy_count += 1
    else:
        target_drug_count = random.randint(1, 2)
        
    patient_meds = []
    
    # A. First, pick 1-2 drugs from their specific department
    dept_meds = dept_info["medications"]
    primary_meds_count = min(len(dept_meds), random.randint(1, 2))
    patient_meds.extend(random.sample(dept_meds, k=primary_meds_count))
    
    # B. If we need more drugs for polypharmacy, pick from "General/Comorbidities"
    # e.g., A Cardiology patient might also have Diabetes (Endo) or Pain (Ortho)
    
    all_possible_drugs = []
    for d_key, d_val in department_data.items():
        if d_key != "Pediatrics": # Don't give adult drugs to random fills unless carefully checked, but for simple demo:
             all_possible_drugs.extend(d_val["medications"])
    
    # Remove duplicates from our master list
    all_possible_drugs = list(set(all_possible_drugs))
    
    attempts = 0
    while len(patient_meds) < target_drug_count and attempts < 20:
        attempts += 1
        random_drug = random.choice(all_possible_drugs)
        if random_drug not in patient_meds:
            patient_meds.append(random_drug)

    # Insert prescriptions
    for drug in patient_meds:
        cursor.execute("INSERT INTO prescriptions (patient_id, drug_name) VALUES (?, ?)", 
                       (patient_id, drug))

conn.commit()
conn.close()

print(f"Successfully created {total_patients} patients.")
print(f"Generated {polypharmacy_count} polypharmacy cases.")
print("Database 'patients.db' ready.")
