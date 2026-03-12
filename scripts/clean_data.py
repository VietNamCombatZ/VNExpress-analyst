import pandas as pd
import re

df = pd.read_csv("vnexpress_raw_data.csv")

print("Initial rows:", len(df))

# remove duplicates
df = df.drop_duplicates(subset="url")

# remove missing
df = df.dropna(subset=["content", "title"])

# fill missing
df['author'] = df['author'].fillna("Unknown")
df['tags'] = df['tags'].fillna("")
df['nums_of_comments'] = df['nums_of_comments'].fillna(0)

# clean text
def clean_text(text):
    text = str(text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

df['content'] = df['content'].apply(clean_text)
df['title'] = df['title'].apply(clean_text)

# clean date
def clean_date(text):
    if pd.isna(text):
        return text
    text = re.sub(r'^Thứ.*?,\s*', '', text)
    text = re.sub(r'\(.*?\)', '', text)
    return text.strip()

df['date'] = df['date'].apply(clean_date)
df['date'] = pd.to_datetime(df['date'], format='%d/%m/%Y, %H:%M', errors='coerce')

# remove invalid date
df = df.dropna(subset=['date'])

# feature engineering
df['year'] = df['date'].dt.year
df['month'] = df['date'].dt.month
df['hour'] = df['date'].dt.hour

df['title_length'] = df['title'].apply(lambda x: len(x.split()))
df['content_length'] = df['content'].apply(lambda x: len(x.split()))

# remove outliers
df = df[df['content_length'] > 50]

df = df.reset_index(drop=True)

print("After cleaning:", len(df))

df.to_csv("vnexpress_clean_data.csv", index=False)

print(df.info())
print(df.describe())

print("Saved clean data")