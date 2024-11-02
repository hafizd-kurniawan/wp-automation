from base.driver import SeleniumDriver
import time


class Login(SeleniumDriver):

    def __init__(self, driver):
        super().__init__(driver)
        self.driver = driver

    ######################################
    # Locator
    ######################################
    _id_user_login = "user_login"
    _id_user_pas = "user_pass"
    _id_user_submit = "wp-submit"
    _url_wp_login = "http://portal-berita.local/wp-login.php"

    def enter_username(self, username):
        username_element = self.waitForElement(locator=self._id_user_login)
        self.sendKeys(username, element=username_element)

    def enter_password(self, password):
        password_element = self.waitForElement(locator=self._id_user_pas)
        self.sendKeys(password, element=password_element)

    def submit(self):
        submit_element = self.waitForElement(locator=self._id_user_submit)
        self.elementClick(element=submit_element)

    def login(self, username, password):
        self.driver.get(self._url_wp_login)
        self.enter_username(username)
        self.enter_password(password)
        self.submit()


class Template(SeleniumDriver):

    def __init__(self, driver):
        super().__init__(driver)
        self.driver = driver

    ######################################
    # Locator
    ######################################
    _url_wp_template = "http://portal-berita.local/wp-admin/edit.php?post_type=elementor_library&tabs_group=library"
    _id_btn_import_template = "elementor-import-template-trigger"
    _xp_insert_file = "//input[@type='file']"
    _xp_btn_confirm = "//button[@class='dialog-button dialog-ok dialog-confirm-ok']"
    _css_btn_import_now = "input[id='e-import-template-action']"

    def clik_import_template(self):
        self.elementClick(locator=self._id_btn_import_template, locatorType="id")

    def insert_file(self, data):
        locator = self._xp_insert_file
        insert_element = self.waitForElementPresence(locator, locatorType="xpath")
        insert_element.send_keys(data)
        time.sleep(1)

    def click_import_now(self):
        btn_element = self.waitForElement(self._css_btn_import_now, locatorType="css")
        self.elementClick(element=btn_element)
        time.sleep(1)

    def click_confirm(self):
        self.elementClick(locator=self._xp_btn_confirm, locatorType="xpath")
        time.sleep(1)

    def get_driver(self):
        return self.driver

    def import_template(self, data):
        self.driver.get(self._url_wp_template)
        self.clik_import_template()
        self.insert_file(data)
        self.click_import_now()
        self.click_confirm()


class Post(SeleniumDriver):

    def __init__(self, driver):
        super().__init__(driver)
        self.driver = driver

    ######################################
    # Locator
    ######################################
    _url_wp_post = "https://ptkaryaagungland.com/wp-admin/post-new.php?post_type=page"
    _xp_btn_new_post = "//a[@class='page-title-action']"
    _xp_btn_publish = '//button[@class="components-button editor-post-publish-panel__toggle editor-post-publish-button__button is-primary is-compact"]'
    _xp_page_editor = "//div[@class='block-editor-iframe__scale-container']"
    _xp_btn_edit_with_elementor = "//div[@id='elementor-switch-mode'] / button"
    _xp_btn_elementor_publish = (
        "//*[@id='elementor-editor-wrapper-v2'] //div[@role='group'] /button"
    )
    _js_open_template = """
    //https://www.w3schools.com/howto/howto_js_element_iframe.asp
    const iframe = document.querySelector("iframe[id='elementor-preview-iframe']").contentDocument.documentElement
    console.log(iframe)
    const elementorAddBtns = iframe.getElementsByClassName("e-view elementor-add-new-section")[0]
    elementorAddBtns.getElementsByClassName("elementor-add-section-area-button")[1].click()
    document.getElementsByClassName("elementor-component-tab")[4].click();
    """
    _js_select_template = """
    const templates = document.querySelectorAll("div#elementor-template-library-templates-container > div");
    const totalTemplate = templates.length;
    console.log(totalTemplate)
    console.log(templates[totalTemplate -1])

    // Mencari template yg terbaru
    const insertBtn = templates[totalTemplate - 1].getElementsByClassName('elementor-template-library-template-action');
    insertBtn[0].click();

    // Tunggu hingga popup notifikasi verifikasi muncul
    const btnNotifikasi = document.getElementById("elementor-insert-template-settings-dialog");
    btnNotifikasi.getElementsByClassName("dialog-confirm-ok")[0].click();
    """

    def click_add_post(self):
        btn_post = self.waitForElement(self._xp_btn_new_post, locatorType="xpath")
        self.elementClick(element=btn_post)

    def wait_loading_editor(self):
        element = self.waitForElementPresence(self._xp_btn_publish, locatorType="xpath")
        self.isElementDisplayed(element=element)
        return element

    def create_js_title(self, title):
        time.sleep(3000)
        _js_insert_title = (
            """
        //const iframe = document.querySelector("iframe[name='editor-canvas']").contentDocument.documentElement

        // Ambil elemen h1 yang dapat diedit
        const editableTitle = document.querySelector('.editor-post-title__input');

        // Fungsi untuk mengupdate teks judul dan memicu event perubahan
        function updateTitle(newTitle) {
            editableTitle.innerText = newTitle; // Mengubah teks di dalam elemen

            // Memicu event 'input' agar WordPress mendeteksi perubahan
            const event = new Event('input', { bubbles: true });
            editableTitle.dispatchEvent(event);
        }

        // Mengatur judul baru langsung tanpa prompt
        const newTitle = "%s"; // Ganti dengan judul yang diinginkan
        updateTitle(newTitle);
        """
            % title
        )
        return _js_insert_title

    def insert_title(self, title="Test title"):
        print("sleep1")
        time.sleep(3000)
        print("sleep2")
        element = self.waitForElementPresence(
            locator=self._xp_page_editor, locatorType="xpath"
        )
        self.driver.execute_script(self.create_js_title(title))

    def click_edit_with_elementor(self):
        element = self.wait_loading_editor()
        attr = element.get_attribute("aria-disabled")
        if attr != "false":
            return "Cant start elementro"
        self.elementClick(self._xp_btn_edit_with_elementor, locatorType="xpath")
        time.sleep(15)
        self.driver.execute_script(self._js_open_template)
        time.sleep(15)
        self.driver.execute_script(self._js_select_template)

    def click_publish_elementor(self):
        self.elementClick(self._xp_btn_elementor_publish, locatorType="xpath")

    def add_post(self):
        self.driver.get(self._url_wp_post)
        # self.wait_loading_editor()
        # print("loaddddd")
        # time.sleep(3000)
        # self.insert_title()
        # self.click_edit_with_elementor()
        # time.sleep(5)
        # self.click_publish_elementor()
        # self.click_publish_elementor()
        # time.sleep(20)
        print()
