import requests
from bs4 import BeautifulSoup
import time
import random
import json
import csv

GOODREADS_LIST_URL = "https://www.goodreads.com/list/show/1.Best_Books_Ever?page={}"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

# ---------------------------------------------------------
#   OBTENER DETALLES DESDE GOOGLE BOOKS API
# ---------------------------------------------------------
def get_google_books_data(title, author):
    query = f"https://www.googleapis.com/books/v1/volumes?q=intitle:{title}+inauthor:{author}"

    try:
        r = requests.get(query)
        data = r.json()

        if "items" not in data:
            return "", [], ""

        book = data["items"][0]["volumeInfo"]

        description = book.get("description", "")
        genres = book.get("categories", [])
        thumbnail = book.get("imageLinks", {}).get("thumbnail", "")

        return description, genres, thumbnail

    except Exception as e:
        print("Error Google Books:", e)
        return "", [], ""

# ---------------------------------------------------------
#   SCRAPEAR LISTA DE GOODREADS
# ---------------------------------------------------------
def scrape_goodreads_list(target=300):
    books = []
    page = 1

    while len(books) < target:
        print(f"\n📄 Scrapeando página {page}...")

        r = requests.get(GOODREADS_LIST_URL.format(page), headers=HEADERS)
        soup = BeautifulSoup(r.text, "html.parser")

        rows = soup.select("table.tableList tr")

        if not rows:
            print("⚠️ No se encontraron libros en esta página.")
            break

        for row in rows:
            if len(books) >= target:
                break

            title_tag = row.select_one("a.bookTitle")
            author_tag = row.select_one("a.authorName")
            rating_tag = row.select_one("span.minirating")

            if not title_tag or not author_tag:
                continue

            title = title_tag.get_text(strip=True)
            author = author_tag.get_text(strip=True)
            rating = rating_tag.get_text(strip=True).split("—")[0].strip()

            print(f"   → {len(books)+1}. {title} - {author}")

            # Obtener detalles desde Google Books
            description, genres, thumbnail = get_google_books_data(title, author)

            books.append({
                "title": title,
                "author": author,
                "rating": rating,
                "genres": genres,
                "description": description,
                "thumbnail": thumbnail
            })

            time.sleep(random.uniform(0.3, 0.7))

        page += 1
        time.sleep(random.uniform(1, 2))

    return books

# ---------------------------------------------------------
#   PROGRAMA PRINCIPAL
# ---------------------------------------------------------
if __name__ == "__main__":
    data = scrape_goodreads_list(300)

    print("\n📚 Scraping completado. Libros recopilados:", len(data))

    # Guardar en CSV
    with open("books_google.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["title", "author", "rating", "genres", "description", "thumbnail"])
        writer.writeheader()
        for book in data:
            writer.writerow(book)

    # Guardar en JSON
    with open("books_google.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    print("💾 Archivos guardados: books_google.csv y books_google.json")
