from structlog import get_logger
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
import time
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    StaleElementReferenceException,
)
from settings import Settings
import pickle
import pathlib
from datetime import datetime

# import undetected_chromedriver.v2 as uc
import enums


class Webdriver:
    logger = None
    driver = None

    def __init__(self):
        self.logger = get_logger()
        # options = uc.ChromeOptions()
        # options.user_data_dir = "./chrome_data"
        # options.headless = True
        # self.driver = uc.Chrome(headless=True)
        self.driver = self.initialize_browser_driver()
        self.wait = WebDriverWait(self.driver, 15)
        self.bigger_wait = WebDriverWait(self.driver, 20)

    def initialize_browser_driver(self) -> webdriver:
        """
        Инициализируем драйвер для работы с браузером.
        """
        options = Options()
        options.add_argument("--headless")  # Выкл. графический интерфейс браузера
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("window-size=1920x1080")
        options.add_argument(
            "user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko)\
                               Chrome/80.0.3987.87 Safari/537.36"
        )
        # options.add_argument(
        #     "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)\
        #     Chrome/74.0.3729.169 Safari/537.36"
        # )
        options.add_argument("--start-maximized")
        options.add_argument("--proxy-server=mitmproxy:8080")
        options.add_argument("--allow-running-insecure-content")
        options.add_argument("--ignore-certificate-errors")
        options.add_argument("user-data-dir=/chrome_data")
        options.add_argument("--log-level=3")
        driver = webdriver.Chrome(  # Объект для управления браузером.
            executable_path=Settings.CHROMEDRIVER_PATH, options=options
        )
        return driver

    def open_new_tab(self):
        self.driver.execute_script("""window.open("about:blank", "_blank");""")
        self.driver.switch_to.window(self.driver.window_handles[-1])

    def upload_cookies_to_browser(self) -> None:
        """
        Загружаем cookies в открытое окно браузера.
        """
        try:
            cookies = pickle.load(open(Settings.COOKIES_PATH, "rb"))
            for cookie in cookies:
                self.driver.add_cookie(cookie)
            self.logger.info("Куки загружены")
        except Exception as exc:
            self.logger.warning(f"Cookie import error: {exc}")

    def check_if_browser_is_detectable(self):
        """Тест драйвера на его детект сайтами. Результат сохраняется скриншотом test.png
        Желательно чтобы все ячейки на скриншоте были зелеными"""
        self.driver.get(
            "https://intoli.com/blog/not-possible-to-block-chrome-headless/chrome-headless-test.html"
        )
        self.driver.save_screenshot("test.png")

    @classmethod
    def take_screenshot_on_error(cls, func):
        def save_error_screenshot(self, *args, **kwargs):
            try:
                return func(self, *args, **kwargs)
            except Exception as e:
                screenshot_dir_path = pathlib.Path("../error_screenshots")
                screenshot_dir_path.mkdir(exist_ok=True)
                round_time = (
                    str(datetime.now())
                    .split(".")[0]
                    .replace(" ", "-")
                    .replace(":", "-")
                )
                screnshot_path = (
                    f"{str(screenshot_dir_path)}/{type(e).__name__}({round_time}).png"
                )
                self.driver.save_screenshot(screnshot_path)
                raise

        return save_error_screenshot


class YandexSelenium(Webdriver):
    @Webdriver.take_screenshot_on_error
    def login_to_yandex_mail(self):
        self.driver.get("https://passport.yandex.ru/auth")
        self.wait.until(
            EC.presence_of_element_located((By.ID, "passp-field-login"))
        ).send_keys(Settings.EMAIL)
        self.wait.until(EC.element_to_be_clickable((By.ID, "passp:sign-in"))).click()
        self.wait.until(
            EC.presence_of_element_located((By.ID, "passp-field-passwd"))
        ).send_keys(Settings.EMAIL_PASSWORD)
        self.wait.until(EC.element_to_be_clickable((By.ID, "passp:sign-in"))).click()
        time.sleep(1)
        try:
            self.driver.find_element(
                By.ID, "passp-field-phoneNumber"
            )  # Если Яндекс просит подтвердить телефон
            self.driver.find_element(
                By.CSS_SELECTOR, 'button[data-t="button:pseudo"]'
            ).click()
        except NoSuchElementException:
            pass
        self.logger.info("Залогинились в Яндекс")

    @Webdriver.take_screenshot_on_error
    def yandex_get_newest_mail(self, mail_title):
        try:
            self.wait.until(
                EC.visibility_of_element_located((By.CLASS_NAME, "user-pic"))
            ).click()
        except TimeoutException:
            self.wait.until(
                EC.visibility_of_element_located((By.CLASS_NAME, "user-account"))
            ).click()
        self.wait.until(
            EC.element_to_be_clickable((By.CLASS_NAME, "menu__list-item"))
        ).click()
        self.wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'a[data-title="Рассылки"]'))
        ).click()  # Письмо от copy.ai теперь в рассылке
        self.logger.info("Ждем прибытия письма 30 сек ...")
        time.sleep(30)  # подождать, пока письмо не придет.
        first_mail = self.wait.until(
            EC.element_to_be_clickable((By.CLASS_NAME, "ns-view-messages-item-wrap"))
        )
        if mail_title in first_mail.text:
            first_mail.click()
        else:
            self.logger.info("Письмо с искомым заголовком не найдено")
            raise
        try:
            time.sleep(0.5)
            first_mail.find_elements(By.CLASS_NAME, "mail-MessageSnippet-Content")[
                1
            ].click()
        except IndexError:
            pass
        self.logger.info("Письмо получено")

        return self.wait.until(
            EC.presence_of_element_located((By.CLASS_NAME, "js-message-body"))
        )


