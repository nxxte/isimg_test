import pdfplumber
import pandas  as pd
with pdfplumber.open("2.pdf") as pdf:
    for page in pdf.pages:
        table = page.extract_table()
        if table:
            df = pd.DataFrame(table)
            print(df)