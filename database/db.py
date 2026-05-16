from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")

db = client["fake_news_db"]

users_collection = db["users"]
history_collection = db["history"]