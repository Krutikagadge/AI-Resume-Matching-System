import pandas as pd
import re
from collections import defaultdict

# Load dataset
df = pd.read_csv('UpdatedResumeDataSet.csv')

# Define skill keywords for different categories
skill_keywords = {
    "Data Science": ["machine learning", "deep learning", "python", "r", "sql", "tensorflow", "pandas", "numpy", "scikit-learn", "matplotlib", "seaborn"],
    "Software Development": ["java", "c++", "c#", "javascript", "git", "react", "angular", "docker", "kubernetes", "flask", "django"],
    "Finance": ["excel", "financial modeling", "accounting", "risk analysis", "budgeting", "forecasting", "investment analysis", "derivatives"],
    "Marketing": ["seo", "social media", "google ads", "content marketing", "branding", "market research", "email marketing", "ppc"],
    "Networking": ["tcp/ip", "firewall", "vpn", "dns", "routing", "switching", "network security", "lan", "wan", "cloud computing"]
}

# Function to clean resume text
def clean_text(text):
    if isinstance(text, str):
        return re.sub(r'\W+', ' ', text.lower())  # Remove special characters and convert to lowercase
    return ""

# Function to extract skills from resume text
def extract_skills(text):
    detected_skills = set()
    text = clean_text(text)
    
    for category, skills in skill_keywords.items():
        for skill in skills:
            # Use regex for exact word match
            if re.search(r'\b' + re.escape(skill.lower()) + r'\b', text):
                detected_skills.add(skill)  # Keep original skill format
    
    return list(detected_skills)

# Process resumes and generate a skills dataset
skill_dataset = defaultdict(list)

for _, row in df.iterrows():
    category = row.get("Category", "").strip()
    resume_text = row.get("Resume", "")
    
    # Extract skills from resume regardless of category
    skills = extract_skills(resume_text)
    
    if skills:  # Only store if skills are found
        skill_dataset[category].extend(skills)

# Remove duplicates and ensure correct formatting
for category in skill_dataset:
    skill_dataset[category] = list(set(skill_dataset[category]))

# Convert to DataFrame and save
skill_df = pd.DataFrame(skill_dataset.items(), columns=["Category", "Skills"])
skill_df["Skills"] = skill_df["Skills"].apply(lambda x: ", ".join(x))  # Convert list to comma-separated string

skill_df.to_csv("Extracted_Skills.csv", index=False)

print("✅ Skill dataset extracted and saved as Extracted_Skills.csv")




