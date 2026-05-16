import pickle
import re
import string
from ml.verification_engine import check_fake_domain
from ml.verification_engine import (
    check_newsapi,
    check_google_news,
    fact_check_score,
    check_trusted_source
)


# ------------------------
# Load Model
# ------------------------

with open("model.pkl", "rb") as f:
    model = pickle.load(f)

with open("vectorizer.pkl", "rb") as f:
    vectorizer = pickle.load(f)


# ------------------------
# Clean Text
# ------------------------

def clean_text(text):

    text = text.lower()

    text = re.sub(r"\d+", "", text)

    text = text.translate(str.maketrans("", "", string.punctuation))

    text = " ".join(text.split())

    return text


# ------------------------
# Score Interpretation
# ------------------------

def interpret_score(score):

    if score <= 20:
        return "MOSTLY REAL"

    elif score <= 40:
        return "SUSPICIOUS"

    elif score <= 60:
        return "LIKELY FAKE"

    elif score <= 80:
        return "FAKE NEWS"

    else:
        return "HIGHLY FAKE"


# ------------------------
# Main Prediction Function
# ------------------------

def predict_news(text, url=None):

    # ------------------------
    # Trusted source check
    # ------------------------

    if url:

        if check_trusted_source(url):

            label = "MOSTLY REAL"

            fake_score = 5

            return label, fake_score
        
    if url and check_fake_domain(url):
        return "FAKE NEWS", 85


    # ------------------------
    # Basic validation
    # ------------------------

    if len(text.split()) < 8:
        return "TEXT TOO SHORT", 0


    # ------------------------
    # Clean and vectorize
    # ------------------------

    cleaned = clean_text(text)

    vector = vectorizer.transform([cleaned])


    # ------------------------
    # Model prediction
    # ------------------------

    probabilities = model.predict_proba(vector)[0]

    classes = model.classes_


    # detect which class is fake
    if classes[0] == 1:
        fake_prob = probabilities[0]
    else:
        fake_prob = probabilities[1]


    fake_score = fake_prob * 100


    # ------------------------
    # LIVE VERIFICATION ENGINE
    # ------------------------

    newsapi_hits = check_newsapi(text)

    google_hits = check_google_news(text)

    fact_score = fact_check_score(text)


    # ------------------------
    # Adjust fake score
    # ------------------------

    if newsapi_hits > 10:
        fake_score -= 35

    elif newsapi_hits > 5:
        fake_score -= 25

    elif newsapi_hits > 2:
        fake_score -= 15


    if google_hits > 10:
        fake_score -= 30

    elif google_hits > 5:
        fake_score -= 20

    elif google_hits > 2:
        fake_score -= 10


    fake_score += fact_score


    # ------------------------
    # Normalize score
    # ------------------------

    fake_score = max(0, min(fake_score, 100))

    fake_score = round(fake_score, 2)


    # ------------------------
    # Final label
    # ------------------------

    label = interpret_score(fake_score)


    return label, fake_score