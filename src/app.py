from fastapi import FastAPI
from src.routes import router
import uvicorn


app = FastAPI()
app.include_router(router=router, prefix="/api/v1")


# if __name__ == "__main__":
#     uvicorn.run("app:app", port=5000)
