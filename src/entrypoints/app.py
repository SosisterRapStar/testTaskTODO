from fastapi import FastAPI



app = FastAPI()






@app.get()
async def get_notes():
    pass


async def create_note():
    pass


async def update_note():
    pass


async def delete_note():
    pass