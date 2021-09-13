from structlog import get_logger
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
import time
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from settings import Settings
import pickle
import pathlib
from datetime import datetime

class Webdriver:
    logger = None
    driver = None

    def __init__(self):
        self.logger = get_logger()
        self.driver = self.initialize_browser_driver()
        self.wait = WebDriverWait(self.driver, 15)
        self.bigger_wait = WebDriverWait(self.driver, 30)

    def initialize_browser_driver(self) -> webdriver:
        """
        Инициализируем драйвер для работы с браузером.
        """
        options = Options()
        options.add_argument('--headless')  # Выкл. графический интерфейс браузера
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('window-size=1920x1080')
        options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36\
                             (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36')
        options.add_argument('start-maximized')
        options.add_argument('--proxy-server=mitmproxy:8080')
        options.add_argument('--allow-running-insecure-content')
        options.add_argument('--ignore-certificate-errors')
        options.add_argument('user-data-dir=/chrome_data')
        driver = webdriver.Chrome(  # Объект для управления браузером.
            executable_path=Settings.CHROMEDRIVER_PATH,
            chrome_options=options
        )
        return driver

    def open_new_tab(self):
        self.driver.execute_script('''window.open("about:blank", "_blank");''')
        self.driver.switch_to.window(self.driver.window_handles[-1])

    def upload_cookies_to_browser(self) -> None:
        """
        Загружаем cookies в открытое окно браузера.
        """
        try:
            cookies = pickle.load(open(Settings.COOKIES_PATH, "rb"))
            # cookies = pickle.load(open('cookies/cookies.pkl', "rb"))
            for cookie in cookies:
                self.driver.add_cookie(cookie)
            self.logger.info('Куки загружены')
        except Exception as exc:
            self.logger.warning(f'Cookie import error: {exc}')

    def check_if_browser_is_detectable(self):
        '''Тест драйвера на его детект сайтами. Результат сохраняется скриншотом test.png
           Желательно чтобы все ячейки на скриншоте были зелеными'''
        self.driver.get('https://intoli.com/blog/not-possible-to-block-chrome-headless/chrome-headless-test.html')
        self.driver.save_screenshot('test.png')

    @classmethod
    def take_screenshot_on_error(cls, func):
        def save_error_screenshot(self, *args, **kwargs):
            try:
                return func(self, *args, **kwargs)
            except Exception as e:
                screenshot_dir_path = pathlib.Path('../error_screenshots')
                screenshot_dir_path.mkdir(exist_ok=True)
                round_time = str(datetime.now()).split('.')[0].replace(' ', '-').replace(':', '-')
                screnshot_path = (f'{str(screenshot_dir_path)}/{type(e).__name__}({round_time}).png')
                self.driver.save_screenshot(screnshot_path)
                raise
        return save_error_screenshot

class YandexSelenium(Webdriver):
    @Webdriver.take_screenshot_on_error
    def login_to_yandex_mail(self):
        self.driver.get('https://passport.yandex.ru/auth')
        email_input = self.wait.until(EC.presence_of_element_located((By.ID, 'passp-field-login')))
        email_input.send_keys(Settings.EMAIL)
        enter_button = self.wait.until(EC.element_to_be_clickable((By.ID, 'passp:sign-in')))
        enter_button.click()
        email_input = self.wait.until(EC.presence_of_element_located((By.ID, 'passp-field-passwd')))
        email_input.send_keys(Settings.EMAIL_PASSWORD)
        enter_button = self.wait.until(EC.element_to_be_clickable((By.ID, 'passp:sign-in')))
        enter_button.click()
        time.sleep(1)
        try:
            self.driver.find_element_by_id('passp-field-phoneNumber')  # Если Яндекс просит подтвердить телефон
            skip = self.driver.find_element_by_css_selector('button[data-t="button:pseudo"]')
            skip.click()
        except NoSuchElementException:
            pass
        self.logger.info('Залогинились в Яндекс')

    @Webdriver.take_screenshot_on_error
    def yandex_get_newest_mail(self, mail_title):
        try:
            account_button = self.wait.until(EC.visibility_of_element_located((By.CLASS_NAME, 'user-pic')))
        except TimeoutException:
            account_button = self.wait.until(EC.visibility_of_element_located((By.CLASS_NAME, 'user-account')))
        account_button.click()
        mail_button = self.wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'menu__list-item')))
        mail_button.click()
        self.logger.info('Ждем прибытия письма 23 сек ...')
        time.sleep(23)  # подождать, пока письмо не придет.
        first_mail = self.wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'ns-view-messages-item-wrap')))
        if mail_title in first_mail.text:
            first_mail.click()
        else:
            self.logger.info('Письмо с искомым заголовком не найдено')
            raise
        try:
            time.sleep(0.5)
            first_in_chain = first_mail.find_elements_by_class_name('mail-MessageSnippet-Content')[1]
            first_in_chain.click()
        except IndexError:
            pass
        message_body = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'js-message-body')))
        self.logger.info('Письмо получено')

        return message_body

