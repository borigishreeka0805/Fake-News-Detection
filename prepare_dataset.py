import pandas as pd

# Load dataset
data = pd.read_csv("dataset/WELFake_Dataset.csv")

# Combine title + text
data["text"] = data["title"] + " " + data["text"]

# Keep only needed columns
data = data[["text","label"]]

# Remove empty rows
data = data.dropna()

# Save cleaned dataset
data.to_csv("dataset/news.csv", index=False)

print("Dataset ready:", len(data))