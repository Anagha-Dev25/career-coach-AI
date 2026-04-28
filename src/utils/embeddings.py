from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re

def calculate_match_score(resume_text, job_desc):
    """
    Calculates a mathematical match percentage between 
    the resume and the job description using Cosine Similarity.
    """
    documents = [resume_text, job_desc]
    vectorizer = TfidfVectorizer().fit_transform(documents)
    vectors = vectorizer.toarray()
    
    # Calculate Cosine Similarity (The 'angle' between the two documents)
    similarity = cosine_similarity([vectors[0]], [vectors[1]])[0][0]
    
    return round(similarity * 100, 2)

def get_missing_keywords(resume_text, job_desc):
    """
    Finds important technical words in the JD that are missing from the Resume.
    """
    # Use Regex to find all words, ignoring case
    jd_words = set(re.findall(r'\w+', job_desc.lower()))
    resume_words = set(re.findall(r'\w+', resume_text.lower()))
    
    # A list of 'High-Value' keywords to look for specifically
    # You can expand this list as your project grows!
    important_keywords = {
        'aws', 'python', 'cybersecurity', 'terraform', 'cloud', 
        'leadership', 'docker', 'kubernetes', 'java', 'sql', 'react'
    }
    
    # Find words that are in (JD + Important List) but NOT in the resume
    missing = (jd_words & important_keywords) - resume_words
    
    return list(missing)