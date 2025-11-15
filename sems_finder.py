from PIL import Image, ImageEnhance, ImageFilter
import pytesseract
import cv2
import numpy as np

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