class CopyAiSelenium(YandexSelenium):

    @Webdriver.take_screenshot_on_error
    def log_in_if_not_loggined(self):
        self.driver.get("https://www.copy.ai/app#")
        try:
            time.sleep(3)
            self.driver.find_element_by_class_name('tool-scroll')
            self.logger.info('Залогинились в CopyAi')
            pickle.dump(self.driver.get_cookies(), open(Settings.COOKIES_PATH, "wb"))  # Сохранение куки
            self.logger.info('Куки обновлены')
        except NoSuchElementException:
            self.logger.info('Нужно залогиниться')
            self.login_to_copyai()

    def login_to_copyai(self):
        self.driver.get("https://www.copy.ai/")
        self.upload_cookies_to_browser()
        self.driver.get("https://www.copy.ai/app#")
        # self.driver.get("https://www.copy.ai/sign-in")

        # login_button = self.wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'login-button')))
        # login_button.click()

        email_input = self.wait.until(EC.presence_of_element_located((By.ID, 'email')))
        email_input.send_keys(Settings.EMAIL)

        login_button = self.wait.until(EC.element_to_be_clickable((By.ID, 'login')))
        login_button.click()

        self.open_new_tab()
        self.login_to_yandex_mail()
        message = self.yandex_get_newest_mail('Log in to CopyAI')
        time.sleep(2)
        for strong in message.find_elements_by_tag_name('strong'):
            if strong.text == 'Log in to CopyAI':
                strong.click()
                break
        self.driver.switch_to.window(self.driver.window_handles[0])
        try:
            if self.wait.until(EC.text_to_be_present_in_element((By.ID, 'next-button-welcome'), 'Continue')):
                self.logger.info('Залогинились в CopyAi')
                welcome_button = self.driver.find_element_by_id('next-button-welcome')
                welcome_button.click()
                pickle.dump(self.driver.get_cookies(), open(Settings.COOKIES_PATH, "wb"))  # Сохранение куки
                self.logger.info('Куки обновлены')
        except TimeoutException:
            self.driver.execute_script("window.history.go(-1)")

    @Webdriver.take_screenshot_on_error
    def copyai_select_option(self, option):
        # try:
        #     skip_button = self.wait.until(EC.element_to_be_clickable((By.ID, 'skip-button')))
        #     skip_button.click()
        #     try:
        #         cross = self.wait.until(EC.element_to_be_clickable((By.ID, 'vid-modal-close')))
        #         cross.click()
        #     except TimeoutException:
        #         pass
        # except TimeoutException:

        top_nav = self.driver.find_element_by_id('nav')
        self.driver.execute_script("arguments[0].style.visibility='hidden'", top_nav)

        expand_button = self.driver.find_element_by_id('expand-side-button')
        if expand_button.is_displayed():
            expand_button.click()
        option_menu = self.wait.until(EC.visibility_of_element_located((By.CLASS_NAME, 'tool-scroll')))
        for op in option_menu.find_elements_by_tag_name('a'):
            if op.text == option:
                op.click()
                self.logger.info(f'Выбрана опция "{option}"')
                break

    @Webdriver.take_screenshot_on_error
    def copyai_change_language(self):
        input_lang = self.wait.until(EC.presence_of_element_located((By.ID, 'input-lang-text')))
        if 'RU' not in input_lang.text:
            translate_from = self.wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'input-lang-dropdown')))
            translate_from.click()
            translate_from.click()
            translate_from_list = self.wait.until(EC.presence_of_element_located((By.ID, 'w-dropdown-list-1')))
            for lang in translate_from_list.find_elements_by_tag_name('a'):
                if lang.get_attribute('data-code') == 'RU':
                    lang.click()
        output_lang = self.wait.until(EC.presence_of_element_located((By.ID, 'output-lang-text')))
        if 'RU' not in output_lang.text:
            translate_to = self.wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'output-lang-dropdown')))
            translate_to.click()
            translate_to.click()
            translate_to_list = self.wait.until(EC.presence_of_element_located((By.ID, 'w-dropdown-list-2')))
            for lang in translate_to_list.find_elements_by_tag_name('a'):
                if lang.get_attribute('data-code') == 'RU':
                    lang.click()

    @Webdriver.take_screenshot_on_error
    def copyai_get_response(self, product_description, product_name=None):
        self.copyai_change_language()
        if product_name:
            product_name_input = self.wait.until(EC.presence_of_element_located((By.ID, 'product-name')))
            product_name_input.clear()
            product_name_input.send_keys(product_name)
        product_description_input = self.wait.until(EC.presence_of_element_located((By.ID, 'product-description')))
        product_description_input.clear()
        product_description_input.send_keys(product_description)
        create_button = self.wait.until(EC.element_to_be_clickable((By.ID, 'create-button')))
        create_button.click()
        result_greed = self.bigger_wait.until(EC.visibility_of_any_elements_located((By.CLASS_NAME, 'input-text-field-result')))
        result_greed = self.wait.until(EC.presence_of_element_located((By.ID, 'result-grid')))
        result = []
        for div in result_greed.find_elements_by_tag_name('div'):
            if div.get_attribute('original_text'):
                result.append(div.get_attribute('original_text'))
        return result

if __name__ == '__main__':
    w = Webdriver()
    w.check_if_browser_is_detectable()
