import pdfplumber
import json

matierat = {
    "matierat": []
}

def find_substring_in_row(row, x):
    found = None
    for item in row:
        if isinstance(item, str):
            if x in item:
                found = item
                break
    return found

notet = {
    "ds": None,
    "tp": None,
    "oral": None,
    "ex": None,
    "ds2": None
}

coeff = {
    "ds": None,
    "tp": None,
    "oral": None,
    "ex": None,
    "ds2": None
}

with pdfplumber.open("pdfs/4.pdf") as pdf:
    for page in pdf.pages:
        tables = page.extract_tables()
        for table in tables:
            for row in table:
                if 'Sem.' in row:
                    continue
#                print(row,(notet["ex"] != None and notet["ds"] != None) or (notet["ds2"] != None and notet["ds"] != None) or ((coeff.get("tp", 0.0) or 0.0) + (coeff.get("ds2", 0.0) or 0.0) == 1.0))
                if ('RM' in row or 'CC' in row):#(notet["ex"] == None and notet["ds"] == None)
                    for i in range(len(row)):
                        if row[i] == 'RM' or row[i] == 'CC':
                            break
                    s = str(row[i-1])
                    name = s.replace("\n", " ")
                    coef = float(row[i+1])
                    credit = int(row[i+2])
                    if (o := find_substring_in_row(row, 'DS')) is not None:
                        notet["ds"] = float(row[i+4])
                        coeff["ds"] = float(o.split('(')[1].replace(')',''))
                    elif (o := find_substring_in_row(row, 'TP')) is not None:
                        notet["tp"] = float(row[i+4])
                        coeff["tp"] = float(o.split('(')[1].replace(')',''))
                elif (o := find_substring_in_row(row, 'TP')) is not None and notet["tp"] == None:
                    for i in range(len(row)):
                        if row[i] == o:
                            break
                    notet["tp"] = (0 if row[i+1] == '' else float(row[i+1]))
                    coeff["tp"] = float(o.split('(')[1].replace(')',''))
                elif (o := find_substring_in_row(row, 'Oral')) is not None and notet["oral"] == None:
                    for i in range(len(row)):
                        if row[i] == o:
                            break
                    notet["oral"] = (0 if row[i+1] == '' else float(row[i+1]))
                    coeff["oral"] = float(o.split('(')[1].replace(')',''))
                elif (o := find_substring_in_row(row, 'Ex')) is not None and notet["ex"] == None:
                    for i in range(len(row)):
                        if row[i] == o:
                            break
                    notet["ex"] = (0 if row[i+1] == '' else float(row[i+1]))
                    coeff["ex"] = float(o.split('(')[1].replace(')',''))
                elif ((o := find_substring_in_row(row, 'DS')) is not None) and notet["ds2"] == None:
                    for i in range(len(row)):
                        if row[i] == o:
                            break
                    notet["ds2"] = (0 if row[i+1] == '' else float(row[i+1]))
                    coeff["ds2"] = float(o.split('(')[1].replace(')',''))
                if (notet["ex"] != None and notet["ds"] != None) or (notet["ds2"] != None and notet["ds"] != None) or ((coeff.get("tp", 0.0) or 0.0) + (coeff.get("ds2", 0.0) or 0.0) == 1.0):
                    matiere = {
                        "name":name,
                        "coef":coef,
                        "credit":credit,
                        "notet": notet,
                        "coeff": coeff
                    }
                    matierat["matierat"].append(matiere)
                    notet = {
                        "ds": None,
                        "tp": None,
                        "oral": None,
                        "ex": None,
                        "ds2": None
                    }
                    coeff = {
                        "ds": None,
                        "tp": None,
                        "oral": None,
                        "ex": None,
                        "ds2": None
                    }
with open('output.json', 'w', encoding='utf-8') as f:
    json.dump(matierat,f,ensure_ascii=False, indent=4)