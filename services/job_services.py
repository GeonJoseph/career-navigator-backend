import json
import os
import re

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "jobs.json")

# Basic stopwords (keeps logic simple)
STOPWORDS = {
    "and", "or", "the", "is", "a", "an", "with",
    "to", "for", "of", "in", "on", "at", "by",
    "i", "am", "like", "want", "interested"
}

def load_jobs():
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def clean_text(text):
    text = text.lower()
    text = re.sub(r"[^\w\s]", "", text)  # remove punctuation
    return text

def simple_match(user_text):
    jobs = load_jobs()

    user_text = clean_text(user_text)
    user_words = [
        word for word in user_text.split()
        if word not in STOPWORDS
    ]

    scores = []

    for job in jobs:
        score = 0

        title = clean_text(job["title"])
        description = clean_text(job["description"])

        for word in user_words:
            if word in title:
                score += 3   # weight title matches higher
            if word in description:
                score += 1

        scores.append((job["title"], score))

    # Sort by highest score
    scores.sort(key=lambda x: x[1], reverse=True)

    # Only return jobs with positive score
    top_jobs = [job[0] for job in scores if job[1] > 0][:3]

    # If no good match, fallback to top 3
    if not top_jobs:
        top_jobs = [job[0] for job in scores[:3]]

    return top_jobs
