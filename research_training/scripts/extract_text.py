import fitz
from pathlib import Path
import re

# Project folders
PDF_DIR = Path("../pdfs")
OUTPUT_DIR = Path("../extracted_text")

# Create output folder if it doesn't exist
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def clean_text(text):
    # Remove excessive spaces
    text = re.sub(r"[ \t]+", " ", text)

    # Reduce excessive blank lines
    text = re.sub(r"\n\s*\n+", "\n\n", text)

    # Remove spaces at the beginning/end of lines
    lines = [line.strip() for line in text.splitlines()]

    text = "\n".join(lines)

    return text.strip()


def extract_pdf(pdf_path):
    print(f"Processing: {pdf_path.name}")

    document = fitz.open(pdf_path)

    all_text = []

    for page_number, page in enumerate(document, start=1):
        text = page.get_text("text")

        if text.strip():
            all_text.append(
                f"\n--- PAGE {page_number} ---\n{text}"
            )

    document.close()

    return clean_text("\n".join(all_text))


# Process every PDF
pdf_files = list(PDF_DIR.glob("*.pdf"))

print(f"Found {len(pdf_files)} PDF files.")

for pdf_path in pdf_files:

    try:
        text = extract_pdf(pdf_path)

        output_file = OUTPUT_DIR / f"{pdf_path.stem}.txt"

        output_file.write_text(
            text,
            encoding="utf-8"
        )

        print(f"Saved: {output_file}")

    except Exception as e:
        print(f"ERROR processing {pdf_path.name}: {e}")


print("\nDone!")