from selenium import webdriver
from pathlib import Path

from src.porta_berita import Login, Template, Post
from utility.json_storage import StorageArticle
from src.kompas import Kompas


def main():
    driver = webdriver.Chrome()
    username = ""
    password = ""
    datas = [
        "/home/biru/Documents/perumahan1.json",
        "/home/biru/Documents/perumahan2.json",
    ]
    # l = Login(driver)
    # l.login(username, password)

    # for data in datas:
    #     t = Template(driver)
    #     t.import_template(data)

    # for data in datas:
    #     p = Post(driver)
    #     p.add_post()

    driver = webdriver.Chrome()
    s = StorageArticle()
    k = Kompas(driver, s)
    k.scraping_kompas()
    driver = k.get_driver()
    data = s.get_data()

    for d in data:
        print("[*] Category:", d)
        for article in data[d]["articles"]:
            link = article["link"]
            index = article["index"]
            content = k.get_article(link)

            s.update_article(d, index, {"content": content})

    path = Path.cwd() / "file.json"
    k.write_to_json(data, path)


main()
