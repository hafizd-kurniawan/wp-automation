from botasaurus.browser import Driver, Wait, browser
from botasaurus.user_agent import UserAgent
from botasaurus.window_size import WindowSize
import time
import subprocess

# Informasi login dan akses WordPress
WP_URL = "http://portal-berita.local/wp-login.php?loggedout=true&wp_lang=en_US"
USERNAME = "admin"
PASSWORD = "admin"
NEW_POST_URL = "https://your-wordpress-site.com/wp-admin/post-new.php"


@browser(
    reuse_driver=True,
    close_on_crash=True,
    user_agent=UserAgent.HASHED,
    window_size=WindowSize.HASHED,
    output=None,
)
def login_wordpress(driver: Driver, data):
    """Login ke dashboard WordPress."""
    driver.google_get(WP_URL, accept_google_cookies=True, wait=Wait.SHORT)

    # Isi username dan password
    driver.type("input[id='user_login']", USERNAME, Wait.SHORT)
    driver.type("input[id='user_pass']", PASSWORD, Wait.SHORT)

    # Klik tombol login
    driver.click("input[id='wp-submit']", Wait.SHORT)
    time.sleep(2)

    print("[*] Login berhasil")
    # driver.google_get(NEW_POST_URL, wait=Wait.LONG)
    # style_content(driver)
    upload_page(driver)


def wait_for_iframe(driver: Driver, iframe_selector: str, timeout=10):
    """Menunggu iframe tersedia dan siap digunakan."""
    start_time = time.time()
    while time.time() - start_time < timeout:
        iframes = driver.select_all(iframe_selector, wait=Wait.SHORT)
        if iframes:
            return iframes[0]  # Kembalikan iframe pertama yang ditemukan
        time.sleep(1)
    raise Exception(f"Iframe '{iframe_selector}' tidak ditemukan dalam batas waktu.")


def upload_page(driver: Driver):
    # Buka halaman untuk menambahkan page baru
    driver.google_get(
        "http://portal-berita.local/wp-admin/edit.php?post_type=page",
        bypass_cloudflare=False,
        wait=Wait.SHORT,
    )

    # Klik tombol "Add New Page"
    add_new_page = driver.select(".page-title-action", wait=Wait.SHORT).get_attribute(
        "href"
    )
    driver.google_get(add_new_page, bypass_cloudflare=False, wait=Wait.SHORT)

    # Tutup popup jika ada
    close_popup_script = """
        const closeBtn = document.querySelector('.components-modal__header .components-button.has-icon');
        if (closeBtn) closeBtn.click();
    """
    time.sleep(5)
    driver.run_js(close_popup_script)
    # driver.reload()
    time.sleep(2)

    # Masukkan konten baru ke dalam editor
    insert_content_script = """
        const editor = document.querySelector('.block-editor-rich-text__editable.block-editor-block-list__block.wp-block.is-selected.wp-block-paragraph.rich-text');
        console.log(editor)
        editor.focus();
        editor.innerHTML = "<p>Halo, ini konten baru</p>";

        // Trigger event 'input' agar WordPress mendeteksi perubahan
        const event = new Event('input', { bubbles: true });
        editor.dispatchEvent(event);
    """
    result = driver.run_js(insert_content_script)
    print(result)
    r = driver.select(
        selector=".block-editor-rich-text__editable.block-editor-block-list__block.wp-block.is-selected.wp-block-paragraph.rich-text",
        wait=Wait.SHORT,
    )
    time.sleep(5)
    print(r)

    # Kembali ke konteks utama
    # driver.switch_to_default_content()

    # Klik tombol "Publish"
    publish_script = """
        const publishBtn = document.querySelector('.editor-post-publish-button');
        if (publishBtn) {
            publishBtn.click();
            return "Page berhasil dipublikasikan.";
        } else {
            return "Tombol Publish tidak ditemukan.";
        }
    """
    result = driver.run_js(publish_script)
    print(result)

    time.sleep(5)  # Jeda agar publikasi selesai

    # Kembali ke konteks utama jika menggunakan iframe
    driver.switch_to_default_content()

    # Klik tombol "Publish"
    publish_script = """
        const publishBtn = document.querySelector('.editor-post-publish-button');
        if (publishBtn) {
            publishBtn.click();
            return "Page berhasil dipublikasikan.";
        } else {
            return "Tombol Publish tidak ditemukan.";
        }
    """
    result = driver.run_js(publish_script)
    print(result)

    time.sleep(5)  # Jeda untuk memastikan publikasi selesai


def style_content(driver: Driver):
    """Mengatur konten dengan drag-and-drop dan styling block."""
    time.sleep(2)  # Beri jeda agar halaman sepenuhnya dimuat

    # Simulasi menambah block baru dengan klik
    driver.click("button[aria-label='Add block']", Wait.SHORT)

    # Pilih block 'Paragraph' menggunakan JavaScript injection
    js_code = """
    const blocks = document.querySelectorAll('button.editor-block-list-item-paragraph');
    if (blocks.length > 0) {
        blocks[0].click();
    }
    """
    driver.execute_script(js_code)
    time.sleep(1)

    # Isi teks paragraf
    paragraph_js = """
    const paragraph = document.querySelector('.block-editor-rich-text__editable');
    if (paragraph) {
        paragraph.innerHTML = '<p>Ini adalah paragraf baru dengan drag-and-drop otomatis!</p>';
    }
    """
    driver.execute_script(paragraph_js)

    print("[*] Paragraf berhasil ditambahkan")

    # Simulasi styling block menggunakan JavaScript
    style_js = """
    const toolbarButton = document.querySelector('button[aria-label="Change alignment"]');
    if (toolbarButton) {
        toolbarButton.click();
        document.querySelector('button[aria-label="Align center"]').click();
    }
    """
    driver.execute_script(style_js)
    print("[*] Paragraf diatur menjadi align-center")

    # Publikasikan postingan
    publish_post(driver)


def publish_post(driver: Driver):
    """Publikasikan postingan."""
    driver.click("button.editor-post-publish-panel__toggle", Wait.SHORT)
    time.sleep(1)
    driver.click("button.editor-post-publish-button", Wait.SHORT)

    print("[*] Konten berhasil dipublikasikan")


# Jalankan automasi login dan styling konten
login_wordpress()
