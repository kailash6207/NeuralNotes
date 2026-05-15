import os
from google import genai
from utils.pdf_engine import extract_and_chunk
from utils.vector_store import create_embeddings, find_best_match

# --- 1. SETUP YOUR AI TUTOR ---
GOOGLE_API_KEY = "YOUR_API_KEY_HERE" # Paste your actual API key here
client = genai.Client(api_key=GOOGLE_API_KEY)

def study_session():
    print("Initializing Master Study Assistant...")
    
    # --- 2. LOAD THE MEMORY (Multi-Document Retrieval) ---
    upload_dir = "uploads"
    
    # Check if directory exists
    if not os.path.exists(upload_dir):
        print(f"Error: The directory '{upload_dir}' does not exist.")
        return

    pdf_files = [f for f in os.listdir(upload_dir) if f.endswith(".pdf")]
    
    if not pdf_files:
        print(f"Please put at least one PDF in the '{upload_dir}' folder!")
        return
        
    all_chunks = []
    print(f"Found {len(pdf_files)} PDFs. Building the knowledge base...")
    
    # Loop through every PDF in the folder
    for pdf_file in pdf_files:
        pdf_path = os.path.join(upload_dir, pdf_file)
        print(f" -> Reading {pdf_file}...")
        try:
            chunks = extract_and_chunk(pdf_path)
            all_chunks.extend(chunks) # Add these chunks to our master list
        except Exception as e:
            print(f"    Skipping {pdf_file} due to read error: {e}")
            
    if not all_chunks:
        print("Failed to extract text from the provided documents.")
        return
        
    print(f"\nSuccess! Broken down into {len(all_chunks)} total chunks.")
    
    # Create vectors for the entire combined knowledge base
    embeddings = create_embeddings(all_chunks)
    
    print("\n" + "="*50)
    print(f"✅ Ready! Studying {len(pdf_files)} documents simultaneously.")
    print("Type 'quit' to end the session.")
    print("="*50 + "\n")
    
    # --- 3. THE CHAT LOOP ---
    while True:
        question = input("You: ")
        if question.lower() == 'quit':
            break
            
        print("Thinking...")
        
        # Search across all documents at once
        best_chunk, score = find_best_match(question, all_chunks, embeddings)
        
        prompt = f"""
        You are an expert engineering tutor helping a university student study for their exams.
        Answer the student's question based ONLY on the provided context from their class notes.
        If the answer is not in the notes, say "I don't see the answer to that in these notes."
        
        Class Notes Context:
        {best_chunk}
        
        Student's Question:
        {question}
        """
        
        try:
            response = client.models.generate_content(
                model='gemini-flash-latest', 
                contents=prompt
            )
            print(f"\nTutor: {response.text}\n")
        except Exception as e:
            print(f"\nAPI Error: {e}\n")

if __name__ == "__main__":
    # Fix for Windows symlink warnings
    os.environ['HF_HUB_DISABLE_SYMLINKS'] = '1'
    os.environ['HF_HUB_DISABLE_SYMLINKS_WARNING'] = '1'
    
    study_session()