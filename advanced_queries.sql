-- =================================================================================
-- ADVANCED SQL QUERIES FOR DDI AUDITOR PORTFOLIO
-- =================================================================================
-- These 10 queries demonstrate advanced data analysis skills:
-- CTEs, Subqueries, Window Functions, Aggregations, String Manipulations, and Joins.
-- Run these against 'audit_results.db' or 'high_risk_patients.db'.
-- =================================================================================
-- 1. DEPARTMENT RISK DISTRIBUTION (Aggregation & Grouping)
-- Calculates the total number of flagged interactions per department
SELECT department,
    COUNT(*) as total_interactions_checked,
    SUM(
        CASE
            WHEN literature_risk LIKE '%KNOWN RISK%' THEN 1
            ELSE 0
        END
    ) as literature_risks,
    SUM(
        CASE
            WHEN biochem_risk LIKE '%HIGH STRUCTURAL SIMILARITY%' THEN 1
            ELSE 0
        END
    ) as high_chemical_risks
FROM patient_safety_audit
GROUP BY department
ORDER BY literature_risks DESC;
-- 2. THE HIGHEST RISK DRUG PAIRS (Aggregation & Filtering)
-- Identifies the specific drug combinations that trigger the most "KNOWN RISK" warnings
SELECT drug_1,
    drug_2,
    COUNT(*) as frequency_of_prescription
FROM patient_safety_audit
WHERE literature_risk LIKE '%KNOWN RISK%'
GROUP BY drug_1,
    drug_2
ORDER BY frequency_of_prescription DESC
LIMIT 5;
-- 3. THE POLYPHARMACY CHAMPIONS (Subqueries / CTE)
-- Finds patients taking the highest number of interacting drugs
WITH PatientInteractions AS (
    SELECT patient_name,
        department,
        COUNT(*) as interaction_count
    FROM patient_safety_audit
    WHERE literature_risk LIKE '%KNOWN RISK%'
        OR biochem_risk LIKE '%HIGH STRUCTURAL SIMILARITY%'
    GROUP BY patient_name,
        department
)
SELECT *
FROM PatientInteractions
WHERE interaction_count > 3
ORDER BY interaction_count DESC;
-- 4. AGE DEMOGRAPHICS OF HIGH RISK PATIENTS (Case Statements & Aggregation)
-- Groups high-risk patients into age brackets to see which demographic is most affected
SELECT CASE
        WHEN age < 30 THEN 'Under 30'
        WHEN age BETWEEN 30 AND 50 THEN '30 - 50'
        WHEN age BETWEEN 51 AND 70 THEN '51 - 70'
        ELSE 'Over 70'
    END AS age_bracket,
    COUNT(DISTINCT patient_name) as unique_high_risk_patients
FROM patient_safety_audit
WHERE literature_risk LIKE '%KNOWN RISK%'
GROUP BY age_bracket
ORDER BY unique_high_risk_patients DESC;
-- 5. THE "SILENT KILLER" CHEMICAL SIMILARITIES (Window Function)
-- Finds drug pairs that have high structural similarity but NO known literature risk yet
-- Ranks them by the number of times they were prescribed
WITH ChemicalRisks AS (
    SELECT drug_1,
        drug_2,
        biochem_risk,
        COUNT(*) as prescription_count,
        RANK() OVER (
            ORDER BY COUNT(*) DESC
        ) as risk_rank
    FROM patient_safety_audit
    WHERE biochem_risk LIKE '%HIGH STRUCTURAL SIMILARITY%'
        AND literature_risk NOT LIKE '%KNOWN RISK%'
    GROUP BY drug_1,
        drug_2,
        biochem_risk
)
SELECT *
FROM ChemicalRisks
WHERE risk_rank <= 3;
-- 6. PERCENTAGE OF RISK BY DEPARTMENT (Math Operations & Subqueries)
-- Calculates what percentage of a department's total prescriptions result in a KNOWN RISK
SELECT department,
    COUNT(
        CASE
            WHEN literature_risk LIKE '%KNOWN RISK%' THEN 1
        END
    ) * 100.0 / COUNT(*) as risk_percentage
FROM patient_safety_audit
GROUP BY department
ORDER BY risk_percentage DESC;
-- 7. BIOLOGICAL AGENT PREVALENCE (String Matching / LIKE)
-- Finds all interactions involving a biological agent (like Insulin)
SELECT department,
    patient_name,
    drug_1,
    drug_2
FROM patient_safety_audit
WHERE biochem_risk LIKE '%Biological Agent%'
ORDER BY department;
-- 8. PATIENTS REQUIRING IMMEDIATE INTERVENTION (Multiple Conditions)
-- Identifies specific, highly vulnerable patients (Elderly + Known Interaction)
SELECT DISTINCT patient_name,
    age,
    department,
    diagnosis
FROM patient_safety_audit
WHERE age > 65
    AND literature_risk LIKE '%KNOWN RISK%'
ORDER BY age DESC;
-- 9. DRUG INVOLVEMENT FREQUENCY (UNION ALL)
-- Determines which single drug is most frequently involved in ANY flagged interaction
WITH AllDrugs AS (
    SELECT drug_1 as drug_name
    FROM patient_safety_audit
    WHERE literature_risk LIKE '%KNOWN RISK%'
    UNION ALL
    SELECT drug_2 as drug_name
    FROM patient_safety_audit
    WHERE literature_risk LIKE '%KNOWN RISK%'
)
SELECT drug_name,
    COUNT(*) as times_involved_in_risk
FROM AllDrugs
GROUP BY drug_name
ORDER BY times_involved_in_risk DESC
LIMIT 10;
-- 10. DEPARTMENTAL WORKLOAD (Basic overview with formatting)
-- A simple summary of how many unique patients each department is managing in this audit
SELECT department,
    COUNT(DISTINCT patient_name) as distinct_patients_audited
FROM patient_safety_audit
GROUP BY department
ORDER BY distinct_patients_audited DESC;