import pandas as pd

fake = pd.read_csv("dataset/Fake.csv")
true = pd.read_csv("dataset/True.csv")

fake["label"] = 0
true["label"] = 1

data = pd.concat([fake,true])

data = data[["text","label"]]

data.to_csv("dataset/news.csv",index=False)

print("Dataset created successfully")