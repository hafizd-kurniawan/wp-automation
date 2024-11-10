from datetime import datetime
from pathlib import Path
from lxml import etree
from lxml import html
import string
import time
import json

from base.driver import SeleniumDriver
from utility.json_storage import ReadWriteJson
from src.chat_gpt import open_chatgpt, runAI
from utility.json_storage import StorageArticle
from src.format_template import ToTemplate


def write_to_json(file, data):
    with open(file, "w") as json_file:
        json.dump(data, json_file, ensure_ascii=False, separators=(",", ":"), indent=4)


def parsing_to_json(input_text, ori_text):
    try:
        text = input_text.replace("Copy code", "").replace("json", "").strip()
        json_data = json.loads(text)
        return json_data
    except:
        return ori_text


def clean_text(text):
    # Menghapus semua tanda baca dan whitespace tambahan
    text = text.translate(str.maketrans("", "", string.punctuation))
    text = "_".join(text.split())
    return text


def paraphrasing(text):
    runAI(text)


class Kompas(SeleniumDriver):
    def __init__(self, driver):
        super().__init__(driver)
        self.driver = driver
        open_chatgpt()
        self.extract_article_v1 = ExtractArticleV1(driver)

    _list_category_url = {
        "otomotif": "https://otomotif.kompas.com/?source=navbar",
        "teknologi": "https://tekno.kompas.com/?source=navbar",
        "gaya hidup": "https://lifestyle.kompas.com/?source=navbar",
        "keuangan": "https://money.kompas.com/?source=navbar",
        "masakan": "https://www.kompas.com/food?source=navbar",
        "traveling": "https://travel.kompas.com/?source=navbar",
        "kesehatan": "https://health.kompas.com/?source=navbar",
    }
    _xp_articles_v1 = "//div[@class='row article__wrap__grid--flex col-offset-fluid']//div[@class='article__grid']"
    _xp_articles = [
        # "//div[@class='articleHL-wrap']//div[@class='articleItem']",
        # "//*[@class='foodLatest__box']",
        # "//div[@class='trenLatest__item clearfix']",
    ]

    _xp_url = ".//h3/a/@href"
    _xp_image = ".//*[@class='article__asset']"
    _xp_detail_article = ".//*[@class='article__link']"

    def parse(self, category, url):
        """
        penyimpanan ke datbase baru bisa dilakukan ketika sudah di
        parahpasing, dan jika sudah di paraphasing maka file json nya
        akan di simpan di db
        """
        done = 0
        if category in ["otomotif", "teknologi", "traveling"]:
            web_elements = self.getElementList(self._xp_articles_v1, "xpath")
            list_article_detail = self.extract_url(web_elements)
            for url in list_article_detail:
                print(f"[*]Found articles {done}/{len(web_elements)}")
                self.extract_article_v1.extract(url)
                self.driver.get(url)
                done += 1

    def extract_url(self, elements):
        list_url = []
        for element in elements:
            element = self.convert_webElement_to_lxml(element)
            res = element.xpath(self._xp_url)[0]
            list_url.append(res)
        return list_url

    def convert_webElement_to_lxml(self, webElement):
        return html.fromstring(webElement.get_attribute("innerHTML"))

    def start_request(self):
        for category, url in self._list_category_url.items():
            self.driver.get(url)
            print(category)
            self.parse(category, url)


