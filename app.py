import os
import random
import json
import streamlit as st
from google import genai
from utils.pdf_engine import extract_and_chunk
from utils.vector_store import create_embeddings, find_best_match

# Fix the Windows bug immediately
os.environ['HF_HUB_DISABLE_SYMLINKS'] = '1'
os.environ['HF_HUB_DISABLE_SYMLINKS_WARNING'] = '1'

# --- SETUP ---
GOOGLE_API_KEY = "YOUR_API_KEY_HERE" # PASTE YOUR WORKING KEY HERE
client = genai.Client(api_key=GOOGLE_API_KEY)

st.set_page_config(page_title="FAT Prep Tutor", page_icon="🎓", layout="wide")

# --- MEMORY SYSTEM ---
HISTORY_FILE = "chat_history.json"

def load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r") as f:
                return json.load(f)
        except:
            return []
    return []

def save_history(messages):
    with open(HISTORY_FILE, "w") as f:
        json.dump(messages, f)

if "messages" not in st.session_state:
    st.session_state.messages = load_history()

# --- INITIALIZE THE BRAIN ---
@st.cache_resource
def load_knowledge_base():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    upload_dir = os.path.join(base_dir, "uploads")
    os.makedirs(upload_dir, exist_ok=True) 
        
    files = [f for f in os.listdir(upload_dir) if f.endswith((".pdf", ".docx"))]
    if not files:
        return None, None
        
    all_chunks = []
    for file_name in files:
        file_path = os.path.join(upload_dir, file_name)
        chunks = extract_and_chunk(file_path)
        if chunks:
            all_chunks.extend(chunks)
            
    if all_chunks:
        embeddings = create_embeddings(all_chunks)
        return all_chunks, embeddings
    return None, None

with st.spinner("Powering up the Brain..."):
    chunks, embeddings = load_knowledge_base()

