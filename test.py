from PIL import Image
import pytesseract

def extract_matiere(image_path, target_char):
    out_txt = 'extracted_matiere.txt'
    out_img_crop = 'cropped_matiere_area.png'

    start_x = 800
    x_end = 1200

    try:
        # Load image
        img = Image.open(image_path)
        img_width, img_height = img.size
        
        print("1. Running OCR to find the vertical bounds of the target row...")
        
        # Run OCR directly on original image - no preprocessing
        data = pytesseract.image_to_data(
            img, 
            output_type=pytesseract.Output.DICT,
            lang='fra'
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
            print("Trying alternative approach - isolated Sem. column...")
            
            # FALLBACK: Crop just the Sem. column and try OCR on it
            sem_crop = img.crop((0, 0, limit_x, img_height))
            sem_crop.save('debug_sem_column.png')
            
            sem_data = pytesseract.image_to_data(
                sem_crop,
                output_type=pytesseract.Output.DICT,
                lang='fra'
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
            return None
                
        # Crop and extract
        vsb = 5
        y_min_crop = max(0, int(y_min_of_two) - vsb) 
        
        veb = 200
        y_max_crop = min(img_height, int(y_max_of_two) + veb)
        
        crop_area = (start_x, y_min_crop, x_end, y_max_crop)
        
        print(f"\n2. Cropping region: {crop_area}")
        
        cropped_img = img.crop(crop_area)
        cropped_img.save(out_img_crop)
        print(f"   Saved cropped area to {out_img_crop}")
        
        print("3. Running OCR on the cropped Matière column...")
        extracted_text = pytesseract.image_to_string(cropped_img, lang='fra').strip()

        if extracted_text:
            with open(out_txt, 'w', encoding='utf-8') as f:
                f.write(extracted_text)
            
            print("\n--- Extraction SUCCESS ---")
            print(f"Matières for semester '{target_char}':")
            print(f"\n{extracted_text}")
            print(f"\nSaved to: {out_txt}")
            return extracted_text
        else:
            print("\n--- No text extracted from cropped area ---")
            return None

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        import traceback
        traceback.print_exc()
        return None

# Usage
result = extract_matiere('page_2_pymupdf_output.png', '2')