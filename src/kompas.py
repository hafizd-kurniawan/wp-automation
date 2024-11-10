from lxml import html
import time

from base.driver import SeleniumDriver
from utility.json_storage import ReadWriteJson
from src.chat_gpt import open_chatgpt, runAI
from utility.json_storage import StorageArticle
import json


class Kompas(SeleniumDriver):
    def __init__(self, driver):
        super().__init__(driver)
        self.driver = driver
        self.data_storage = StorageArticle()

    _list_category = {
        # "otomotif": "https://otomotif.kompas.com/?source=navbar",
        # "teknologi": "https://tekno.kompas.com/?source=navbar",
        # "gaya hidup": "https://lifestyle.kompas.com/?source=navbar",
        # "keuangan": "https://money.kompas.com/?source=navbar",
        # "masakan": "https://www.kompas.com/food?source=navbar",
        # "traveling": "https://travel.kompas.com/?source=navbar",
        "kesehatan": "https://health.kompas.com/?source=navbar",
    }
    _xp_top_ten_news = "//div[@class='most__wrap clearfix'] / div"
    _xp_top_ten_link = ".//a/@href"
    _xp_top_ten_title = ".//h4/text()"
    _lxml_content_article = "//div[@class='read__content']"
    _target_tag = ["h1", "h2", "h3", "h4", "h5", "h6", "p", "img"]

    def most_list_top_ten(self, category):
        list_el = self.getElementList(self._xp_top_ten_news, "xpath")
        for index, el in enumerate(list_el):
            # convert element ke lxml untuk hasil lebih dinammis
            el = self.convert_webElement_to_lxml(el)
            link = self.get_link(el)
            title = self.get_title(el)

            self.data_storage.add_article(category, index, title, link)

    def convert_webElement_to_lxml(self, webElement):
        return html.fromstring(webElement.get_attribute("innerHTML"))

    def get_link(self, element):
        link = element.xpath(self._xp_top_ten_link)[0]
        return link

    def get_title(self, element):
        title = element.xpath(self._xp_top_ten_title)[0]
        return title

    def get_article(self, url):
        self.driver.get(url)
        time.sleep(5)

        xp = html.fromstring(self.driver.page_source)
        res_div = xp.xpath(self._lxml_content_article)[0]
        # print(html.tostring(res_div, pretty_print=True, encoding='unicode'))

        # span digunakaan untuk ads
        # p perlu di cek dalam nya jika ada attr target
        # div attr target skip
        exclude_attrib = ["kompasidRec"]
        content = []
        h1 = xp.xpath("//h1")[0]
        text = h1.text
        content.append({"tag": h1.tag, "content": text})

        img = xp.xpath("//div[@class='photo__wrap'] / img")[0]
        src = img.xpath("./@src")[0]
        alt = img.xpath("./@alt")[0]
        content.append({"tag": img.tag, "src": src, "alt": alt})

        print("[*] Parsing: ", text)
        for element in res_div.iter():
            tmp = {}
            tag = element.tag
            attr = element.attrib
            text = element.xpath("string(.)")

            if tag not in self._target_tag:
                continue
            if "Baca juga:" in text:
                continue

            tmp["tag"] = tag
            if tag == "img":
                src = element.xpath("./@src")
                src = src[0] if len(src) != 0 else ""
            else:
                value = text.replace("KOMPAS.com", "PT. XYZ")
            if value == "":
                continue
            tmp["content"] = value
            content.append(tmp)

        # print(content)
        # print("\n\n")
        return content

    def save_data(self, file_path):
        data = self.data_storage.get_data()

        for category in data:
            print("[*] Category:", category)
            for article in data[category]["articles"]:
                link = article["link"]
                index = article["index"]
                content = self.get_article(link)
                self.data_storage.update_article(category, index, {"content": content})
        ReadWriteJson.write_to_json(data, file_path)

    def parsing_to_json(self, input_text, ori_text):
        try:
            text = input_text.replace("Copy code", "").replace("json", "").strip()
            json_data = json.loads(text)
            return json_data
        except:
            return ori_text

    def paraphrasing_content(self, data):
        open_chatgpt()
        for category in data:
            print("[*] Category:", category)

            # Iterasi melalui setiap artikel dalam kategori
            for index, article in enumerate(data[category]["articles"]):

                print("[*] Title:", article["title"])

                # Iterasi melalui setiap konten dalam artikel, melewati indeks 0 dan 1 (judul dan gambar)
                content = article["content"]
                res = runAI(content)

                # original_content = content["content"]
                # tag_content = content["tag"]
                # # skip jika tidak ada konten agar ai tidak menulis tulisan tidak terarah
                # if (
                #     original_content == ""
                #     or len(original_content) == 0
                #     or tag_content == "img"
                # ):
                #     continue
                # # Panggil AI untuk parafrase
                # paraphrased_content = runAI(original_content)
                # # Update konten setelah parafrase
                # article["content"][index_content]["content"] = paraphrased_content

                # Update artikel dalam data_storage setelah semua konten di-paraphrasing
                self.data_storage.update_article(
                    category, index, {"content": self.parsing_to_json(res, content)}
                )

        # berikan path aktif sekarang
        # belum bisa handel jika terjadi error saat parapasing
        ReadWriteJson.write_to_json(
            data, "/home/biru/Project/automaation-beritaa/kompas_scraping.json"
        )

    def scraping_kompas(self, file_path=None):
        path = "/home/biru/Project/automaation-beritaa/kompas_scraping.json"
        for category, link in self._list_category.items():
            self.driver.get(link)
            self.data_storage.add_category(category)
            self.most_list_top_ten(category)
        self.save_data(file_path)

        data = ReadWriteJson.load_json(
            "/home/biru/Project/automaation-beritaa/kompas_scraping.json"
        )
        self.paraphrasing_content(data)
