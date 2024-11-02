import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Informasi login dan akses WordPress
WP_URL = "http://portal-berita.local/wp-login.php?loggedout=true&wp_lang=en_US"
USERNAME = "admin"
PASSWORD = "admin"
FILE_PATH = "/home/biru/Project/automaation-beritaa/template.json"


class WPLogin:
    @staticmethod
    def login(driver):
        driver.get(WP_URL)

        # Isi username dan password
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "user_login"))
        ).send_keys(USERNAME)

        driver.find_element(By.ID, "user_pass").send_keys(PASSWORD)

        # Klik tombol login
        driver.find_element(By.ID, "wp-submit").click()
        time.sleep(2)
        print("[*] Login berhasil")


class WPTemplates:
    def __init__(self, driver):
        self.driver = driver

    def navigate_to_templates(self):
        url = "http://portal-berita.local/wp-admin/edit.php?post_type=elementor_library&tabs_group=library"
        self.driver.get(url)

    def btn_import_template(self):
        try:
            element = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, "elementor-import-template-trigger"))
            )
            element.click()
        except Exception as e:
            print(f"[x] btn_import_template error: {e}")

    def insert_file_manager(self):
        try:
            # Menggunakan 'send_keys' untuk mengisi input file.
            file_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//input[@type='file']"))
            )
            file_input.send_keys(FILE_PATH)
        except Exception as e:
            print(f"[x] insert_file_manager error: {e}")

    def btn_import_now(self):
        try:
            element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "input[id='e-import-template-action']")
                )
            )
            element.click()
            print("[*] Template berhasil diimpor")
        except Exception as e:
            print(f"[x] btn_import_now error: {e}")

    def btn_confirm(self):
        try:
            element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (
                        By.XPATH,
                        '//button[@class="dialog-button dialog-ok dialog-confirm-ok"]',
                    )
                )
            )
            element.click()
            print("[*] sukses")
        except Exception as e:
            print(f"[x] btn_import_now error: {e}")


if __name__ == "__main__":
    # Inisialisasi WebDriver (Pastikan driver browser ada di PATH)
    driver = webdriver.Chrome()

    # Login ke WordPress
    WPLogin.login(driver)

    # Akses dan impor template di WordPress
    wp_template = WPTemplates(driver)
    wp_template.navigate_to_templates()
    wp_template.btn_import_template()
    wp_template.insert_file_manager()
    wp_template.btn_import_now()
    wp_template.btn_confirm()
    time.sleep(3600)

    # Tutup browser setelah selesai
    driver.quit()
