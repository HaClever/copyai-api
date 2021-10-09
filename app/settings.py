import os


class Settings:
    SERVER_HOST: str = "localhost"
    SERVER_PORT: int = 777
    LOG_LEVEL: str = os.environ.get("LOG_LEVEL")
    CHROMEDRIVER_PATH: str = os.environ.get("CHROMEDRIVER_PATH")
    COOKIES_PATH: str = "/chrome_data/cookies.pkl"
    ENV: str = os.environ.get("ENV", "DEV")
    # Docs auth
    DOCS_ADMIN_USERNAME: str = os.environ.get("DOCS_ADMIN_USERNAME", "admin")
    DOCS_ADMIN_PASSWORD: str = os.environ.get("DOCS_ADMIN_PASSWORD", "admin")
    # Yandex auth
    EMAIL: str = os.environ.get("EMAIL")  # поддерживается только Yandex
    EMAIL_PASSWORD: str = os.environ.get("EMAIL_PASSWORD")

    # EMAIL = "chibsc@yandex.ru"  # поддерживается только Yandex
    # EMAIL_PASSWORD = "Qwertyu11"

    PROGECT_TITLE: str = os.environ.get("PROGECT_TITLE", "Soulport")
    RELEVANT_WEBSITE: str = os.environ.get("RELEVANT_WEBSITE", "https://soulport.ru/")
    NUMBER_OF_RETRIES: int = os.environ.get(
        "NUMBER_OF_RETRIES", 3
    )  # Количество попыток получить сгенерированный текст
