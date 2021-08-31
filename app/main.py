import uvicorn
from fastapi import FastAPI
from router import router
from settings import Settings

app = FastAPI()

app.include_router(router)

if __name__ == '__main__':
    uvicorn.run("main:app", host=Settings.SERVER_HOST, port=Settings.SERVER_PORT, log_level=Settings.LOG_LEVEL)
