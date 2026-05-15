import PyPDF2
import docx  # The new Word Doc library

def extract_and_chunk(file_path, chunk_size=500):
    text = ""
    
    # Check if it's a PDF
    if file_path.lower().endswith('.pdf'):
        try:
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                for page in reader.pages:
                    extracted = page.extract_text()
                    if extracted:
                        text += extracted + "\n"
        except Exception as e:
            print(f"Error reading PDF {file_path}: {e}")
            
    # Check if it's a Word Doc
    elif file_path.lower().endswith('.docx'):
        try:
            doc = docx.Document(file_path)
            for para in doc.paragraphs:
                if para.text:
                    text += para.text + "\n"
        except Exception as e:
            print(f"Error reading DOCX {file_path}: {e}")

    # Chunk the text so the AI can digest it
    words = text.split()
    chunks = [' '.join(words[i:i + chunk_size]) for i in range(0, len(words), chunk_size)]
    return chunks