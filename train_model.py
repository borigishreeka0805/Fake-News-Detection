import pandas as pd
import pickle
import re
import string

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.utils import shuffle

# ---------------------------
# Load Dataset
# ---------------------------

data = pd.read_csv("dataset/news.csv")

# Remove empty rows
data = data.dropna()

# ---------------------------
# Balance Dataset
# ---------------------------

fake = data[data["label"] == 0]
real = data[data["label"] == 1]

min_size = min(len(fake), len(real))

fake = fake.sample(min_size, random_state=42)
real = real.sample(min_size, random_state=42)

data = pd.concat([fake, real])

# Shuffle dataset
data = shuffle(data, random_state=42)

print("Dataset balanced:")
print(data["label"].value_counts())

# ---------------------------
# Text Cleaning
# ---------------------------

def clean_text(text):

    text = text.lower()

    text = re.sub(r"\d+", "", text)

    text = text.translate(str.maketrans("", "", string.punctuation))

    text = re.sub(r"\s+", " ", text)

    return text.strip()


data["text"] = data["text"].apply(clean_text)

X = data["text"]
y = data["label"]

# ---------------------------
# Improved TF-IDF
# ---------------------------

vectorizer = TfidfVectorizer(
    stop_words="english",
    ngram_range=(1,3),
    max_features=20000,
    min_df=2
)

X_vector = vectorizer.fit_transform(X)

# ---------------------------
# Train Test Split
# ---------------------------

X_train, X_test, y_train, y_test = train_test_split(
    X_vector,
    y,
    test_size=0.2,
    random_state=42
)

# ---------------------------
# Logistic Regression Model
# ---------------------------

model = LogisticRegression(
    max_iter=2000
)

model.fit(X_train, y_train)

# ---------------------------
# Model Evaluation
# ---------------------------

pred = model.predict(X_test)

accuracy = accuracy_score(y_test, pred)

print("Model Accuracy:", accuracy)

# ---------------------------
# Save Model
# ---------------------------

pickle.dump(model, open("model.pkl", "wb"))
pickle.dump(vectorizer, open("vectorizer.pkl", "wb"))

print("Model saved successfully")