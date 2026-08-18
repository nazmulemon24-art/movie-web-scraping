import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

all_movies = []

headers = {
    "User-Agent": "Mozilla/5.0"
}

# 2000+ data পাওয়ার জন্য 2000 থেকে 2024
for year in range(2000, 2025):

    url = f"https://www.filmfansite.org.uk/date/{year}.htm"

    print("Scraping:", year)

    try:
        response = requests.get(
            url,
            headers=headers,
            timeout=20
        )

        if response.status_code != 200:
            print("Page failed:", response.status_code)
            continue

        soup = BeautifulSoup(response.text, "html.parser")

        # Year page-এর main heading
        heading = soup.find("h1")

        if heading is None:
            print("Heading not found")
            continue

        # Heading-এর পরের অংশ থেকে movie খুঁজবো
        for element in heading.find_all_next("a"):

            title = element.get_text(" ", strip=True)

            # Empty link বাদ
            if not title:
                continue

            # Menu / navigation / Oscar related link বাদ
            if title.lower() in [
                "menu",
                "home",
                "actor",
                "actress",
                "films",
                "dates",
                "people",
                "image"
            ]:
                continue

            # Image link বাদ
            if element.find("img"):
                continue

            # Movie link-এর পাশে rating image খোঁজা
            rating = ""

            parent = element.parent

            if parent:
                image = parent.find("img")

                if image:
                    rating = image.get("alt", "")

            # শুধুমাত্র reasonable movie title
            if len(title) > 1:

                all_movies.append({
                    "Movie_Title": title,
                    "Release_Year": year,
                    "Rating": rating,
                    "Movie_URL": element.get("href", "")
                })

        # Server-কে বেশি request না দেওয়ার জন্য delay
        time.sleep(2)

    except Exception as e:

        print("Error:", e)


# DataFrame
df = pd.DataFrame(all_movies)

# Duplicate remove
df = df.drop_duplicates(
    subset=["Movie_Title", "Release_Year"]
)

# Empty title remove
df = df[
    df["Movie_Title"].notna()
]

# 2000 rows
df = df.head(2000)

# CSV
df.to_csv(
    "movies_dataset.csv",
    index=False,
    encoding="utf-8-sig"
)

print("\n==============================")
print("SCRAPING COMPLETED")
print("==============================")

print("Total rows:", len(df))

print("\nColumns:")
print(df.columns.tolist())

print("\nFirst 10 rows:")
print(df.head(10))

print("\nCSV file created:")
print("movies_dataset.csv")