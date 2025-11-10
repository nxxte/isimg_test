from PIL import Image, ImageDraw

# --- Configuration ---
IMAGE_FILE = 'pdf_images/page_2.png' # Your stitched image file
PREVIEW_FILE = 'crop_preview.png'     # The file where the marked image will be saved
FINAL_CROP_FILE = 'final.png'
# Define your desired crop coordinates (left, top, right, bottom)
# Example: Cropping a 200x200 area starting at (100, 50)
CROP_BOX = (100, 200, 800, 2000) 
# Remember: Coordinates are 0-indexed from the top-left corner.

def crop_image(input_path, output_path, crop_box_coords):
    """Crops an image based on the provided bounding box coordinates."""
    try:
        img = Image.open(input_path)
        
        # The core cropping operation
        cropped_img = img.crop(crop_box_coords)
        
        cropped_img.save(output_path)
        print(f"\nSUCCESS: Image cropped and saved to: {output_path}")
        
    except FileNotFoundError:
        print(f"Error: The input file '{input_path}' was not found.")
    except Exception as e:
        print(f"An error occurred during cropping: {e}")

try:
    # 1. Open the image
    img = Image.open(IMAGE_FILE).convert("RGB") 
    
    # 2. Get the dimensions for reference
    width, height = img.size
    print(f"Original Image Dimensions: {width}x{height}")
    print(f"Planned Crop Box (L, T, R, B): {CROP_BOX}")

    # 3. Create a drawing object
    draw = ImageDraw.Draw(img)
    
    # 4. Draw the bounding box
    # Arguments: (left, top, right, bottom), outline color, line width
    draw.rectangle(
        CROP_BOX, 
        outline="red", 
        width=3 # You can change the line width
    )

    # 5. Save the preview image
    img.save(PREVIEW_FILE)
    crop_image(IMAGE_FILE, FINAL_CROP_FILE, CROP_BOX)
    print(f"\nSaved preview image with red box to: {PREVIEW_FILE}")
    print("Open this file to see where your image will be cropped.")

    # Optional: Display the image immediately (requires a display environment)
    # img.show() 

except FileNotFoundError:
    print(f"Error: The file '{IMAGE_FILE}' was not found.")
except Exception as e:
    print(f"An unexpected error occurred: {e}")