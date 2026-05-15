# 🧠 NeuralNotes

**NeuralNotes** is an AI-powered academic assistant built specifically for engineering students at **VIT Chennai**. It uses **RAG (Retrieval-Augmented Generation)** to transform static lecture notes and syllabus PDFs into an interactive learning experience.

## 🚀 Key Features
- **ELI5 Concept Explainer:** Simplifies complex topics like VLSI, CMOS, and Signal Processing using intuitive analogies.
- **Automated Quiz Generation:** Creates mock FAT (Final Assessment Test) questions directly from your uploaded documents.
- **Smart Flashcards:** Extracts key technical terms for quick revision.
- **Context-Aware Chat:** Answers questions based *only* on the provided study material to prevent AI hallucinations.

## 🛠️ Technical Architecture
The app follows a modern AI pipeline:
1. **Document Ingestion:** Parses PDFs and Word docs using `PyMuPDF` and `python-docx`.
2. **Vector Embeddings:** Converts text into mathematical vectors for semantic search.
3. **Retrieval Engine:** Finds the most relevant technical context from your notes.
4. **Generation:** Uses **Google Gemini Pro** to synthesize accurate, context-rich answers.

## 💻 Tech Stack
- **Frontend:** Streamlit
- **AI Model:** Google Gemini API
- **Processing:** NumPy, Scikit-Learn (Vector Similarity)
- **Language:** Python 3.x
