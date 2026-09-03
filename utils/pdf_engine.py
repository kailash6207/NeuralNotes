import os
import docx

# Support both PyMuPDF (fitz, faster) and PyPDF2
try:
    import fitz  # PyMuPDF
    HAS_FITZ = True
except ImportError:
    HAS_FITZ = False

try:
    import PyPDF2
    HAS_PYPDF2 = True
except ImportError:
    HAS_PYPDF2 = False

def extract_and_chunk(file_path, chunk_size=500):
    """Extracts text from PDF or DOCX files and chunks into uniform word blocks."""
    text = ""
    
    # PDF Processing
    if file_path.lower().endswith('.pdf'):
        if HAS_FITZ:
            try:
                doc = fitz.open(file_path)
                for page in doc:
                    page_text = page.get_text()
                    if page_text:
                        text += page_text + "\n"
            except Exception as e:
                print(f"PyMuPDF error reading {file_path}: {e}")
        elif HAS_PYPDF2:
            try:
                with open(file_path, 'rb') as file:
                    reader = PyPDF2.PdfReader(file)
                    for page in reader.pages:
                        extracted = page.extract_text()
                        if extracted:
                            text += extracted + "\n"
            except Exception as e:
                print(f"PyPDF2 error reading {file_path}: {e}")
        else:
            print("Warning: Neither PyMuPDF nor PyPDF2 is installed. Please install PyMuPDF or PyPDF2.")
            
    # Word DOCX Processing
    elif file_path.lower().endswith('.docx'):
        try:
            doc = docx.Document(file_path)
            for para in doc.paragraphs:
                if para.text:
                    text += para.text + "\n"
        except Exception as e:
            print(f"Error reading DOCX {file_path}: {e}")

    # Chunk the text into uniform word windows
    words = text.split()
    chunks = [' '.join(words[i:i + chunk_size]) for i in range(0, len(words), chunk_size)]
    return chunks
