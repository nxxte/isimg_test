import pdfplumber
import json
import os # Keep os for file path management

# --- Configuration ---
PDF_PATH = 'pdfs/4.pdf' # Changed to use a variable for better clarity
OUTPUT_FILE = 'output_idk.json'

# --- Data Structures ---
matierat = {
    "matierat1": [], # Semester 1 subjects
    "matierat2": []  # Semester 2 subjects
}#time python script1.py
# Initial state trackers
current_sem = "1"
current_matiere_data = {}
notet = {"ds": None, "tp": None, "oral": None, "ex": None, "ds2": None}
coeff = {"ds": None, "tp": None, "oral": None, "ex": None, "ds2": None}
is_grade_row = False

# --- Helper Functions for Robust Parsing ---

def safe_float(value):
    """Converts value to float, handling None, empty strings, and commas."""
    if value is None or value == '':
        return None
    try:
        # Replace comma with period for French numbers and clean whitespace
        return float(str(value).replace(",", ".").strip())
    except ValueError:
        return None

def safe_int(value):
    """Converts value to int, handling None, empty strings, or floats."""
    if value is None or value == '':
        return None
    try:
        # Convert to float first to handle cases like '3.0'
        return int(float(str(value).strip()))
    except (ValueError, TypeError):
        return None

def find_substring_in_row(row, x):
    """Finds the index of a cell containing substring x."""
    for i, item in enumerate(row):
        if isinstance(item, str) and x in item:
            return i, item
    return None, None

def save_current_matiere(sem_key):
    """Saves the completed subject data to the global structure."""
    global current_matiere_data, notet, coeff
    
    # Check if a subject has been started and has collected at least one grade
    if current_matiere_data and (any(notet.values()) or any(coeff.values())):
        matiere = {
            "name": current_matiere_data.get("name"),
            "coef": current_matiere_data.get("coef"),
            "credit": current_matiere_data.get("credit"),
            "notet": notet.copy(),
            "coeff": coeff.copy()
        }
        matierat[f"matierat{sem_key}"].append(matiere)
    
    # Reset state for the next subject
    current_matiere_data = {}
    notet.clear()
    notet.update({"ds": None, "tp": None, "oral": None, "ex": None, "ds2": None})
    coeff.clear()
    coeff.update({"ds": None, "tp": None, "oral": None, "ex": None, "ds2": None})


# --- Main Parsing Logic ---

with pdfplumber.open(PDF_PATH) as pdf:
    for page in pdf.pages:
        tables = page.extract_tables()
        for table in tables:
            for row in table:
                
                # Clean and normalize row elements
                cleaned_row = [str(c).strip().replace('\n', ' ') if c is not None else '' for c in row]
                
                # 1. Skip header rows
                if 'Sem.' in cleaned_row or 'Unité' in cleaned_row or not cleaned_row or all(c == '' for c in cleaned_row):
                    continue
                
                # 2. SEMESTER DETECTION (Replaces slow OCR)
                # Check for the Unit Code (e.g., UE21) in the first few columns
                if 'UE2' in cleaned_row[0] or 'UE2' in cleaned_row[1]:
                    current_sem = "2"
                # If 'UE1' is detected, ensure we are back to SEM 1 (in case file has multiple pages)
                elif 'UE1' in cleaned_row[0] or 'UE1' in cleaned_row[1]:
                    current_sem = "1"
                    
                # 3. SUBJECT DEFINITION (New Matière)
                
                # The most reliable markers for a new subject are 'RM'/'CC' (Régime) and the Crédits value (int > 0)
                regime_index = -1
                for i in [3, 4, 5]: # Check typical Régime columns
                    if i < len(cleaned_row) and (cleaned_row[i] == 'RM' or cleaned_row[i] == 'CC'):
                        regime_index = i
                        break
                
                if regime_index != -1 and safe_int(cleaned_row[regime_index + 2]): # Check for Credit value (2 columns after Régime)
                    
                    # Save the previous subject's data before defining the new one
                    save_current_matiere(current_sem)
                    
                    # Define the new subject
                    current_matiere_data = {
                        "name": cleaned_row[regime_index - 1], # Matière is 1 column left of Régime
                        "coef": safe_float(cleaned_row[regime_index + 1]), # Coeff is 1 column right
                        "credit": safe_int(cleaned_row[regime_index + 2]), # Credit is 2 columns right
                    }

                # 4. GRADE EXTRACTION (Works for continuation rows)
                
                # Find the Epreuve column
                epreuve_index, epreuve_text = find_substring_in_row(cleaned_row, '(') # Looks for (0.3), (0.7), etc.
                
                if epreuve_index is not None and epreuve_index < len(cleaned_row) - 1:
                    
                    # Note is always 1 column right of Epreuve
                    note_value = cleaned_row[epreuve_index + 1] 
                    note = safe_float(note_value)
                    
                    # Coefficient is extracted from the Epreuve text
                    coeff_val = safe_float(epreuve_text.split('(')[-1].replace(')', ''))
                    
                    if note is not None and current_matiere_data:
                        # Logic to assign note/coeff
                        if 'Ex' in epreuve_text:
                            notet["ex"] = note
                            coeff["ex"] = coeff_val
                        elif 'TP' in epreuve_text:
                            notet["tp"] = note
                            coeff["tp"] = coeff_val
                        elif 'Oral' in epreuve_text:
                            notet["oral"] = note
                            coeff["oral"] = coeff_val
                        elif 'DS' in epreuve_text:
                            # Assign DS only if the first slot is empty, otherwise use DS2
                            if notet["ds"] is None:
                                notet["ds"] = note
                                coeff["ds"] = coeff_val
                            else:
                                notet["ds2"] = note
                                coeff["ds2"] = coeff_val

# 5. Final Save: Save the very last subject processed
save_current_matiere(current_sem)

# 6. Output the result
with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
    json.dump(matierat, f, ensure_ascii=False, indent=4)