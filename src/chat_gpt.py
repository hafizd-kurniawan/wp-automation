from queue import Queue
from botasaurus.browser import Driver, Wait, browser
from botasaurus.user_agent import UserAgent
from botasaurus.window_size import WindowSize
import time

HIT_BUTTON_SEND_PROMPT = 0  # Counter global untuk tracking prompt
DRIVER = None


def inject_text_with_js(driver: Driver, text: str):
    """Injeksi teks langsung ke elemen prompt dengan JavaScript."""
    js_code = f"""
    document.querySelector("div[id='prompt-textarea']").innerText = `{text}`;
    """
    driver.run_js(js_code)


def send_prompt(driver: Driver, prompt: str):
    """Mengirim prompt dengan injeksi JavaScript."""
    global HIT_BUTTON_SEND_PROMPT

    default_prompt = """kamu adalah seorang ahli seo dan copywriting, saat ini kamu sedang melakukan paraphrasing dari  beberapa webiste berita lokal dan manca negara untuk situs berita mu sendiri. dibawah ini adalah hasil scraping dari webiste berita orang lain dengan format .json paraphrasing bagian content dengan bahasa yang baik menurut SEO, jadikan output nya dengan bentuk .json tanpa ada noise teks tambahan, penjelasan dan sejenis nya"""

    full_prompt = f"{default_prompt} {prompt}"

    driver.wait_for_element("div[id='prompt-textarea']", wait=60)

    # Inject teks langsung ke input prompt
    inject_text_with_js(driver, full_prompt)

    # Klik tombol kirim
    driver.click("button[aria-label='Send prompt']", Wait.LONG)

    HIT_BUTTON_SEND_PROMPT += 1
    time.sleep(2)


def get_response(driver: Driver, prompt: str) -> str:
    """Mengambil respons terakhir dari ChatGPT dengan timeout."""
    send_prompt(driver, prompt)

    start_time = time.time()
    timeout = 10  # Timeout dalam detik

    while time.time() - start_time < timeout:
        # Cek apakah tombol 'Copy' sudah muncul, berarti respons siap
        buttons = driver.select_all("button[aria-label='Copy']", Wait.VERY_LONG)
        responses = driver.select_all(".markdown", Wait.VERY_LONG)
        response_text = responses[-1].text  # Ambil respons terakhir
        return response_text  # Kembalikan respons
        time.sleep(1)  # Tambahkan jeda agar tidak terlalu cepat
    print("[Error]: Respons ChatGPT timeout.")
    time.sleep(3500)
    return ""


@browser(
    reuse_driver=True,
    close_on_crash=True,
    user_agent=UserAgent.HASHED,
    window_size=WindowSize.HASHED,
    output=None,
)
def open_chatgpt(driver: Driver, data={}):
    """Membuka halaman ChatGPT dan menambahkan driver ke antrian (queue)."""
    driver.google_get("https://chatgpt.com/", bypass_cloudflare=True)
    global DRIVER
    DRIVER = driver


def check_popup(driver: Driver):
    """Cek dan klik popup jika muncul."""
    try:
        result = driver.wait_for_element(
            "a[class='mt-5 cursor-pointer text-sm font-semibold text-token-text-secondary underline']",
            wait=Wait.SHORT,
        )
        if result:
            result.click()
    except:
        pass


def runAI(prompts):
    """Jalankan penerjemahan untuk setiap prompt secara berurutan."""
    try:
        check_popup(DRIVER)
        response = get_response(DRIVER, prompts)
        # print(f"[++] Response: {response}\n\n")
        return response
    except Exception as e:
        print(f"[Error]: {e}")
    return {}
