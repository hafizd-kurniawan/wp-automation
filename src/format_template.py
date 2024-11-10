import json


template = None
with open("base/template_base.json", "r") as f:
    template = json.load(f)


class ReadWriteJson:
    @classmethod
    def write_to_json(cls, data, file_path):
        with open(file_path, "w") as sp:
            json.dump(data, sp, indent=2)

    @classmethod
    def load_json(cls, file_path):
        with open(file_path, "r") as f:
            return json.load(f)


class ToTemplate:
    def __init__(self) -> None:
        self.base_template = template
        self.filename = None

    def create_title_template(self, title):
        self.base_template["title"] = title

    def create_heading_h1(self, content):
        return {
            "id": "3fd75882",
            "settings": {
                "title": content,
                "_element_width": "initial",
                "_element_custom_width": {"unit": "%", "size": 97.763},
                "header_size": "h1",
                "typography_typography": "custom",
                "typography_font_size": {"unit": "px", "size": 40, "sizes": []},
            },
            "elements": [],
            "isInner": False,
            "widgetType": "heading",
            "elType": "widget",
        }

    def creaate_heading(self, content):
        return {
            "id": "3d96e25d",
            "settings": {"title": content},
            "elements": [],
            "isInner": False,
            "widgetType": "heading",
            "elType": "widget",
        }

    def create_image(self, src, alt):
        return {
            "id": "49e1d852",
            "settings": {
                "image": {"url": src, "id": "", "size": "", "source": "url"},
                "caption_source": "custom",
                "caption": alt,
                "link_to": "custom",
                "link": {
                    "url": src,
                    "is_external": "",
                    "nofollow": "",
                    "custom_attributes": "",
                },
            },
            "elements": [],
            "isInner": False,
            "widgetType": "image",
            "elType": "widget",
        }

    def create_paragraf(self, content):
        return {
            "id": "24e63671",
            "settings": {"editor": f"<p>{content}</p>"},
            "elements": [],
            "isInner": False,
            "widgetType": "text-editor",
            "elType": "widget",
        }

    def start_create_template(self, filejson):
        store_templates = []
        datas = ReadWriteJson.load_json(filejson)
        for data in datas:
            tag = data["tag"]
            content = data.get("content", "")
            src = data.get("src", "")
            alt = data.get("alt", "")

            self.create_title_template(content)
            if tag == "h1":
                res = self.create_heading_h1(content)
                store_templates.append(res)
            if tag == "img" and src != None:
                res = self.create_image(src, alt)
                store_templates.append(res)
            if tag in ["h2", "h3", "h4", "h5", "h6"]:
                res = self.creaate_heading(content)
                store_templates.append(res)
            if tag == "p":
                res = self.create_paragraf(content)
                store_templates.append(res)

        self.base_template["content"][1]["elements"][0]["elements"].clear()
        self.base_template["content"][1]["elements"][0]["elements"].extend(
            store_templates
        )

        templateFile = f"template-{self.filename}.json"
        with open(templateFile, "w") as f:
            json.dump(self.base_template, f, ensure_ascii=False, separators=(",", ":"))
        print(f"[*] Create Template Success: {templateFile}")
