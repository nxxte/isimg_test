import pdfplumber


with pdfplumber.open("2.pdf") as pdf:
    page = pdf.pages[0]
    
    # This generates an image where pdfplumber draws the lines it detects.
    # Look at the bottom of the image for coordinates.
    page.to_image(force_mediabox=True).debug_tablefinder().save("debug_table_finder.png")