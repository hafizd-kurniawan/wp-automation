from queue import Queue
from botasaurus.browser import Driver, Wait, browser
from botasaurus.user_agent import UserAgent
from botasaurus.window_size import WindowSize
import time

q = Queue()  # Queue untuk menyimpan driver
HIT_BUTTON_SEND_PROMPT = 0  # Counter global untuk tracking prompt


def inject_text_with_js(driver: Driver, text: str):
    """Injeksi teks langsung ke elemen prompt dengan JavaScript."""
    js_code = f"""
    document.querySelector("div[id='prompt-textarea']").innerText = `{text}`;
    """
    driver.run_js(js_code)


def send_prompt(driver: Driver, prompt: str):
    """Mengirim prompt dengan injeksi JavaScript."""
    global HIT_BUTTON_SEND_PROMPT

    default_prompt = """Parafrasekan [artikel lama] ini dan gunakan kalimat aktif dan kalimat pendek untuk membuat konten lebih mudah dibaca oleh semua kalangan
    agar artikel lebih menarik, tanpa ada pengurangan maksud kata dan arti inti dari artikel sebelum nya\n\n dan buatkan struktur ulang untuk kepentingan SEO \n\n buaatkan hasil nya menjadi struktur html SEMATIC dan hanya kode html """

    full_prompt = f"{default_prompt} {prompt}"

    driver.wait_for_element("div[id='prompt-textarea']", Wait.LONG)

    # Inject teks langsung ke input prompt
    inject_text_with_js(driver, full_prompt)

    # Klik tombol kirim
    driver.click("button[aria-label='Send prompt']", Wait.LONG)

    HIT_BUTTON_SEND_PROMPT += 1
    time.sleep(2)


def get_response(driver: Driver, prompt: str) -> str:
    """Mengambil respons terakhir dari ChatGPT."""
    send_prompt(driver, prompt)

    while True:
        # Cek apakah tombol 'Copy' sudah muncul, berarti respons siap
        buttons = driver.select_all("button[aria-label='Copy']", Wait.LONG)
        if len(buttons) >= HIT_BUTTON_SEND_PROMPT:
            responses = driver.select_all(".markdown", Wait.SHORT)
            response_text = responses[-1].text  # Ambil respons terakhir
            return response_text  # Kembalikan respons


@browser(
    reuse_driver=True,
    close_on_crash=True,
    user_agent=UserAgent.HASHED,
    window_size=WindowSize.HASHED,
)
def open_chatgpt(driver: Driver, data={}):
    """Membuka halaman ChatGPT dan menambahkan driver ke antrian (queue)."""
    driver.google_get("https://chatgpt.com/")
    q.put(driver)  # Tambahkan driver ke queue


def get_driver() -> Driver:
    """Mengambil driver dari queue."""
    return q.get()


def check_popup(driver: Driver):
    """Cek dan klik popup jika muncul."""
    try:
        result = driver.wait_for_element(
            "a[class='mt-5 cursor-pointer text-sm font-semibold text-token-text-secondary underline']",
            wait=Wait.SHORT,
        )
        if result:
            result.click()
            print("[*] Popup terdeteksi dan diklik.")
    except:
        print("[*] Tidak ada popup yang muncul.")


def runAI(prompts):
    """Jalankan penerjemahan untuk setiap prompt secara berurutan."""
    # Ambil driver dari antrian
    driver = get_driver()

    # Proses setiap prompt satu per satu
    print(f"[*] Memproses prompt: {prompts}")
    try:
        response = get_response(driver, prompts)
        print(f"[Response]: {response}\n")
    except Exception as e:
        print(f"[Error]: {e}")

    print("[*] Semua prompt selesai diproses.")


# if __name__ == "__main__":
#     # Daftar prompt untuk dijalankan
#     prompts = [
#         "Apa itu AI?",
#     ]

#     # Buka dan siapkan driver untuk tiap sesi
#     open_chatgpt()  # Memulai session dan menambahkan driver ke queue

#     # Tunggu beberapa detik agar driver siap
#     time.sleep(5)

#     # Jalankan proses utama
#     runAI(prompts)
