import easyocr
from PIL import Image
import os

# --- Configuration ---
IMAGE_FILE = 'final.png' 
OUTPUT_TEXT_FILE = 'extracted_text.txt'
TARGET_CHARACTER = '2'

# Initialize the OCR reader (runs once)
# Specify the language(s) you need. 'en' for English.
reader = easyocr.Reader(['en'])

try:
    # 1. Load the image
    img = Image.open(IMAGE_FILE)
    width, height = img.size

    # 2. Run OCR
    # 'detail=1' ensures we get the bounding box coordinates
    results = reader.readtext(IMAGE_FILE, detail=1)
    
    crop_start_x = -1
    
    # 3. Search for the target character '2'
    for (bbox, text, prob) in results:
        # Check if the detected text contains our target character
        if TARGET_CHARACTER in text:
            # bbox is [[x1, y1], [x2, y2], [x3, y3], [x4, y4]] (corners)
            # We need the top-left (x1) and top-right (x2) points.
            
            # The rightmost X-coordinate of the detected text block
            # This is typically bbox[1][0] or bbox[2][0]
            # Since we are using the simple bounding box of the whole word/block:
            x_right_of_text_block = int(bbox[1][0])
            
            # If the block is multi-character (e.g., '123'), we need to refine the x_right
            # If you know the '2' is always the last character, this works.
            # For simplicity, we'll use the right edge of the entire text block:
            crop_start_x = x_right_of_text_block
            
            print(f"Found text containing '{TARGET_CHARACTER}' at position: {x_right_of_text_block}")
            
            # Use the first instance found and break the loop
            break
            
    if crop_start_x != -1:
        # 4. Define the Crop Area (Everything to the right of the detected block)
        crop_area = (
            crop_start_x,  # Left: Right edge of the detected text block
            0,             # Top: Top edge of the image
            width,         # Right: Right edge of the image
            height         # Bottom: Bottom edge of the image
        )
        
        # 5. Crop the image
        cropped_img = img.crop(crop_area)
        
        # 6. Perform OCR on the cropped section
        # NOTE: We run OCR again on the cropped PIL image object
        cropped_results = reader.readtext(cropped_img)
        extracted_text = " ".join([text for (bbox, text, prob) in cropped_results])
        
        # 7. Save the extracted text
        with open(OUTPUT_TEXT_FILE, 'w', encoding='utf-8') as f:
            f.write(extracted_text.strip())

        print("\n--- easyocr Results ---")
        print(f"Extracted Text from cropped area:\n{extracted_text.strip()}")
        print(f"Saved text to: {OUTPUT_TEXT_FILE}")

    else:
        print(f"Character '{TARGET_CHARACTER}' not found in the image.")

except FileNotFoundError:
    print(f"Error: The image file '{IMAGE_FILE}' was not found.")
except Exception as e:
    print(f"An unexpected error occurred: {e}")