import uvicorn
from fastapi import FastAPI
from router import router
from settings import Settings

if Settings.ENV == "PROD":
    app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
    from docs_security import secure_docs

    secure_docs(
        app,
        admin_username=Settings.DOCS_ADMIN_USERNAME,
        admin_password=Settings.DOCS_ADMIN_PASSWORD,
        title="Copyai Selenium",
    )
else:
    app = FastAPI(title="Copyai Selenium", version="2.0.0")

app.include_router(router)

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=Settings.SERVER_HOST,
        port=Settings.SERVER_PORT,
        log_level=Settings.LOG_LEVEL,
    )
