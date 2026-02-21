from rdkit import Chem
from rdkit.Chem import DataStructs
from rdkit.Chem import AllChem
from rdkit import RDLogger

# Suppress RDKit warnings/logs to keep output clean
RDLogger.DisableLog('rdApp.*')

# ==========================================
# BIO-CHEMIST AGENT
# ==========================================
# Role: Perform structural analysis on drugs.
# ==========================================

# Dictionary mapping Drug Names to SMILES strings (Chemical Structures)
# EXPANDED LIST for all departments
DRUG_SMILES = {
    # 1. Cardiology
    "Amlodipine": "CCOC(=O)C1=C(C)NC(C)=C(C1C2=CC=CC=C2Cl)C(=O)OC",
    "Lisinopril": "NCCCCC(N)C(=O)N1CCCC1C(=O)O", 
    "Losartan": "CCCC1=NC(=C(N1CC2=CC=C(C=C2)C3=CC=CC=C3N4N=NN=C4)Cl)CO",
    "Hydrochlorothiazide": "NS(=O)(=O)C1=CC=C(NCC2=CC=CC=C2)C=C1",
    "Furosemide": "C1=C(C=C(C(=C1)C(=O)O)S(=O)(=O)N)NCC2=CC=CO2",
    "Carvedilol": "COC1=CC=CC=C1OCCNCC(O)COC2=CC=CC3=C2C=CN3",
    "Spironolactone": "CC12CCC3C(C1CCC2SC(=O)C)CCC4=CC(=O)CCC34C", # Approx steroid backbone
    "Digoxin": "CC1C(OC2C(OC3C(OC4CCC(C(C4)O)O)C)O)OC5C1OC(C5O)C", # Complex glycoside, simplified
    "Atorvastatin": "CC(C)C1=C(C(=O)NC2=CC=CC=C2)C(C3=CC=CC=C3)=C(N1CC[C@H](O)C[C@H](O)CC(=O)O)C4=CC=C(F)C=C4",
    "Aspirin": "CC(=O)OC1=CC=CC=C1C(=O)O",
    "Clopidogrel": "COC(=O)C(C1=CC=CC=C1Cl)N2CCC3=C(C2)C=CS3",

    # 2. Endocrinology
    "Metformin": "CN(C)C(=N)NC(=N)N",
    "Glipizide": "CC1=CC=C(C=C1)S(=O)(=O)NC(=O)NCC2=CC=CC=N2",
    "Insulin": None, # Protein, too big
    "Sitagliptin": "FC(F)(F)C1=CC(=CC=C1)CC(N)CC(=O)N2CC(N3C=NN=N3)CC2F",
    "Levothyroxine": "OC1=C(I)C=C(OC2=CC(I)=C(O)C(I)=C2)C=C1CC(N)C(=O)O", # T4
    "Pioglitazone": "CC1=CN=C(C=C1)CCOC2=CC=C(C=C2)CC3C(=O)NC(=O)S3",
    "Empagliflozin": "ClC1=CC=C(CC2=CC=C(O[C@H]3O[C@H](CO)[C@@H](O)[C@H](O)[C@H]3O)C(Cl)=C2)C=C1",

    # 3. Neurology
    "Sumatriptan": "CNS(=O)(=O)CC1=CC2=C(NC2=C1)CC(N)C", # Simplification
    "Topiramate": "CC1(C)OC2CC(OS(=O)(=O)N)OC2(C)OC1(C)C", # Simplification
    "Levodopa": "NC(CC1=CC(O)=C(O)C=C1)C(=O)O",
    "Gabapentin": "NC1(CC1)CC(=O)O",
    "Pregabalin": "CC(C)CC(CN)CC(=O)O",
    "Carbamazepine": "NC(=O)N1C2=CC=CC=C2C=CC3=CC=CC=C31",
    "Valproate": "CCCC(CCC)C(=O)O",

    # 4. Gastroenterology
    "Omeprazole": "CC1=CN=C(C(=C1OC)C)CS(=O)C2=NC3=C(N2)C=C(OC)C=C3",
    "Pantoprazole": "OC1=NC2=C(S1)C(OC)=CC=C2",
    "Ranitidine": "CNC(=C[N+](=O)[O-])NCCSC1=CC=C(O1)CN(C)C",
    "Famotidine": "NS(=O)(=O)C1=C(N=C(N)S1)CSC2=CC=C(CN(C)C)O2", # Approx
    "Ondansetron": "CN1C2=CC=CC=C2C(=O)C3=C1CCC3=O", # Approx
    "Loperamide": "CN(C)C(=O)C(C1=CC=CC=C1)(C2=CC=CC=C2)CCN3CCC(O)(C4=CC=C(Cl)C=C4)CC3",

    # 5. Pediatrics / Gen Med
    "Albuterol": "CC(C)(C)NCC(O)C1=CC(CO)=C(O)C=C1",
    "Amoxicillin": "CC1(C(N2C(S1)C(C2=O)NC(=O)C(C3=CC=CCC3)N)C(=O)O)C",
    "Paracetamol": "CC(=O)Nc1ccc(O)cc1",
    "Ibuprofen": "CC(C)CC1=CC=C(C=C1)C(C)C(=O)O",
    "Cetirizine": "ClC1=CC=C(C(N2CCN(CC(=O)O)CC2)C3=CC=CC=C3)C=C1",
    "Azithromycin": "CN(C)C", # Placeholder

    # 6. Orthopedics
    "Naproxen": "CC(C1=CC2=C(C=C1)C=C(OC)C=C2)C(=O)O",
    "Diclofenac": "OC(=O)Cc1ccccc1Nc2c(Cl)cccc2Cl",
    "Tramadol": "CN(C)CC(C1=CC=CC=C1)(O)C2CCCCC2",
    "Meloxicam": "CN1C(=C(O)C2=CC=CC=C2S1(=O)=O)C(=O)NC3=CC=C(C)N=C3",
    "Calcium/Vit D": None # Not a small molecule in this context
}

def analyze_structure_risk(drug1_name, drug2_name):
    """
    Calculates the Tanimoto Similarity between two drugs.
    """
    
    # 1. Get SMILES strings
    smi1 = DRUG_SMILES.get(drug1_name)
    smi2 = DRUG_SMILES.get(drug2_name)
    
    if not smi1 or not smi2:
        return "⚪ Data Unavailable (Complex/Missing structure)"
        
    try:
        # 2. Convert SMILES to RDKit Molecule objects
        mol1 = Chem.MolFromSmiles(smi1)
        mol2 = Chem.MolFromSmiles(smi2)
        
        if mol1 is None or mol2 is None:
            return "⚪ Invalid chemical structure data"

        # 3. Generate Fingerprints using the new Generator method to avoid warnings
        # Old: BigMorgan (Deprecation warning) -> New: MorganGenerator
        fpgen = AllChem.GetMorganGenerator(radius=2, fpSize=1024)
        fp1 = fpgen.GetFingerprint(mol1)
        fp2 = fpgen.GetFingerprint(mol2)
        
        # 4. Calculate Similarity
        similarity = DataStructs.TanimotoSimilarity(fp1, fp2)
        
        # 5. Evaluate Risk
        if similarity > 0.4:
            return f"⚠️ HIGH STRUCTURAL SIMILARITY ({similarity:.2f}). Possible metabolic competition."
        else:
            return f"✅ Low similarity ({similarity:.2f})."
            
    except Exception as e:
        return f"Error in chemical analysis: {e}"

# Simple test block
if __name__ == "__main__":
    print(analyze_structure_risk("Ibuprofen", "Naproxen"))
