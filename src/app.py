from fastapi import FastAPI
from src.routes import router
import uvicorn
import logging


logger = logging.getLogger("fastapi-logger")
logger.setLevel(logging.DEBUG)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

console_handler.setFormatter(formatter)

logger.addHandler(console_handler)

app = FastAPI()
app.include_router(router=router, prefix="/api/v1")


if __name__ == "__main__":
    uvicorn.run("app:app", port=5000)