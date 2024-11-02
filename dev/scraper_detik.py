from botasaurus.browser import browser, Driver
from botasaurus.browser import Wait
from botasaurus.request import request, Request
from botasaurus.soupify import soupify
from lxml import html, etree

from chat_gpt import open_chatgpt, runAI
from wp2 import login_wordpress

list_article_class = ".list-content__item"
span_image_article_class = ".ratiobox"
span_media_image = ".media__image"
span_media_text = ".media__text"
span_media_title = ".media__title"
link_article = f"{span_media_text} {span_media_title} a"
title_article = f"{span_media_text} {span_media_title}"
tb_image_article = f"{span_media_image} a"
# detail content
base_url = "https://www.detik.com"
detik_detail_content = "detikdetailtext"
class_detail_properti = "detail"

class_swiper = ".swiper"
list_ignore_class = [
    "clearfix",
    "parallaxindetail",
    "scrollpage",
    "ads-scrollpage-container",
    "para_caption",
    "linksisip",
    "staticdetail_container",
    "staticdetail_ads",
    "parallaxindetail",
    "scrollpage",
    "para_caption",
    "ads-scrollpage-container",
    "ads-scrollpage-height",
    "ads-scrollpage-box",
    "ads-scrollpage-top",
    "ads-scrollpage-banner",
]
list_target_tag = ["h1", "p"]
list_data = []
list_content = []


def string_to_lxml_parse(text):
    try:
        return html.fromstring(str(text))
    except etree.ParseError as e:
        return False


def get_content(element):
    # Gabungkan semua teks dari elemen dan anak-anaknya
    try:
        text_content = " ".join(element.itertext()).strip()
        return text_content
    except Exception as e:
        print(f"[*] Error saat mengambil teks: {e}")
        return ""


def set_query_xpath(tag_lxml, tag):
    tag_html = tag.name
    node = f"//{tag_html}"
    query = " and ".join(
        f"not(contains(@class, '{attr}'))" for attr in list_ignore_class
    )
    query = f"{node}[{query}]"
    result_filtered = tag_lxml.xpath(query)
    if len(result_filtered) == 0:
        return

    # print(result_filtered)
    content = get_content(result_filtered[0]).strip()
    c = {"tag": tag_html, "content": content}
    list_content.append(c)


def has_excluded_parent(tag, excluded_classes):
    parent = tag.parent
    while parent:  # Iterasi ke atas sampai root
        if "class" in parent.attrs and set(parent["class"]) in excluded_classes:
            return True  # Jika ada parent dengan class yang dikecualikan
        parent = parent.parent
    return False


@browser(
    output=None,
    wait_for_complete_page_load=False,
    # close_on_crash=True,
    # block_images=True,
)
def scraper_article(driver: Driver, data):
    for dict_data in list_data:
        link = dict_data["link"]
        driver.google_get(link, bypass_cloudflare=False, wait=Wait.SHORT)
        exits_ads = driver.is_element_present(class_swiper, wait=Wait.SHORT)
        if exits_ads:
            print("[*] Skip video ads")
            continue
        soup = soupify(driver.page_html)
        if f"{base_url}/properti" in link:
            element_detail = soup.find("article", class_=class_detail_properti)
        if f"{base_url}/media" in link:
            element_detail = soup.find(id=detik_detail_content)

        if not element_detail:
            print("[*] Detail content tidak ditemukan")
            continue

        for tag in list_target_tag:
            for cur in element_detail.find_all(tag):
                lxml = string_to_lxml_parse(cur)
                set_query_xpath(lxml, cur)
        # for tag in element_detail.find_all(list_target_tag):

        open_chatgpt()
        runAI(list_content)
        list_content.clear()


@browser(
    output=None,
    close_on_crash=True,
    wait_for_complete_page_load=False,
    # block_images=True,
)
def open_detik(driver: Driver, data):
    driver.google_get(
        "https://www.detik.com/properti", bypass_cloudflare=False, wait=Wait.SHORT
    )
    is_element_exists = driver.wait_for_element(list_article_class, wait=Wait.SHORT)
    if is_element_exists:
        for el_article in driver.select_all(list_article_class, wait=Wait.LONG):
            result = {"driver": driver, "image": "", "title": "", "link": ""}
            res_tb_image = el_article.select(tb_image_article, wait=Wait.SHORT)
            res_title_article = el_article.select(title_article, wait=Wait.SHORT)
            res_link_article = el_article.select(link_article, wait=Wait.SHORT)
            result["title"] = res_title_article.text
            result["image"] = res_tb_image.get_attribute("style")
            result["link"] = res_link_article.get_attribute("href")
            print(f"[*] Scraping page {result['link']}")
            print(f"[*] Scraping page {result['title']}")
            list_data.append(result)
            break
    else:
        print("error saat memuat index")


open_detik()
scraper_article()
try:
    login_wordpress()
except:
    pass
