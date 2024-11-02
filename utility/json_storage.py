class StorageArticle:
    def __init__(self) -> None:
        self.data_scraping = {}

    def add_category(self, category):
        if category not in self.data_scraping:
            self.data_scraping[category] = {"total": 0, "date": "", "articles": []}

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
        else:
            print(
                f"Artikel '{title}' dengan link '{link}' sudah ada di kategori '{category}'."
            )

    def update_article(self, category, index, new_data):
        if category in self.data_scraping:
            article = self.data_scraping[category]["articles"][index]
            if article["index"] == index:
                article.update(new_data)
                print(f"Artikel pada index {index} berhasil diperbarui dengan data")
                return
            else:
                print(f"Kategori '{category}' tidak ditemukan.")

    def get_data(self):
        return self.data_scraping
