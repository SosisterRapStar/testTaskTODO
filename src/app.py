from fastapi import FastAPI



app = FastAPI()






@app.get()
async def get_notes():
    pass

@app.post()
async def create_note():
    pass

@app.put()
async def update_note():
    pass

@app.delete()
async def delete_note():
    pass

@app.post()
async def add_tag_to_note():
    pass

