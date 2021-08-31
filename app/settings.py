import os

class Settings:
    SERVER_HOST: str = 'localhost'
    SERVER_PORT: int = 777
    LOG_LEVEL: str = os.environ.get('LOG_LEVEL')
    EMAIL: str = os.environ.get('EMAIL')
    EMAIL_PASSWORD: str = os.environ.get('EMAIL_PASSWORD')
    CHROMEDRIVER_PATH: str = os.environ.get('CHROMEDRIVER_PATH')
    COOKIES_PATH: str = './chrome_data/cookies.pkl'
