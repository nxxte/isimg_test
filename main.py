import pdfplumber
import json
#unité credit, matiere, coeff

matierat = {
    "matierat": []
}



'''                    s = row[1][row[1].find(":")+1:row[1].find("Cré")].replace("\n"," ")
                    unite = Unite(s)
                    matiere = Matiere(row[3].replace("\n", " "),float(row[5]),int(row[6]))
                    unite.add_matiere(matiere)

with pdfplumber.open("2.pdf") as pdf:
    for page in pdf.pages:
        print("\n")
        tables = page.extract_tables()
        for table in tables:
            for row in table:
                print(row)
                if 'Sem.' in row:
                    continue
                if ('DS (0.3)' in row or 'DS\n(0.15)' in row or 'DS (0.4)' in row or 'DS (0.15)' in row):
                    s=str(row[3])
                    if row[5] and row[6]:
                        name,coef,credit=s.replace("\n", " "),float(row[5]),int(row[6])
                    else:
                        matiere = {
                            "name":name,
                            "coef":coef,
                            "credit":credit,

                        }
                    for i in range(len(row)):
                        if row[i] in ['DS (0.3)', 'DS\n(0.15)', 'DS (0.4)', 'DS (0.15)']:
                            break
                    dss = (0 if row[i+1] == '' else float(row[i+1]))
                elif 'Ex (0.7)' in row:
                    for i in range(len(row)):
                        if row[i] == 'Ex (0.7)':
                            break
                    ex = (0 if row[i+1] == '' else float(row[i+1]))
                elif ('TP\n(0.15)' in row or 'TP (0.2)' in row or 'TP (0.15)' in row):
                    for i in range(len(row)):
                        if row[i] in ['TP\n(0.15)', 'TP (0.2)', 'TP (0.15)']:
                            break
                    tp = (0 if row[i+1] == '' else float(row[i+1]))
                elif ('Oral\n(0.2)' in row or 'Oral (0.2)' in row):
                    for i in range(len(row)):
                        if row[i] in ['Oral\n(0.2)', 'Oral (0.2)']:
                            break
                    oral = (0 if row[i+1] == '' else float(row[i+1]))
    a = 0
    b = 0
    c = 0
    d = 0
#print(dss)
     for key, value in grades.items():
        if a < len(dss):
            value['DS'] = dss[a]
            a += 1
        else:
            value['DS'] = 0

        if 'Ex' in value:
            if b < len(ex):
                value['Ex'] = ex[b]
                b += 1
            else:
                value['Ex'] = 0

        if 'Oral' in value:
            if c < len(oral):
                value['Oral'] = oral[c]
                c += 1
            else:
                value['Oral'] = 0

        if 'TP' in value:
            if d < len(tp):
                value['TP'] = tp[d]
                d += 1
            else:
                value['TP'] = 0

        if 'DS2' in value:
            if a < len(dss):
                value['DS2'] = dss[a]
                a += 1
            else:
                value['DS2'] = 0

    data = [
            { 'subject': 'proba1', 'ds': grades["proba1"]["DS"], 'tp': grades["proba1"]["TP"], 'ex': grades["proba1"]["Ex"]},  
            { 'subject': 'automat1', 'ds': grades["automat1"]["DS"], 'ex': grades["automat1"]["Ex"] },
            { 'subject': 'graphe1', 'ds': grades["graphe1"]["DS"], 'ex': grades["graphe1"]["Ex"] },  
            { 'subject': 'conception1', 'ds': grades["conception1"]["DS"], 'ex': grades["conception1"]["Ex"]},  
            { 'subject': 'java1', 'ds': grades["java1"]["DS"], 'ex': grades["java1"]["Ex"], 'tp': grades["java1"]["TP"] },  
            { 'subject': 'bd1', 'ds': grades["bd1"]["DS"], 'ex': grades["bd1"]["Ex"], 'tp': grades["bd1"]["TP"]},  
            { 'subject': 'reseaux1', 'ds': grades["reseaux1"]["DS"], 'tp': grades["reseaux1"]["TP"], 'ex': grades["reseaux1"]["Ex"]},  
            { 'subject': 'ang1', 'oral': grades["ang1"]["Oral"], 'ds': grades["ang1"]["DS"], 'ds2': grades["ang1"]["DS2"] },  
            { 'subject': 'ges1','oral': grades["ges1"]["Oral"], 'ds': grades["ges1"]["DS"], 'ds2': grades["ges1"]["DS2"]},  
            { 'subject': 'web1', 'ds': grades["web1"]["DS"], 'tp': grades["web1"]["TP"], 'ex': grades["web1"]["Ex"]},
            { 'subject': 'animation1', 'ds': grades["animation1"]["DS"], 'tp': grades["animation1"]["TP"], 'ex': grades["animation1"]["Ex"]}
    ]
    data2 =[
            { 'subject': "num", 'ds': grades["num"]["DS"], 'ex': grades["num"]["Ex"]},
            { 'subject': "tdi", 'ds': grades["tdi"]["DS"], 'tp': grades["tdi"]["TP"], 'ex': grades["tdi"]["Ex"]},
            { 'subject': "ig", 'd,': grades["ig"]["DS"], 'tp': grades["ig"]["TP"], 'ex': grades["ig"]["Ex"]},
            { 'subject': "web2", 'ds': grades["web2"]["DS"], 'tp': grades["web2"]["TP"], 'ex': grades["web2"]["Ex"]},
            { 'subject': "appm", 'ds': grades["appm"]["DS"], 'tp': grades["appm"]["TP"], 'ex': grades["appm"]["Ex"]},
            { 'subject': "ai", 'ds': grades["ai"]["DS"], 'tp': grades["ai"]["TP"], 'ex': grades["ai"]["Ex"]},
            { 'subject': "test", 'ds': grades["test"]["DS"], 'tp': grades["test"]["TP"], 'ex': grades["test"]["Ex"]},
            { 'subject': "ang2", 'ds': grades["ang2"]["DS"], 'oral': grades["ang2"]["Oral"], 'ds2': grades["ang2"]["DS2"]},
            { 'subject': "droit", 'ds': grades["droit"]["DS"], 'oral': grades["droit"]["Oral"], 'ds2': grades["droit"]["DS2"]},
            { 'subject': "projet", 'ds': grades["projet"]["DS"], 'tp': grades["projet"]["TP"], 'ds2': grades["projet"]["DS2"]},
            { 'subject': "web3", 'ds': grades["web3"]["DS"], 'tp': grades["web3"]["TP"], 'ex': grades["web3"]["Ex"]},
            { 'subject': "cross", 'ds': grades["cross"]["DS"], 'tp': grades["cross"]["TP"], 'ex': grades["cross"]["Ex"]}
    ]'''
