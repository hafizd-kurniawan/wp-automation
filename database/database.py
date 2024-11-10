import sqlite3


# error installasi
# sudo apt-get install libsqlite3-dev
class Database:
    def __init__(self, db_name="articles.db") -> None:
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        self.cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS articles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category TEXT NOT NULL,
        title TEXT NOT NULL,
        link TEXT UNIQUE NOT NULL,
        content_path TEXT,
        date_added DATE DEFAULT CURRENT_DATE,
        publish_date DATE,
        is_published BOOLEAN DEFAULT 0,
        source TEXT,
        tags TEXT,
        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        )

    def parse_to_db(self):
        pass

    def add_article(self):
        pass

    def is_article_exist(self):
        pass
