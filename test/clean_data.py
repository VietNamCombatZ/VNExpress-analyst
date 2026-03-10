import pandas as pd
import re

df = pd.read_csv("vnexpress_raw_data.csv")

print("Số dòng ban đầu:", len(df))

# 1 remove duplicates
df = df.drop_duplicates(subset="url")

# 2 remove missing content
df = df.dropna(subset=["content", "title"])

# 3 clean text
def clean_text(text):
    text = str(text)
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    return text

df['content'] = df['content'].apply(clean_text)
df['title'] = df['title'].apply(clean_text)

# 4 tạo feature mới

df['title_length'] = df['title'].apply(lambda x: len(x.split()))
df['content_length'] = df['content'].apply(lambda x: len(x.split()))

# convert date
df['date'] = pd.to_datetime(df['date'], errors='coerce')

df['year'] = df['date'].dt.year
df['month'] = df['date'].dt.month
df['hour'] = df['date'].dt.hour

print("Sau khi clean:", len(df))

df.to_csv("vnexpress_clean_data.csv", index=False)

print("Saved clean data")