notet = {
    "ds": None,
    "tp": None,
    "oral": None,
    "ex": None,
    "ds2": None
}
with pdfplumber.open("pdfs/3.pdf") as pdf:
    for page in pdf.pages:
        tables = page.extract_tables()
        for table in tables:
            for row in table:
                print(row)
                if 'Sem.' in row:
                    continue
'''                if (notet["ex"] == None and notet["ds"] == None):
                    s=str(row[3])
                    if row[5] and row[6]:
                        name,coef,credit=s.replace("\n", " "),float(row[5]),int(row[6])
                        notet["ds"] = (0 if row[8] == '' else float(row[8]))
                elif ('TP\n(0.15)' in row or 'TP (0.2)' in row or 'TP (0.15)' in row):
                    for i in range(len(row)):
                        if row[i] in ['TP\n(0.15)', 'TP (0.2)', 'TP (0.15)']:
                            break
                    notet["tp"] = (0 if row[i+1] == '' else float(row[i+1]))
                elif ('Oral\n(0.2)' in row or 'Oral (0.2)' in row):
                    for i in range(len(row)):
                        if row[i] in ['Oral\n(0.2)', 'Oral (0.2)']:
                            break
                    notet["oral"] = (0 if row[i+1] == '' else float(row[i+1]))
                elif 'Ex (0.7)' in row:
                    for i in range(len(row)):
                        if row[i] == 'Ex (0.7)':
                            break
                    notet["ex"] = (0 if row[i+1] == '' else float(row[i+1]))
                elif 'DS (0.4)' in row and notet["ds"] != None:
                    for i in range(len(row)):
                        if row[i] == 'DS (0.4)':
                            break
                    notet["ds2"] = (0 if row[i+1] == '' else float(row[i+1]))
                if notet["ex"] or notet["ds2"]:    
                    
                    matiere = {
                        "name":name,
                        "coef":coef,
                        "credit":credit,
                        "notet": notet
                    }
                    matierat["matierat"].append(matiere)
                    notet = {
                        "ds": None,
                        "tp": None,
                        "oral": None,
                        "ex": None,
                        "ds2": None
                    }
with open('output.json', 'w', encoding='utf-8') as f:
    json.dump(matierat,f,ensure_ascii=False, indent=4)'''