# --- LEFT SIDEBAR UI ---
with st.sidebar:
    st.header("⚙️ Control Panel")
    
    # 1. In-App File Uploader
    st.subheader("📁 Upload New Syllabus")
    uploaded_files = st.file_uploader("Drop PDF or Word files here", type=['pdf', 'docx'], accept_multiple_files=True)
    
    if uploaded_files:
        for file in uploaded_files:
            save_path = os.path.join("uploads", file.name)
            with open(save_path, "wb") as f:
                f.write(file.getbuffer())
        st.success("Files saved! Click below to process them.")
        if st.button("🔄 Reload Brain"):
            st.cache_resource.clear()
            st.rerun()

    st.divider()
    
    # 2. STUDY TOOLS
    st.subheader("🛠️ Study Tools")
    
    if st.button("📝 Generate Practice Exam", use_container_width=True):
        st.session_state.trigger_quiz = True
        
    if st.button("📇 Generate Flashcards", use_container_width=True):
        st.session_state.trigger_flashcards = True

    if len(st.session_state.messages) > 0 and st.session_state.messages[-1]["role"] == "assistant":
        eli5_target = st.text_input("Target concept (Optional):", placeholder="e.g., Question 6")
        if st.button("👶 Simplify Concept (ELI5)", use_container_width=True):
            st.session_state.trigger_eli5 = True
            st.session_state.eli5_target = eli5_target
            
    st.divider()
    
    # UPGRADED CLEAR BUTTON (Wipes the hard drive too)
    if st.button("🧹 Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        if os.path.exists(HISTORY_FILE):
            os.remove(HISTORY_FILE)
        st.rerun()

# --- MAIN CHAT UI ---
st.title("🎓 Engineering Study Assistant")

if not chunks:
    st.info("👋 Welcome! Please upload your syllabus PDFs or Word Docs in the sidebar to get started.")
    st.stop()

# --- HANDLE FLASHCARDS ---
if getattr(st.session_state, 'trigger_flashcards', False):
    st.session_state.trigger_flashcards = False
    sample_text = "\n".join(random.sample(chunks, min(3, len(chunks))))
    flashcard_prompt = f"Based ONLY on the following class notes, generate 5 high-yield flashcards...\n\n**Q:** [Question]\n\n**A:** [Short Answer]\n\n---\nContext: {sample_text}"
    
    st.session_state.messages.append({"role": "user", "content": "*(Requested Flashcards)*"})
    with st.chat_message("assistant"):
        with st.spinner("Building flashcard deck..."):
            response = client.models.generate_content(model='gemini-flash-latest', contents=flashcard_prompt)
            st.markdown("### 📇 Your Custom Flashcard Deck")
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
            save_history(st.session_state.messages) # Save to memory
            st.rerun()

# --- HANDLE QUIZ ---
if getattr(st.session_state, 'trigger_quiz', False):
    st.session_state.trigger_quiz = False
    sample_text = "\n".join(random.sample(chunks, min(4, len(chunks))))
    quiz_prompt = f"Based ONLY on the following text from my class notes, generate a 10-question multiple-choice practice quiz. Format each question using STRICT Markdown lists so it renders correctly on the web. It MUST look exactly like this, with an empty line between the question and the options:\n\n**1. [Insert Question Here]**\n* A) [Option 1]\n* B) [Option 2]\n* C) [Option 3]\n* D) [Option 4]\n\nDo NOT reveal the answers immediately. Put the Answer Key with brief explanations at the very bottom of the quiz.\nContext: {sample_text}"
    
    st.session_state.messages.append({"role": "user", "content": "*(Requested a practice exam)*"})
    with st.chat_message("assistant"):
        with st.spinner("Generating 10-question mock exam..."):
            response = client.models.generate_content(model='gemini-flash-latest', contents=quiz_prompt)
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
            save_history(st.session_state.messages) # Save to memory
            st.rerun()

# --- HANDLE ELI5 ---
if getattr(st.session_state, 'trigger_eli5', False):
    st# --- HANDLE ELI5 ---
if getattr(st.session_state, 'trigger_eli5', False):
    st.session_state.trigger_eli5 = False
    target = getattr(st.session_state, 'eli5_target', "")
    
    # 1. Search backward through the chat memory to find the last thing the AI said
    last_ai_text = ""
    for msg in reversed(st.session_state.messages):
        if msg["role"] == "assistant":
            last_ai_text = msg["content"]
            break
            
    # 2. Inject that exact text into the prompt so the AI actually knows what you are talking about
    if target:
        concept_to_explain = f"Find the concept related to '{target}' in the following text:\n\n{last_ai_text}\n\nNow, explain that specific concept."
    else:
        concept_to_explain = last_ai_text
        
    eli5_prompt = f"""
    Rewrite this engineering concept using a simple, real-world analogy so a beginner can understand it. 
    
    STRICT ENGINEERING GUARDRAIL: Before you output the analogy, double-check all mathematical relationships, equations, and logic (e.g., additions vs. subtractions) against standard engineering principles to ensure they are 100% accurate. Do not alter the core mathematical truth to make the analogy fit.
    
    Concept to explain:
    {concept_to_explain}
    """
    
    st.session_state.messages.append({"role": "user", "content": f"*(Requested a simpler explanation for: {target if target else 'Last Answer'})*"})
    with st.chat_message("assistant"):
        with st.spinner("Simplifying..."):
            response = client.models.generate_content(model='gemini-flash-latest', contents=eli5_prompt)
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
            save_history(st.session_state.messages) # Save to memory
            st.rerun()

# --- RENDER CHAT ---
for message in st.session_state.messages:
    if message["content"] not in ["*(Requested a practice exam)*", "*(Requested a simpler explanation)*", "*(Requested Flashcards)*"]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# --- HANDLE Q&A ---
user_question = st.chat_input("Ask a question about your notes...")

if user_question:
    with st.chat_message("user"):
        st.markdown(user_question)
    
    st.session_state.messages.append({"role": "user", "content": user_question})
    
    with st.chat_message("assistant"):
        with st.spinner("Searching notes..."):
            best_chunk, score = find_best_match(user_question, chunks, embeddings)
            prompt = f"Answer the user's question based ONLY on this context from their notes. If it's not in the notes, say you don't know.\n\nContext: {best_chunk}\n\nQuestion: {user_question}"
            
            try:
                response = client.models.generate_content(model='gemini-flash-latest', contents=prompt)
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
                save_history(st.session_state.messages) # Save to memory
                st.rerun()
            except Exception as e:
                st.error(f"API Error: {e}")