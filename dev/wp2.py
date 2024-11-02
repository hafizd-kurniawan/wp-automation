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


def login_wordpress():
    """Login ke dashboard WordPress."""
    driver = webdriver.Chrome()  # Ganti dengan driver yang sesuai jika perlu
    driver.get(WP_URL)

    # Isi username dan password
    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.ID, "user_login"))
    ).send_keys(USERNAME)

    driver.find_element(By.ID, "user_pass").send_keys(PASSWORD)

    # Klik tombol login
    driver.find_element(By.ID, "wp-submit").click()

    print("[*] Login berhasil")
    upload_page(driver)


def upload_page(driver):
    """Mengupload halaman baru di WordPress."""
    # Buka halaman untuk menambahkan page baru
    driver.get("http://portal-berita.local/wp-admin/edit.php?post_type=page")

    # Klik tombol "Add New Page"
    add_new_page = driver.find_element(
        By.CLASS_NAME, "page-title-action"
    ).get_attribute("href")
    driver.get(add_new_page)

    # Tutup popup jika ada
    try:
        close_btn = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable(
                (
                    By.CSS_SELECTOR,
                    ".components-modal__header .components-button.has-icon",
                )
            )
        )
        close_btn.click()
    except:
        print("Tidak ada popup untuk ditutup.")

    # Tunggu iframe muncul dan pindah ke iframe
    iframe_selector = "//iframe[@name='editor-canvas']"

    # Simpan konteks awal
    original_context = driver.current_window_handle

    # Pindah ke iframe
    driver.switch_to.frame(
        driver.find_element(By.XPATH, "//iframe[@name='editor-canvas']")
    )

    iframe_js = """
    const iframe = document.querySelector("iframe[name='editor-canvas']");
    return iframe ? true : false;
"""
    is_iframe_present = driver.execute_script(iframe_js)

    if is_iframe_present:
        driver.switch_to.frame(driver.find_element(By.NAME, "editor-canvas"))
        print("Berhasil pindah ke iframe.")
    else:
        print("Iframe belum tersedia.")

    # Cek apakah kita berada di dalam iframe
    current_context = driver.current_window_handle
    if current_context != original_context:
        print("Berhasil berpindah ke iframe.")
    else:
        print("Masih di konteks utama.")

    WebDriverWait(driver, 50).until(
        EC.presence_of_element_located((By.XPATH, iframe_selector))
    )
    driver.switch_to.frame(driver.find_element(By.XPATH, iframe_selector))

    # Masukkan konten baru ke dalam editor
    editor_selector = ".block-editor-rich-text__editable.block-editor-block-list__block.wp-block.is-selected.wp-block-paragraph.rich-text"
    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, editor_selector))
    )

    editor = driver.find_element(By.CSS_SELECTOR, editor_selector)
    editor.click()  # Fokus pada editor
    editor.send_keys("Halo, ini konten baru")

    # Trigger event 'input' agar WordPress mendeteksi perubahan
    editor.send_keys(Keys.ENTER)

    # Kembali ke konteks utama (keluar dari iframe)
    driver.switch_to.default_content()

    # Klik tombol "Publish"
    publish_btn = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, ".editor-post-publish-button"))
    )
    publish_btn.click()
    print("[*] Page berhasil dipublikasikan.")

    time.sleep(5)  # Jeda untuk memastikan publikasi selesai
    driver.quit()  # Menutup browser setelah selesai


# Jalankan automasi login dan upload halaman
login_wordpress()
