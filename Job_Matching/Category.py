#!/usr/bin/env python
# coding: utf-8

# In[1]:


import os
import fitz  # PyMuPDF
import shutil

# Define input and output directories
INPUT_DIR = "raw_resumes/"  # Folder containing PDF resumes
OUTPUT_DIR = "processed_resumes/"  # Folder to store text resumes

# Define categories
categories = [
    "ACCOUNTANT", "ADVOCATE", "AGRICULTURE", "APPAREL", "ARTS", "AUTOMOBILE",
    "AVIATION", "BANKING", "BPO", "BUSINESS-DEVELOPMENT", "CHEF", "CONSTRUCTION",
    "CONSULTANT", "DESIGNER", "DIGITAL-MEDIA", "ENGINEERING", "FINANCE", "FITNESS",
    "HEALTHCARE", "HR", "INFORMATION-TECHNOLOGY", "PUBLIC-RELATIONS", "SALES", "TEACHER"
]

# Ensure category directories exist
for category in categories:
    os.makedirs(os.path.join(OUTPUT_DIR, category), exist_ok=True)

def extract_text_from_pdf(pdf_path):
    """Extracts text from a PDF file."""
    doc = fitz.open(pdf_path)
    text = "\n".join(page.get_text() for page in doc)
    return text.strip()

def process_resumes():
    """Processes all PDFs, extracts text, and stores them in category-wise folders."""
    for category in categories:
        category_dir = os.path.join(INPUT_DIR, category)
        if not os.path.exists(category_dir):
            print(f"Skipping {category} (No resumes found)")
            continue
        
        for file in os.listdir(category_dir):
            if file.endswith(".pdf"):
                pdf_path = os.path.join(category_dir, file)
                text = extract_text_from_pdf(pdf_path)

                if text:
                    # Save extracted text
                    txt_filename = os.path.splitext(file)[0] + ".txt"
                    output_path = os.path.join(OUTPUT_DIR, category, txt_filename)
                    with open(output_path, "w", encoding="utf-8") as f:
                        f.write(text)
                    print(f"Processed: {file} → {output_path}")

if __name__ == "__main__":
    process_resumes()


# In[2]:


import os
import numpy as np
from sentence_transformers import SentenceTransformer

# Load pre-trained sentence embedding model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Define input and output directories
INPUT_DIR = "processed_resumes/"
EMBEDDING_DIR = "resume_embeddings/"

# Ensure embedding directory exists
os.makedirs(EMBEDDING_DIR, exist_ok=True)

def generate_embedding(text):
    """Generates a numerical embedding for the given resume text."""
    return model.encode(text)

def process_embeddings():
    """Processes all resumes, generates embeddings, and stores them category-wise."""
    for category in os.listdir(INPUT_DIR):
        category_path = os.path.join(INPUT_DIR, category)
        embedding_path = os.path.join(EMBEDDING_DIR, f"{category}_embeddings.npy")
        
        if not os.path.isdir(category_path):
            continue
        
        resume_embeddings = []
        file_names = []

        for file in os.listdir(category_path):
            if file.endswith(".txt"):
                txt_path = os.path.join(category_path, file)
                with open(txt_path, "r", encoding="utf-8") as f:
                    text = f.read().strip()
                
                if text:
                    embedding = generate_embedding(text)
                    resume_embeddings.append(embedding)
                    file_names.append(file)

        if resume_embeddings:
            np.save(embedding_path, np.array(resume_embeddings))  # Save embeddings as .npy file
            np.save(os.path.join(EMBEDDING_DIR, f"{category}_filenames.npy"), np.array(file_names))
            print(f"✅ Saved {len(resume_embeddings)} embeddings for category: {category}")

if __name__ == "__main__":
    process_embeddings()


# In[3]:


import faiss
import numpy as np
import os

# Define embedding directory
EMBEDDING_DIR = "resume_embeddings/"
FAISS_DIR = "faiss_indexes/"

# Ensure FAISS index directory exists
os.makedirs(FAISS_DIR, exist_ok=True)

def create_faiss_index():
    """Loads resume embeddings and stores them in a FAISS index category-wise."""
    for file in os.listdir(EMBEDDING_DIR):
        if file.endswith("_embeddings.npy"):
            category = file.replace("_embeddings.npy", "")
            embeddings_path = os.path.join(EMBEDDING_DIR, file)
            filenames_path = os.path.join(EMBEDDING_DIR, f"{category}_filenames.npy")

            # Load embeddings and filenames
            embeddings = np.load(embeddings_path).astype('float32')
            filenames = np.load(filenames_path)

            # Create FAISS index
            dimension = embeddings.shape[1]  # Get embedding size (e.g., 384)
            index = faiss.IndexFlatL2(dimension)  # L2 distance (Euclidean)
            index.add(embeddings)  # Add embeddings to index

            # Save FAISS index
            faiss.write_index(index, os.path.join(FAISS_DIR, f"{category}_index.faiss"))
            np.save(os.path.join(FAISS_DIR, f"{category}_filenames.npy"), filenames)

            print(f"✅ Stored {len(embeddings)} embeddings in FAISS for category: {category}")

if __name__ == "__main__":
    create_faiss_index()


# In[8]:


import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
import os

# Load Sentence Transformer Model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Define directories
FAISS_DIR = "faiss_indexes/"

def get_job_embedding(job_description):
    """Generate embedding for the given job description"""
    return model.encode(job_description).astype('float32')

def match_candidates(job_description, category, top_n=10):
    """Find top matching resumes based on job description and category"""
    index_path = os.path.join(FAISS_DIR, f"{category}_index.faiss")
    filenames_path = os.path.join(FAISS_DIR, f"{category}_filenames.npy")

    # Check if category index exists
    if not os.path.exists(index_path) or not os.path.exists(filenames_path):
        return {"error": f"No resumes found for category: {category}"}

    # Load FAISS index and filenames
    index = faiss.read_index(index_path)
    filenames = np.load(filenames_path)

    # Convert job description into an embedding
    job_embedding = get_job_embedding(job_description).reshape(1, -1)

    # Search for top matches in FAISS
    distances, indices = index.search(job_embedding, top_n)

    # Prepare response with ranked candidates
    matched_candidates = []
    for i, idx in enumerate(indices[0]):
        matched_candidates.append({
            "rank": i + 1,
            "resume_file": filenames[idx],
            "match_score": round(1 - distances[0][i], 4)  # Convert L2 distance to similarity score
        })

    return matched_candidates



# In[9]:


# Example usage
if __name__ == "__main__":
    category = "ENGINEERING"  # Example: Recruiter selects category
    job_description = "Looking for a software engineer with experience in Python and Machine Learning."

    results = match_candidates(job_description, category, top_n=5)

    # Print output in a readable format
    print("\nTop Matching Candidates:\n")
    for candidate in results:
        print(f"Rank: {candidate['rank']}")
        print(f"Resume File: {candidate['resume_file']}")
        print(f"Match Score: {candidate['match_score']}\n")