class ExtractArticleV1(SeleniumDriver):
    def __init__(self, driver):
        super().__init__(driver)
        self.driver = driver
        self.toTemplate = ToTemplate()

    _lxml_content_article = "//div[@class='read__content']"
    _xp_asset = ".//div[@class='article__asset']/a/@href"
    _xp_url = ".//h3/a/@href"
    _xp_title = "//h1"
    _xp_image_description = "//div[contains(text(),'Lihat Foto')]/parent::div/img"
    _target_tag = ["h1", "h2", "h3", "h4", "h5", "h6", "p", "img", "div", "li"]

    def extract(self, url):
        """
        url dari extract article adalah detail dari aticle,
        yg akan di scraping contentn nya
        """
        if "https://video.kompas.com" in url:
            return
        self.driver.get(url)
        title = self.extract_title()
        t = clean_text(title)
        res = self.extract_content(url)
        result_paraphrasing = paraphrasing(res)
        result_from_json = parsing_to_json(result_paraphrasing, res)
        path_json = f"{Path.cwd() / t}.json"
        write_to_json(file=path_json, data=result_from_json)
        self.toTemplate.filename = t
        self.toTemplate.start_create_template(path_json)

    def get_date(self):
        date_today = datetime.now().strftime("%Y-%m-%d")
        return date_today

    def extract_asset(self, element):
        return element.xpath(self._xp_asset)

    def extract_url(self, element):
        return element.xpath(self._xp_url)

    def extract_title(self):
        time.sleep(2)
        el = self.getElement(locator=self._xp_title, locatorType="xpath")
        return el.text

    def extract_content(self, url):
        print("[*] Fetching URL:", url)
        if "https://video.kompas.com" in url:
            return
        self.driver.get(url)
        time.sleep(5)  # Tunggu hingga halaman selesai dimuat

        page_tree = html.fromstring(self.driver.page_source)

        # Mendapatkan header utama artikel
        content = []
        content.extend(self.get_header_content(page_tree))

        # Mendapatkan div utama artikel
        main_div = page_tree.xpath(self._lxml_content_article)
        if not main_div:
            print("Div utama artikel tidak ditemukan.")
            return content

        main_div = main_div[0]

        # Mendapatkan konten artikel
        content.extend(self.get_article_content(main_div))
        return content

    def get_header_content(self, page_tree):
        content = []

        # Menyimpan h1
        h1_elements = page_tree.xpath("//h1")
        if h1_elements:
            content.append({"tag": "h1", "content": h1_elements[0].text_content()})

        # Menyimpan gambar utama jika ada
        img_elements = page_tree.xpath("//div[@class='photo__wrap']//img")
        if img_elements:
            img_src = img_elements[0].get("src", "")
            img_alt = img_elements[0].get("alt", "")
            content.append({"tag": "img", "src": img_src, "alt": img_alt})

        return content

    def get_article_content(self, main_div):
        content = []
        exclude_attrib = ["kompasidRec"]
        found_img_description = []

        for element in main_div.iter():
            tag = element.tag
            if tag not in self._target_tag:
                continue

            # Mengabaikan elemen yang memiliki atribut tertentu
            if any(attr in element.attrib for attr in exclude_attrib):
                continue

            text = element.text_content().strip()
            # Mengecek teks elemen
            if not text or "Baca juga:" in text:
                continue

            if tag == "img":
                img_src = element.get("src", "")
                if img_src:
                    content.append(
                        {"tag": "img", "src": img_src, "alt": element.get("alt", "")}
                    )

            # Jika elemen adalah teks
            if tag == "p":
                # Membersihkan teks
                cleaned_text = text.replace("KOMPAS.com", "PT. XYZ")
                if cleaned_text:
                    content.append({"tag": tag, "content": cleaned_text})

            if tag == "div":
                el = element.xpath("./*[@class='photo__wrap']")
                if len(el) != 0:
                    img_element = el[0].xpath(self._xp_image_description)
                    if img_element is not None:
                        img_element = img_element[0]
                        img_src = img_element.get("src", "")
                        if img_src in found_img_description:
                            continue
                        content.append(
                            {
                                "tag": "img",
                                "src": img_src,
                                "alt": img_element.get("alt", ""),
                            }
                        )
            if tag in ["h2", "h3", "h4", "h5", "h6"]:
                content.append({"tag": tag, "content": text})

            if tag == "li":
                content.append({"tag": tag, "content": text})

        return content
