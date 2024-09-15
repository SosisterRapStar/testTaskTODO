from fastapi import APIRouter


router = APIRouter(tags=["Notes"])


@router.get("/")
async def get_notes():
    pass


@router.post("/")
async def create_note():
    pass


@router.put()
async def update_note():
    pass


@router.delete()
async def delete_note():
    pass


@router.post()
async def add_tag_to_note():
    pass
