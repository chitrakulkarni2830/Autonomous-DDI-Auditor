# Project Report: Autonomous Drug-Drug Interaction (DDI) Auditor

## Executive Summary
The Autonomous DDI Auditor is a multi-agent AI system designed to proactively scan synthetic electronic health records (EHR) to identify high-risk patients suffering from polypharmacy (the concurrent use of multiple medications). The system cross-references patient prescriptions against the public NCBI PubMed database for known clinical interactions, and utilizes RDKit (Cheminformatics) to calculate structural similarities between drugs to predict undisclosed risks. 

## Business Problem & Context
Polypharmacy is a leading cause of preventable hospitalizations, particularly among the elderly. As patients are treated by multiple specialists (Cardiologists, Endocrinologists, Neurologists), the risk of adverse Drug-Drug Interactions (DDIs) increases exponentially. Traditional alert systems often suffer from "alert fatigue" (bombarding physicians with minor warnings) or rely on static, outdated databases. 

## Methodology: The Architecture
This project implements an **Agentic Workflow**, breaking the complex problem into specialized tasks managed by distinct Python modules:

1.  **Database Agent (`database_agent.py`)**: 
    *   **Skill:** Data Engineering & SQL.
    *   **Action:** Connects to the SQLite patient database, filtering out straightforward cases and identifying patients taking 3+ medications.
2.  **Literature Agent (`literature_agent.py`)**: 
    *   **Skill:** APIs & Natural Language Processing (Simulated).
    *   **Action:** Acts as a medical researcher. It builds dynamic API queries against the NCBI Entrez system (PubMed) to search for scientific literature mentioning the specific drug pair and "Drug Interactions". It employs a simulated LLM layer to parse the returned abstract volume and generate a readable clinical summary of the risk.
3.  **Bio-Chemist Agent (`biochem_agent.py`)**: 
    *   **Skill:** Computational Chemistry (RDKit).
    *   **Action:** When literature is inconclusive, this agent converts chemical names into SMILES strings, generates Morgan Fingerprints, and calculates the Tanimoto Similarity coefficient. High structural similarity (>50%) flags a potential risk for competitive metabolic binding (e.g., in liver CYP450 enzymes).

## Data Engineering Pipeline
The project generates 100 realistic, synthetic patient records mapped to specific medical departments. The output of the agentic audit is routed back into a structured, relational architecture.
*   **Audit Results (`audit_results.db`)**: Dynamically partitions data into department-specific tables (e.g., `Cardiology`, `Neurology`) for organized querying.
*   **High Risk Export (`high_risk_patients.db`)**: A chronologically appended database containing only interactions flagged as critical, acting as a priority queue for clinical pharmacists.

## Advanced Analytics & Visualization
The project goes beyond simple data processing:
*   **Advanced SQL Module (`advanced_queries.sql`)**: Contains 10 complex queries demonstrating proficiency in CTEs, Window Functions (Ranking risks), Aggregations, and string manipulation to derive business intelligence from the audit data.
*   **Streamlit Dashboard (`app.py`)**: A modern web interface built with Streamlit and Plotly to visualize the SQLite database. It provides an executive summary of total patients audited, dynamic bar charts of risk distribution across departments, and interactive data tables for granular review.

## Conclusion
The Autonomous DDI Auditor successfully demonstrates the integration of Data Engineering (SQL/SQLite), API manipulation (NCBI), Specialized Scientific Computation (RDKit), and Data Visualization (Streamlit). It represents a scalable, intelligent prototype capable of reducing adverse drug events in complex clinical environments.
