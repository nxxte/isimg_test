from pdf2image import convert_from_path
from PIL import Image
import os

# --- Configuration ---
PDF_FILE = '2.pdf' # Replace with the path to your PDF file
OUTPUT_IMAGE_NAME = 'combined_pdf_pages.png' # Name of the final stitched image
DPI = 200 # Resolution for converting PDF pages (higher = better quality, larger file)
PADDING = 10 # Pixels between pages in the combined image

try:
    # 1. Convert each PDF page to a Pillow Image object
    images = convert_from_path(PDF_FILE, dpi=DPI)

    if not images:
        print("No pages found in the PDF or an error occurred during conversion.")
    else:
        # Determine the maximum width among all pages
        max_width = 0
        for img in images:
            if img.width > max_width:
                max_width = img.width

        # Calculate the total height required for the combined image
        # This includes all page heights plus padding between them
        total_height = sum(img.height for img in images) + (len(images) - 1) * PADDING

        # Create a new blank image with the calculated dimensions
        # 'RGBA' mode supports transparency, 'RGB' for opaque images
        combined_image = Image.new('RGB', (max_width, total_height), color='white') # You can change color

        # Paste each page onto the combined image
        y_offset = 0
        for img in images:
            # Paste the current page, centered horizontally if pages have different widths
            x_offset = (max_width - img.width) // 2
            combined_image.paste(img, (x_offset, y_offset))
            y_offset += img.height + PADDING # Move down for the next page + padding

        # Save the final combined image
        combined_image.save(OUTPUT_IMAGE_NAME, 'PNG') # You can also use 'JPEG'
        
        print(f"All pages combined and saved to: {OUTPUT_IMAGE_NAME}")
        
except Exception as e:
    print(f"An error occurred: {e}")
    print("Please ensure Poppler is installed and its 'bin' directory is in your system's PATH.")
    print("Also, check that the PDF_FILE path is correct.")