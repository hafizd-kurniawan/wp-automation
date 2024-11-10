import json
import sqlite3
from datetime import datetime
from typing import List


class StorageArticle:
    def __init__(self) -> None:
        self.data_scraping = {}
        self.db = StorageArticleDB()

    def add_category(self, category):
        if category not in self.data_scraping:
            self.data_scraping[category] = {"total": 0, "date": "", "articles": []}
            self.db.add_category(category)

    def add_article(self, category, index, title, link, content=[]):
        # Periksa apakah artikel dengan title dan link yang sama sudah ada
        if not any(
            article["title"] == title and article["link"] == link
            for article in self.data_scraping[category]["articles"]
        ):
            article = {
                "index": index,
                "title": title,
                "link": link,
                "published": False,
                "content": content,
            }
            self.data_scraping[category]["articles"].append(article)
            self.data_scraping[category]["total"] += 1
            self.db.add_article(category, title, link)
        else:
            print(
                f"Artikel '{title}' dengan link '{link}' sudah ada di kategori '{category}'."
            )

    def update_article(self, category, index, new_data):
        if category in self.data_scraping:
            article = self.data_scraping[category]["articles"][index]
            if article["index"] == index:
                article.update(new_data)
                print(
                    f"Artikel pada index {index} berhasil diperbarui dengan data {new_data}"
                )
                return
            else:
                print(f"Kategori '{category}' tidak ditemukan.")

    def get_data(self):
        return self.data_scraping


class ReadWriteJson:
    @classmethod
    def write_to_json(cls, data, file_path):
        with open(file_path, "w") as sp:
            json.dump(data, sp, indent=2)

    @classmethod
    def load_json(cls, file_path):
        with open(file_path, "r") as f:
            return json.load(f)


class StorageArticleDB:
    def __init__(self, db_name="articles.db"):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                date TEXT
            )
        """
        )
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS articles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category_id INTEGER,
                index INTEGER,
                title TEXT,
                link TEXT,
                content TEXT,
                published BOOLEAN DEFAULT 0,
                date TEXT,
                FOREIGN KEY (category_id) REFERENCES categories(id)
            )
        """
        )
        self.conn.commit()

    def add_category(self, category: str):
        self.cursor.execute(
            "INSERT OR IGNORE INTO categories (name) VALUES (?)", (category,)
        )
        self.conn.commit()

    def add_article(
        self, category: str, title: str, link: str, content: List[str] = []
    ):
        # Mendapatkan ID kategori
        self.cursor.execute("SELECT id FROM categories WHERE name = ?", (category,))
        category_data = self.cursor.fetchone()
        if category_data:
            category_id = category_data[0]
            # Cek apakah artikel sudah ada
            self.cursor.execute(
                "SELECT 1 FROM articles WHERE title = ? AND link = ? AND category_id = ?",
                (title, link, category_id),
            )
            if not self.cursor.fetchone():
                # Menambahkan artikel baru dengan tanggal saat ini
                content_str = "\n".join(content)
                date_today = datetime.now().strftime("%Y-%m-%d")
                self.cursor.execute(
                    """
                    INSERT INTO articles (category_id, index, title, link, content, date)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (category_id, title, link, content_str, date_today),
                )
                self.conn.commit()
            else:
                print(
                    f"Artikel '{title}' dengan link '{link}' sudah ada di kategori '{category}'."
                )

    def get_data_by_date(self, target_date: str):
        # Mengambil data artikel yang ditambahkan pada tanggal tertentu
        self.cursor.execute(
            """
            SELECT c.name, a.title, a.link, a.content, a.published
            FROM articles a
            JOIN categories c ON a.category_id = c.id
            WHERE a.date = ?
            """,
            (target_date,),
        )
        articles = self.cursor.fetchall()
        result = {}
        for category, title, link, content, published in articles:
            if category not in result:
                result[category] = []
            result[category].append(
                {
                    "title": title,
                    "link": link,
                    "content": content,
                    "published": bool(published),
                }
            )
        return result

    def close(self):
        self.conn.close()
