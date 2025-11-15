import pdfplumber
import json
import fitz  # PyMuPDF
import os
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
import pytesseract
import cv2

def convert_specific_page_to_image(pdf_path, output_path, page_num):
    if not os.path.exists(pdf_path):
        print(f"Error: PDF file '{pdf_path}' not found.")
        return

    page_index = page_num - 1 

    try:
        doc = fitz.open(pdf_path)
        
        if page_index < 0 or page_index >= len(doc):
            print(f"Error: PDF only has {len(doc)} pages. Cannot access page {page_num}.")
            doc.close()
            return
        
        page = doc.load_page(page_index)
        
        zoom = 300 / 72
        matrix = fitz.Matrix(zoom, zoom)
        
        pix = page.get_pixmap(matrix=matrix, alpha=False)
        
        pix.save(output_path)

        doc.close()
        
        print("\n--- Conversion SUCCESS ---")
    except Exception as e:
        return {"error": f"Conversion error: {str(e)}"}

def extract_matiere(image_path, target_char):
    out_txt = 'extracted_matiere.txt'
    out_img_crop = 'cropped_matiere_area.png'
    out_img_debug = 'debug_preprocessed.png'

    start_x = 800
    x_end = 1200

    try:
        # Load image
        img = Image.open(image_path)
        img_width, img_height = img.size
        
        # PREPROCESSING: Enhance the image for better OCR
        print("1. Preprocessing image for better OCR...")
        
        # Convert to OpenCV format
        img_cv = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
        
        # Convert to grayscale
        gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
        
        # Apply threshold to get black text on white background
        _, binary = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
        
        # Optional: Apply slight dilation to make text bolder
        kernel = np.ones((2,2), np.uint8)
        binary = cv2.dilate(binary, kernel, iterations=1)
        
        # Convert back to PIL
        img_preprocessed = Image.fromarray(binary)
        img_preprocessed.save(out_img_debug)
        print(f"   Saved preprocessed image to {out_img_debug}")
        
        # Run OCR on preprocessed image
        print("2. Running OCR to find the vertical bounds of the target row...")
    
        # Try with different PSM modes for better table detection
        custom_config = r'--psm 6 -l fra'  # PSM 6: Assume uniform block of text
        data = pytesseract.image_to_data(
            img_preprocessed, 
            output_type=pytesseract.Output.DICT,
            config=custom_config
        )
        
        y_min_of_two = -1
        y_max_of_two = -1
        limit_x = 300
        
        print("\n=== DEBUG: All detected text in leftmost area ===")
        for i, text in enumerate(data['text']):
            text_stripped = text.strip()
            if text_stripped and data['left'][i] < limit_x:
                x = data['left'][i]
                y = data['top'][i]
                conf = data['conf'][i]
                print(f"  Text: '{text_stripped}' at X={x}, Y={y}, Confidence={conf}")
        
        print("\n=== Searching for target ===")
        for i, text in enumerate(data['text']):
            text_stripped = text.strip()
            if text_stripped == target_char and data['left'][i] < limit_x:
                y_min_of_two = data['top'][i]
                y_max_of_two = data['top'][i] + data['height'][i]
                
                print(f"✓ Found '{target_char}' at X={data['left'][i]}, Y={y_min_of_two}")
                print(f"  Bounding box (Y-range: {y_min_of_two:.0f} to {y_max_of_two:.0f})")
                break
                
        if y_min_of_two == -1:
            print(f"\nERROR: OCR could not detect '{target_char}' in the Sem. column.")
            print("This is a known issue with table OCR. Trying alternative approach...")
            
            # FALLBACK: Manual Y-coordinate approach
            # Crop just the Sem. column and try OCR on it
            sem_crop = img_preprocessed.crop((0, 0, limit_x, img_height))
            sem_crop.save('debug_sem_column.png')
            
            sem_data = pytesseract.image_to_data(
                sem_crop,
                output_type=pytesseract.Output.DICT,
                config=custom_config
            )
            
            print("\n=== Trying OCR on isolated Sem. column ===")
            for i, text in enumerate(sem_data['text']):
                text_stripped = text.strip()
                if text_stripped:
                    print(f"  Text: '{text_stripped}' at Y={sem_data['top'][i]}, Conf={sem_data['conf'][i]}")
                    if text_stripped == target_char:
                        y_min_of_two = sem_data['top'][i]
                        y_max_of_two = sem_data['top'][i] + sem_data['height'][i]
                        print(f"✓ Found '{target_char}' in isolated column!")
                        break
        
        if y_min_of_two == -1:
            print("\nFAILURE: Could not detect the target character with OCR.")
            print("Possible solutions:")
            print("1. Manually provide Y-coordinates")
            print("2. Use a different image preprocessing technique")
            print("3. Try a different OCR engine (e.g., EasyOCR)")
            return None
                
        # Crop and extract
        vsb = 5
        y_min_crop = max(0, int(y_min_of_two) - vsb) 
        
        veb = 200
        y_max_crop = min(img_height, int(y_max_of_two) + veb)
        
        crop_area = (start_x, y_min_crop, x_end, y_max_crop)
        
        print(f"\n3. Cropping region: {crop_area}")
        
        cropped_img = img.crop(crop_area)  # Use original image for final crop
        cropped_img.save(out_img_crop)
        print(f"   Saved cropped area to {out_img_crop}")
        
        print("4. Running OCR on the cropped Matière column...")
        extracted_text = pytesseract.image_to_string(cropped_img, lang='fra').strip()

        if extracted_text:
            cleaned_text = ' '.join(extracted_text.split())
            
            print("\n--- Extraction SUCCESS ---")
            print(f"Matières for semester '{target_char}':")
            print(f"\n{cleaned_text}")
            print(f"\nSaved to: {out_txt}")
            return cleaned_text
        else:
            print("\n--- No text extracted from cropped area ---")
            return None

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        import traceback
        traceback.print_exc()
        return None

pdf = 'pdfs/2.pdf'
out_img = 'page_2_pymupdf_output.png'
num_page = 2

convert_specific_page_to_image(pdf, out_img, num_page)

img = 'page_2_pymupdf_output.png'  
target = '2'

sem = extract_matiere(img, target)


matierat = {
    "matierat1": [],
    "matierat2": []
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
z = "1"
with pdfplumber.open("pdfs/2.pdf") as pdf:
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
                    if (sem == name):
                        z = "2"
                    matiere = {
                        "name":name,
                        "coef":coef,
                        "credit":credit,
                        "notet": notet,
                        "coeff": coeff
                    }
                    matierat[f"matierat{z}"].append(matiere)
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