class CopyAiSelenium(YandexSelenium):
    @Webdriver.take_screenshot_on_error
    def log_in_if_not_loggined(self):
        self.driver.get("https://app.copy.ai/")
        self.upload_cookies_to_browser()
        self.driver.get("https://app.copy.ai/")
        try:
            time.sleep(3)
            self.driver.find_element(
                By.CSS_SELECTOR, 'button[data-testid="sidebar-projects"]'
            )
            self.logger.info("Залогинились в CopyAi")
            pickle.dump(
                self.driver.get_cookies(), open(Settings.COOKIES_PATH, "wb")
            )  # Сохранение куки
            self.logger.info("Куки обновлены")
        except NoSuchElementException:
            self.logger.info("Нужно залогиниться")
            self.login_to_copyai()

    def login_to_copyai(self):
        self.driver.get("https://app.copy.ai/")
        # self.upload_cookies_to_browser()
        # self.driver.get("https://www.copy.ai/app#")
        self.wait.until(
            EC.presence_of_element_located((By.ID, "enter-your-email"))
        ).send_keys(Settings.EMAIL)
        for butt in self.driver.find_elements(By.TAG_NAME, "button"):
            if butt.text == "Continue":
                butt.click()
        self.open_new_tab()
        self.login_to_yandex_mail()
        message = self.yandex_get_newest_mail("Log in to CopyAI")
        time.sleep(2)
        try:
            for strong in message.find_elements(By.TAG_NAME, "strong"):
                if strong.text == "Log in to CopyAI":
                    strong.click()
                    break
        except StaleElementReferenceException:
            message_body = self.bigger_wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "js-message-body"))
            )
            self.logger.info(f"Messsage text:{message_body.text}")
            raise
        self.driver.switch_to.window(self.driver.window_handles[0])
        time.sleep(30)  # Новое приложение долго запускается
        self.wait.until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, 'button[data-testid="sidebar-projects"]')
            )
        )
        self.logger.info("Залогинились в CopyAi")
        pickle.dump(
            self.driver.get_cookies(), open(Settings.COOKIES_PATH, "wb")
        )  # Сохранение куки
        self.logger.info("Куки обновлены")

    def enter_project(self):
        self.wait.until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, 'button[data-testid="sidebar-new-project"]')
            )
        ).click()
        self.wait.until(
            EC.presence_of_element_located((By.ID, "project-title"))
        ).send_keys(Settings.PROGECT_TITLE)
        self.driver.find_element(By.ID, "relevant-website").send_keys(
            Settings.RELEVANT_WEBSITE
        )
        for butt in self.driver.find_elements(By.TAG_NAME, "button"):
            if butt.text == "Create Project":
                butt.click()
        self.logger.info("Проект создан")

    @Webdriver.take_screenshot_on_error
    def copyai_select_option(self, option: str):
        self.wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'div[class*="ml-auto"]'))
        ).click()
        for op in self.driver.find_elements(By.CSS_SELECTOR, 'li[class*="rounded-sm"]'):
            if op.text.strip() == option:
                op.click()
                self.logger.info(f'Выбрана опция "{option}"')
                break

    @Webdriver.take_screenshot_on_error
    def copyai_change_language(self, tone: enums.Tone = "Friendly"):
        self.wait.until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, 'button[data-testid="advanced-settings"]')
            )
        ).click()
        lang_inputs = self.wait.until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "css-yk16xz-control"))
        )
        self.driver.find_element(By.ID, "react-select-input-language-input").send_keys(
            "Russian"
        )
        self.driver.find_element(By.ID, "react-select-output-language-input").send_keys(
            "Russian"
        )
        self.driver.find_element(By.ID, "react-select-tone-input").send_keys(tone.value)
        lang_inputs[2].click()
        self.wait.until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, 'button[data-testid="apply-advanced-settings"]')
            )
        ).click()

    @Webdriver.take_screenshot_on_error
    def copyai_get_response(self, product_description: str, product_name: str = None):
        if product_name:
            self.wait.until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, 'input[data-testid="project-name"]')
                )
            ).send_keys(product_name)
        self.wait.until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, 'textarea[data-testid="project-desc"]')
            )
        ).send_keys(product_description)
        for retry in range(1, int(Settings.NUMBER_OF_RETRIES) + 1):
            self.wait.until(
                EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, 'button[data-testid="create-copy"]')
                )
            ).click()
            try:
                self.bigger_wait.until(
                    EC.visibility_of_any_elements_located(
                        (By.CSS_SELECTOR, 'pre[class*="result"]')
                    )
                )
                break
            except TimeoutException:
                self.logger.info(
                    f"Не удалось получить текст с {retry} попытки. Пробую еще раз ...  "
                )
                continue
        result = [
            r.text
            for r in self.driver.find_elements(By.CSS_SELECTOR, 'pre[class*="result"]')
        ]
        return result


if __name__ == "__main__":
    w = Webdriver()
    w.check_if_browser_is_detectable()
