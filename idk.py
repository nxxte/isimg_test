import pdfplumber
import json

# --- Data Structures ---
matierat = {
    "matierat": []
}

current_matiere = None
notet = {
    "ds": None,
    "tp": None,
    "oral": None,
    "ex": None,
    "ds2": None
}

# --- Helper Functions for Robust Parsing ---

def safe_float(value):
    """Converts value to float, handling None or empty strings."""
    if value is None or value == '':
        return 0.0
    try:
        # Replace comma with period for French numbers and clean whitespace
        return float(str(value).replace(",", ".").strip())
    except ValueError:
        return None

def safe_int(value):
    """Converts value to int, handling None, empty strings, or floats."""
    if value is None or value == '':
        return 0
    try:
        # Convert to float first to handle cases like '3.0' or '3'
        return int(float(str(value).strip()))
    except (ValueError, TypeError):
        return None

# --- Main Parsing Logic ---

with pdfplumber.open("1.pdf") as pdf:
    for page in pdf.pages:
        tables = page.extract_tables()
        for table in tables:
            for row in table:
                
                # 1. Clean up row elements and replace None with ''
                cleaned_row = [str(c).strip().replace('\n', ' ') if c is not None else '' for c in row]
                
                # Skip header rows or empty rows
                if 'Sem.' in cleaned_row or 'Unité' in cleaned_row or not cleaned_row or all(c == '' for c in cleaned_row[1:]):
                    continue

                # 2. DETECT AND STORE NEW MATIERE (SUBJECT)
                
                # Find the 'Crédits' column index (the most reliable indicator)
                # Check columns 4, 5, or 6 for a positive integer value (3, 4, 6, etc.)
                credit_index = -1
                for i in [4, 5, 6]:
                    if i < len(cleaned_row) and safe_int(cleaned_row[i]) is not None and safe_int(cleaned_row[i]) > 0:
                        credit_index = i
                        break

                # If we found a valid credit and a subject name before it, it's a new subject definition.
                if credit_index != -1 and cleaned_row[credit_index - 2]:
                    
                    # Save the previous subject's data if complete
                    if current_matiere is not None and (notet["ex"] is not None or notet["ds"] is not None):
                        current_matiere["notet"] = notet.copy()
                        matierat["matierat"].append(current_matiere)
                    
                    # Define the new subject
                    current_matiere = {
                        "name": cleaned_row[credit_index - 2], # Matière is two columns left of Crédits
                        "coef": safe_float(cleaned_row[credit_index - 1]), # Coeff is one column left
                        "credit": safe_int(cleaned_row[credit_index]),
                        "notet": None
                    }
                    # Reset notes for the new subject
                    notet = { "ds": None, "tp": None, "oral": None, "ex": None, "ds2": None }

                # 3. EXTRACT GRADES FOR THE CURRENT MATIERE

                # Find the 'Epreuve' column index by checking for keywords in expected columns (6, 7, 8)
                epreuve_index = -1
                EP_KEYWORDS = ['DS', 'Ex', 'TP', 'Oral']
                for i in [6, 7, 8]:
                    if i < len(cleaned_row) and cleaned_row[i] and any(kw in cleaned_row[i] for kw in EP_KEYWORDS):
                        epreuve_index = i
                        break
                
                if current_matiere and epreuve_index != -1:
                    
                    epreuve = cleaned_row[epreuve_index]
                    # Note is always one column right of Epreuve
                    note_value = cleaned_row[epreuve_index + 1] 
                    
                    note = safe_float(note_value)
                    
                    if note is not None:
                        # Map Epreuve to the note key
                        if 'Ex' in epreuve:
                            notet["ex"] = note
                        elif 'TP' in epreuve:
                            notet["tp"] = note
                        elif 'Oral' in epreuve:
                            notet["oral"] = note
                        # Handle DS and DS2: Use DS for the first one found, DS2 for the second
                        elif 'DS' in epreuve:
                            if notet["ds"] is None:
                                notet["ds"] = note
                            else:
                                # Assign to DS2 only if DS is already taken
                                notet["ds2"] = note

# 4. Save the last processed subject outside the loops
if current_matiere is not None and (notet["ds"] is not None or notet["ex"] is not None):
    current_matiere["notet"] = notet.copy()
    matierat["matierat"].append(current_matiere)

# 5. Output the result
with open('output_1_fixed.json', 'w', encoding='utf-8') as f:
    json.dump(matierat, f, ensure_ascii=False, indent=4)