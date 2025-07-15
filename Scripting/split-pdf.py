# split >=80mb pdfs to smaller parts
# pip install PyPDF2
# python split_pdf.py large_file.pdf
# python split_pdf.py large_file.pdf output_folder 80

import os
import sys
from PyPDF2 import PdfWriter, PdfReader

def split_pdf(input_pdf, output_dir, max_size_mb=80):
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Get file size in bytes
    file_size = os.path.getsize(input_pdf)
    max_size = max_size_mb * 1024 * 1024  # Convert MB to bytes

    # If the file is small enough, just copy it
    if file_size <= max_size:
        print(f"File is already ≤ {max_size_mb} MB. No split needed.")
        return

    # Get base name (without extension)
    base_name = os.path.splitext(os.path.basename(input_pdf))[0]

    # Open the PDF
    reader = PdfReader(input_pdf)
    total_pages = len(reader.pages)

    # Start splitting
    start_page = 0
    part_num = 1

    while start_page < total_pages:
        # Initialize a new PDF writer for this part
        writer = PdfWriter()
        part_size = 0
        last_good_page = start_page

        # Add pages until size would exceed max_size or end of PDF
        for page_num in range(start_page, total_pages):
            page = reader.pages[page_num]
            writer.add_page(page)

            # Estimate the current part size
            temp_path = os.path.join(output_dir, f"temp_part_{part_num}.pdf")
            with open(temp_path, "wb") as f:
                writer.write(f)
            current_size = os.path.getsize(temp_path)
            os.remove(temp_path)  # Clean up temp file

            # If current size exceeds max_size, undo the last add
            if current_size > max_size:
                writer = PdfWriter()  # Reset writer
                for p in range(start_page, page_num):  # Add up to the previous page
                    writer.add_page(reader.pages[p])
                last_good_page = page_num  # Next part starts here
                break
            else:
                part_size = current_size
                last_good_page = page_num + 1  # Next part starts after this page

        # Save this part
        if writer.pages:  # Only save if there are pages
            output_pdf = os.path.join(output_dir, f"{base_name}-part-{part_num}.pdf")
            with open(output_pdf, "wb") as f:
                writer.write(f)
            print(f"Created: {output_pdf} (size: {os.path.getsize(output_pdf) / (1024*1024):.2f} MB)")
            part_num += 1

        start_page = last_good_page

    print("PDF split complete.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python split_pdf.py <input.pdf> [output_dir] [max_size_mb]")
        sys.exit(1)

    input_pdf = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "split_pdf_parts"
    max_size_mb = int(sys.argv[3]) if len(sys.argv) > 3 else 80

    split_pdf(input_pdf, output_dir, max_size_mb)
