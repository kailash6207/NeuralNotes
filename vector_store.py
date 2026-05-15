import os

# 1. THE NUCLEAR OPTION: Completely disable symlinks BEFORE importing anything else
os.environ['HF_HUB_DISABLE_SYMLINKS'] = '1'
os.environ['HF_HUB_DISABLE_SYMLINKS_WARNING'] = '1'

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# 2. Force a strict ABSOLUTE path so Windows doesn't get confused by "./"
safe_cache_dir = os.path.abspath("local_ai_model")
print(f"Loading AI Model directly into: {safe_cache_dir}")

# 3. Load the model using the safe path
model = SentenceTransformer('all-MiniLM-L6-v2', cache_folder=safe_cache_dir)

def create_embeddings(chunks):
    """Turns a list of text chunks into mathematical vectors."""
    print(f"Converting {len(chunks)} chunks into vectors...")
    embeddings = model.encode(chunks)
    return embeddings

def find_best_match(question, chunks, chunk_embeddings):
    """Finds the chunk of text that best answers the user's question."""
    question_vector = model.encode([question])
    similarities = cosine_similarity(question_vector, chunk_embeddings)[0]
    
    best_index = np.argmax(similarities)
    best_score = similarities[best_index]
    
    return chunks[best_index], best_score

# --- QUICK TEST LOGIC ---
if __name__ == "__main__":
    sample_chunks = [
        "Dr.T.Ilavarasan, Associate Professor, SENSE, VIT. Mail: ilavarasan.t@vit.ac.in",
        "Avoid using mobile phones during lecture and lab sessions.",
        "General course information: Prerequisite – BECE206"
    ]
    
    embeddings = create_embeddings(sample_chunks)
    
    my_question = "What is the prerequisite for this class?"
    print(f"\nQuestion: {my_question}")
    
    best_chunk, score = find_best_match(my_question, sample_chunks, embeddings)
    
    print(f"\nBest Match Found (Score: {score:.2f}):")
    print(best_chunk)