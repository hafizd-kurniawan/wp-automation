from selenium import webdriver
from lxml import html
import time
import json

from base.driver import SeleniumDriver


class Kompas(SeleniumDriver):
    def __init__(self, driver, data_storage):
        super().__init__(driver)
        self.driver = driver
        self.data_storage = data_storage

    _list_category = {
        "kesehatan": "https://health.kompas.com/?source=navbar",
        # "otomotif":"https://otomotif.kompas.com/?source=navbar",
        # "teknologi":"https://tekno.kompas.com/?source=navbar",
        # "gaya hidup":"https://lifestyle.kompas.com/?source=navbar",
        # "keuangan":"https://money.kompas.com/?source=navbar",
        # "masakan":"https://www.kompas.com/food?source=navbar",
        # "traveling":"https://travel.kompas.com/?source=navbar"
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

    def get_driver(self):
        return self.driver

    def get_article(self, url):
        self.driver.get(url)
        time.sleep(10)

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
        content.append({h1.tag: text})

        img = xp.xpath("//div[@class='photo__wrap'] / img")[0]
        src = img.xpath("./@src")[0]
        alt = img.xpath("./@alt")[0]
        content.append({"img": img.tag, "src": src, "alt": alt})

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

            tmp[tag] = text.replace("KOMPAS.com", "PT. XYZ")
            content.append(tmp)

        # print(content)
        # print("\n\n")
        return content

    def write_to_json(self, data, file_path):
        # Membuka file dalam mode tulis dan menulis data JSON ke file
        with open(file_path, "w") as sp:
            json.dump(data, sp, indent=4)

    def scraping_kompas(self):
        for category, link in self._list_category.items():
            self.driver.get(link)
            self.data_storage.add_category(category)
            self.most_list_top_ten(category)
