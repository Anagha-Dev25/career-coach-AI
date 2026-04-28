import pypdf

def extract_text_from_pdf(pdf_path):
    """
    Extracts raw text from a PDF file for the AI to process.
    """
    try:
        with open(pdf_path, "rb") as file:
            reader = pypdf.PdfReader(file)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text.strip()
    except Exception as e:
        return f"Error reading PDF: {e}"

if __name__ == "__main__":
    # Quick test - replace with a path to your own resume!
    # print(extract_text_from_pdf("data/raw_resumes/test_resume.pdf"))
    pass