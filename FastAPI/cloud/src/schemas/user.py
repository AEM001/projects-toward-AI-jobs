from pydantic import BaseModel, Field, ConfigDict

class UserBase(BaseModel):
    email: str = Field(description="User email address")

class UserCreate(UserBase):
    password: str = Field(min_length=6, description="User password")

class UserLogin(UserBase):
    password: str = Field(description="User password")

class User(UserBase):
    id: int

    model_config = ConfigDict(from_attributes=True)