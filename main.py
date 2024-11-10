from selenium import webdriver
from pathlib import Path

from src.porta_berita import Login, Template, Post
from src.kompas_v2 import Kompas


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

    # article
    path = Path.cwd() / "kompas_scraping.json"
    k = Kompas(driver)
    k.start_request()


main()
