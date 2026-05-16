from flask import Flask, render_template, request, redirect, session, jsonify
from flask_bcrypt import Bcrypt
from database.db import users_collection, history_collection
from ml.predict import predict_news
from ml.verification_engine import check_trusted_source
from newspaper import Article
import datetime
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

app.secret_key = "hackathon_secret_key"

bcrypt = Bcrypt(app)


# ------------------------
# Home
# ------------------------

@app.route("/")
def home():
    return render_template("index.html")


# ------------------------
# Signup
# ------------------------

@app.route("/signup", methods=["GET", "POST"])
def signup():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        user = users_collection.find_one({"email": email})

        if user:
            return "User already exists"

        hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")

        users_collection.insert_one({
            "email": email,
            "password": hashed_password
        })

        return redirect("/login")

    return render_template("signup.html")


# ------------------------
# Login
# ------------------------

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        user = users_collection.find_one({"email": email})

        if user and bcrypt.check_password_hash(user["password"], password):

            session["user"] = email

            return redirect("/dashboard")

        return "Invalid credentials"

    return render_template("login.html")


# ------------------------
# Logout
# ------------------------

@app.route("/logout")
def logout():

    session.pop("user", None)

    return redirect("/")


# ------------------------
# Dashboard
# ------------------------

@app.route("/dashboard")
def dashboard():

    if "user" not in session:
        return redirect("/login")

    return render_template("dashboard.html")


# ------------------------
# Detect Page
# ------------------------

@app.route("/detect")
def detect():

    if "user" not in session:
        return redirect("/login")

    return render_template("detect.html")


# ------------------------
# Text Prediction
# ------------------------

@app.route("/predict", methods=["POST"])
def predict():

    if "user" not in session:
        return jsonify({"error": "Unauthorized"})

    news_text = request.form.get("news")

    label, score = predict_news(news_text)

    history_collection.insert_one({

        "email": session["user"],
        "news": news_text,
        "prediction": label,
        "confidence": score,
        "date": datetime.datetime.now()

    })

    return jsonify({
        "prediction": label,
        "confidence": score
    })


# ------------------------
# URL Prediction
# ------------------------

@app.route("/predict_url", methods=["POST"])
def predict_url():

    if "user" not in session:
        return jsonify({"error": "Unauthorized"})

    url = request.form.get("url")

    # Trusted source check
    if check_trusted_source(url):

        label = "MOSTLY REAL"
        score = 5

        history_collection.insert_one({
            "email": session["user"],
            "news": url,
            "prediction": label,
            "confidence": score,
            "date": datetime.datetime.now()
        })

        return jsonify({
            "prediction": label,
            "confidence": score
        })

    # Try newspaper3k first
    try:

        article = Article(url)
        article.download()
        article.parse()

        article_text = article.text

    except Exception:

        # Fallback scraping method
        try:
            import requests
            from bs4 import BeautifulSoup

            response = requests.get(url, timeout=5)

            soup = BeautifulSoup(response.text, "html.parser")

            paragraphs = soup.find_all("p")

            article_text = " ".join([p.get_text() for p in paragraphs])

        except Exception:

            return jsonify({
                "prediction": "ERROR",
                "confidence": 0,
                "message": "Unable to fetch article text"
            })

    # Run prediction
    label, score = predict_news(article_text, url)

    history_collection.insert_one({
        "email": session["user"],
        "news": url,
        "prediction": label,
        "confidence": score,
        "date": datetime.datetime.now()
    })

    return jsonify({
        "prediction": label,
        "confidence": score
    })


# ------------------------
# History
# ------------------------

@app.route("/history")
def history():

    if "user" not in session:
        return redirect("/login")

    user_history = history_collection.find({"email": session["user"]})

    return render_template("history.html", history=user_history)


# ------------------------
# Clear History
# ------------------------

@app.route("/clear_history", methods=["POST"])
def clear_history():

    if "user" not in session:
        return jsonify({"status": "error"})

    history_collection.delete_many({
        "email": session["user"]
    })

    return jsonify({"status": "success"})


# ------------------------
# Run Server
# ------------------------

if __name__ == "__main__":
    app.run(debug=True)