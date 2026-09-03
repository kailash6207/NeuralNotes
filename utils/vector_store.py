import os

# Disable HuggingFace Hub symlinks on Windows immediately
os.environ['HF_HUB_DISABLE_SYMLINKS'] = '1'
os.environ['HF_HUB_DISABLE_SYMLINKS_WARNING'] = '1'

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# Safe absolute path for local model cache
safe_cache_dir = os.path.abspath("local_ai_model")

# Load model locally
model = SentenceTransformer('all-MiniLM-L6-v2', cache_folder=safe_cache_dir)

def create_embeddings(chunks):
    """Turns a list of text chunks into mathematical vectors."""
    embeddings = model.encode(chunks)
    return embeddings

def find_best_match(question, chunks, chunk_embeddings):
    """Finds the chunk of text that best answers the user's question via cosine similarity."""
    question_vector = model.encode([question])
    similarities = cosine_similarity(question_vector, chunk_embeddings)[0]
    
    best_index = np.argmax(similarities)
    best_score = similarities[best_index]
    
    return chunks[best_index], best_score
