# 🚀 AI-Resume-Matching-System

## 📌 Overview
AI Resume Analyzer is a machine learning-based application designed to parse resumes, extract key details (such as skills, education, and experience), and classify candidates based on job roles. It leverages **Natural Language Processing (NLP)** and **Machine Learning** to analyze resumes and match candidates to job descriptions effectively.

This AI-powered resume screening system automates candidate shortlisting, helping recruiters quickly identify the most relevant applicants. It also includes a **scoring system** that ranks candidates based on resume quality and relevance to job requirements, making the hiring process more efficient and data-driven.

---

## ✨ Features

✅ **Resume Upload**
- **File Format Support:** Processes resumes in various formats (**PDF, DOCX, TXT**).

✅ **Resume Classification**
- Categorizes resumes into predefined job roles using an **SVC classifier with TF-IDF**.

✅ **Skills Extraction**
- Identifies and extracts key skills mentioned in resumes.

✅ **Skills Recommendation**
- Recommends missing skills to enhance candidate profiles.

✅ **Candidate Scoring System**
- Assigns a score based on **resume quality and relevance**.

✅ **Category-Based Resume Storage**
- Stores resumes under predefined categories like **IT, Finance, Healthcare, etc.**

✅ **AI-Powered Resume Matching**
- Uses **Semantic Search** to match resumes with job descriptions.

✅ **Real-time Candidate Ranking**
- Provides a **Similarity Score** for dynamic ranking of candidates.

---

## 📥 Installation

### Prerequisites
- Python 3.x
- pip
- Virtual environment (optional but recommended)

### Setup Instructions

1. **Clone the Repository:**
   ```sh
   git clone https://github.com/Krutikagadge/resume-analyzer.git
   cd resume-analyzer
   ```

2. **Create and Activate Virtual Environment (Optional):**
   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install Dependencies:**
   ```sh
   pip install -r requirements.txt
   ```

4. **Run the Application:**
   ```sh
   python main_code_file.py
   ```

---

## 🚀 Usage

1️⃣ Upload a resume (**PDF, DOCX, TXT**) via the interface or specify a file path.
2️⃣ The system extracts **skills, education, and experience**.
3️⃣ The classifier assigns a **job category** based on the extracted details.
4️⃣ Recruiters provide a **job description**.
5️⃣ The system ranks the **most suitable candidates** based on the similarity score.
6️⃣ Recruiters can **download candidate resumes**.

---

## 📂 Project Structure
```
AI-Resume-Matching-System/
│
├── Resume_Analyze/
│   ├── main.py
│   ├── courses.py
│   ├── extract_skills.py
│   ├── requirements.txt
│   ├── clf.pkl
│   ├── encoder.pkl
│   ├── tfidf.pkl
│
├── Resume_Matching/
│
├── Job_Matching/
│   ├── Category.py
│   ├── matching.py
│   ├── api.py
│ 
└── README.md    
```

---

## 🔮 Future Enhancements
- Improve text extraction using advanced OCR techniques.
- Expand dataset diversity to improve classification accuracy.
- Implement multi-label classification for resumes spanning multiple job roles.
- Enhance the scoring algorithm for better candidate ranking.

---

## 🖼️ Screenshots

## Comapany Side

### 🔹 Job Description Input
![Job Description Input]([path/to/resume_upload_image.png](https://github.com/Krutikagadge/AI-Resume-Matching-System/blob/master/UI_Images/Job_Description1.jpg))

### 🔹 Candidate Matching Results
![Matching Results]([path/to/matching_results_image.png](https://github.com/Krutikagadge/AI-Resume-Matching-System/blob/master/UI_Images/Job_Description2.jpg))

## Candidate Side

### 🔹 Resume Upload
![Resume_Upload]([path/to/job_description_input_image.png](https://github.com/Krutikagadge/AI-Resume-Matching-System/blob/master/UI_Images/Resume_Analysis1.jpg))

### 🔹 Resume Analysis
![Resume Analysis]([path/to/final_ranking_image.png](https://github.com/Krutikagadge/AI-Resume-Matching-System/blob/master/UI_Images/Resume_Analysis2.jpg))

### 🔹 Skills Extraction & Recommendation
![Skills Extraction & Recommendation]([https://github.com/Krutikagadge/AI-Resume-Matching-System/blob/master/UI_Images/Resume_Analysis3.jpg))

### 🔹 Course Recommendation
![Course Recommendation](https://github.com/Krutikagadge/AI-Resume-Matching-System/blob/master/UI_Images/Resume_Analysis4.jpg))


---

🚀 **Make hiring faster, smarter, and more efficient with AI-Resume-Matching-System!**
