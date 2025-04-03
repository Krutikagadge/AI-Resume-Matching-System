import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
import os
import logging

# ✅ Configure Logging
logging.basicConfig(level=logging.INFO)

# ✅ Load Sentence Transformer Model
model = SentenceTransformer('all-MiniLM-L6-v2')

# ✅ Define directories
FAISS_DIR = "faiss_indexes/"

def get_job_embedding(job_description):
    """
    Generate embedding for the given job description using Sentence Transformer.
    """
    return model.encode(job_description).astype('float32')

def match_candidates(job_description, category, top_n=10):
    """
    Find top matching resumes based on job description and category using FAISS.
    """
    index_path = os.path.join(FAISS_DIR, f"{category}_index.faiss")
    filenames_path = os.path.join(FAISS_DIR, f"{category}_filenames.npy")

    # ✅ Check if category index exists
    if not os.path.exists(index_path) or not os.path.exists(filenames_path):
        logging.error(f"FAISS index or filenames not found for category: {category}")
        return {"error": f"No resumes found for category: {category}"}

    # ✅ Load FAISS index and filenames
    try:
        index = faiss.read_index(index_path)
        filenames = np.load(filenames_path)
    except Exception as e:
        logging.error(f"Error loading FAISS index or filenames: {str(e)}")
        return {"error": "Failed to load resume index"}

    # ✅ Convert job description into an embedding
    job_embedding = get_job_embedding(job_description).reshape(1, -1)

    # ✅ Search for top matches in FAISS
    distances, indices = index.search(job_embedding, top_n)

    # ✅ Prepare response with ranked candidates
    matched_candidates = []
    for i, idx in enumerate(indices[0]):
        if idx < len(filenames):  # Ensure index is within range
            matched_candidates.append({
                "rank": i + 1,
                "resume_file": filenames[idx].replace(".txt", ".pdf"),  # Convert .txt to .pdf
                "match_score": round((1 - distances[0][i]) * 100, 2)  # Convert score to percentage
            })
        else:
            logging.warning(f"Invalid index: {idx}, skipping entry.")

    return matched_candidates


# ✅ Example usage (for debugging)
if __name__ == "__main__":
    category = "ENGINEERING"  # Example: Recruiter selects category
    job_description = "Looking for a software engineer with experience in Python and Machine Learning."

    results = match_candidates(job_description, category, top_n=5)

    # Print output in a readable format
    print("\n🔹 Top Matching Candidates:\n")
    for candidate in results:
        print(f"🏅 Rank: {candidate['rank']}")
        print(f"📄 Resume File: {candidate['resume_file']}")
        print(f"✅ Match Score: {candidate['match_score']}%\n")
