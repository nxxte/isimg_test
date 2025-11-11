import fitz  # PyMuPDF
import os
import easyocr
from PIL import Image
import numpy as np

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
        print(f"Page {page_num} successfully converted and saved as: {output_path}")

    except Exception as e:
        print("\n--- Conversion FAILURE ---")
        print(f"An unexpected error occurred: {e}")

def extract_matiere(image_path, target_char):
    out_txt = 'extracted_matiere.txt'
    out_img_crop = 'cropped_matiere_area.png'

    start_x = 800 
    x_end = 1130 

    reader = easyocr.Reader(['fr'])
    try:
        img = Image.open(image_path)
        img_height = img.size[1]
        
        print("1. Running initial OCR to find the vertical bounds of the target row...")
        results = reader.readtext(image_path, detail=1)
        
        y_min_of_two = -1
        y_max_of_two = -1

        limit_x = 200
        
        for (bbox, text, prob) in results:
            if target_char in text and bbox[0][0] < start_x and \
                bbox[0][0] < limit_x:
                
                all_y_coords = [point[1] for point in bbox]
                
                y_min_of_two = min(all_y_coords) 
                y_max_of_two = max(all_y_coords)
                
                print(f"2. Found '{target_char}' bounding box (Y-range: {y_min_of_two:.0f} to {y_max_of_two:.0f}).")
                break
                
        if y_min_of_two != -1:
            vsb = 5 #vertical start buffer
            y_min_crop = max(0, int(y_min_of_two) - vsb) 
            
            veb = 150
            y_max_crop = min(img_height, int(y_max_of_two) + veb)
            
            crop_area = (start_x, y_min_crop, x_end, y_max_crop)
            
            print(f"3. Cropping region: {crop_area}")
            
            cropped_img = img.crop(crop_area)
            cropped_img.save(out_img_crop)
            print(f"   (Saved cropped area to {out_img_crop} for visual check.)")

            cropped_img_np = np.array(cropped_img) 
            
            print("4. Running second OCR on the cropped Matière column...")
            cropped_results = reader.readtext(cropped_img_np, detail=0) 
            
            extracted_text = ""

            if cropped_results:
                extracted_text = " ".join(cropped_results).strip()

                with open(out_txt, 'w', encoding='utf-8') as f:
                    f.write(extracted_text)

                print("\n--- Extraction SUCCESS ---")
                print(f"The Matière corresponding to the start of index '{target}' is:")
                print(f"**{extracted_text}**")
                print(f"Saved text to: {out_txt}")
            else:
                 print("\n--- Extraction FAILURE ---")
                 print("ERROR: Second OCR run on the cropped area found NO text. Check cropped_matiere_area.png.")

        else:
            print(f"Character '{target_char}' not found in the image or is outside the expected X-range.")

    except FileNotFoundError:
        print(f"Error: The image file '{image_path}' was not found.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

pdf = 'pdfs/2.pdf'
out_img = 'page_2_pymupdf_output.png'
num_page = 2

convert_specific_page_to_image(pdf, out_img, num_page)

img = 'page_2_pymupdf_output.png'  
target = '2'

extract_matiere(img, target)
