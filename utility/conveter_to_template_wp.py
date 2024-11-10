import json

from utility.builder_template_wp import *


class Conveter:
    def __init__(self) -> None:
        self.template_article = None
        self.data_scraping = None

    def load_json(self, filename):
        with open(filename, "r") as f:
            return json.load(f)

    def update_template(self, template, list_element):
        # list of elements
        t = template["content"][0]["elements"][0]["elements"]
        t.extend(list_element)

    def convert_to_template(self, data):
        for category in data:
            for article in data[category]["articles"]:
                for content in article["content"]:
                    for tag in content.key():
                        if tag == "img":
                            for k, v in content[tag]:
                                image["image"]["url"] = "src"
                                image["image"]["alt"] = "alt"
                            pass
                        if tag == "p":
                            pass
                        if tag == "h1":
                            pass
                        if tag in ["h2", "h3", "h4", "h5", "h6"]:
                            pass

    def convert(self, scraping, template_wp):
        data_scraping = self.load_json(scraping)
        data_template = self.load_json(template_wp)
