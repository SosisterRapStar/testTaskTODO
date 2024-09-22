from fastapi import HTTPException


class PasswordVerificationError(HTTPException):
    def __init__(self):
        super().__init__(status_code=400, detail="Invalid username or password")
    