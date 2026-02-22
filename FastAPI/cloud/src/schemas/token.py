from pydantic import BaseModel, Field

class Token(BaseModel):
    access_token: str = Field(description="JWT Access token")
    token_type: str = Field(default="bearer", description="Token type")

class TokenData(BaseModel):
    email: str | None = Field(default=None, description="User email from token")