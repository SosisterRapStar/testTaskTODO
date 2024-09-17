from pydantic import BaseModel, ConfigDict


class TokenResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    access_token: str
    refresh_token: str
    expires_in: int
    token_type: str = "Bearer"
