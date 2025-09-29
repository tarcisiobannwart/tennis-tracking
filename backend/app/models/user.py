"""
User models for MongoDB
"""
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field
from bson import ObjectId


class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, field_schema):
        field_schema.update(type="string")


class UserRole(str):
    """User role enumeration"""
    ADMIN = "admin"
    COACH = "coach"
    PLAYER = "player"
    ANALYST = "analyst"
    VIEWER = "viewer"


class UserBase(BaseModel):
    """Base user model"""
    email: EmailStr
    username: str
    fullName: str
    role: str = UserRole.VIEWER
    isActive: bool = True
    profileImage: Optional[str] = None
    phone: Optional[str] = None
    country: Optional[str] = None
    language: str = "en"
    preferences: Optional[dict] = Field(default_factory=dict)


class UserCreate(UserBase):
    """User creation model"""
    password: str


class UserInDB(UserBase):
    """User model as stored in database"""
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    password: str
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    updatedAt: datetime = Field(default_factory=datetime.utcnow)
    lastLogin: Optional[datetime] = None
    refreshToken: Optional[str] = None

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "email": "user@example.com",
                "username": "johndoe",
                "fullName": "John Doe",
                "role": "player",
                "isActive": True,
                "createdAt": "2024-01-01T00:00:00",
                "updatedAt": "2024-01-01T00:00:00"
            }
        }


class UserResponse(UserBase):
    """User response model (without password)"""
    id: str
    createdAt: datetime
    updatedAt: datetime
    lastLogin: Optional[datetime] = None


class UserUpdate(BaseModel):
    """User update model"""
    email: Optional[EmailStr] = None
    fullName: Optional[str] = None
    profileImage: Optional[str] = None
    phone: Optional[str] = None
    country: Optional[str] = None
    language: Optional[str] = None
    preferences: Optional[dict] = None


class UserLogin(BaseModel):
    """User login model"""
    username: str
    password: str


class Token(BaseModel):
    """Token model"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Token data model"""
    user_id: str
    username: str
    role: str
    exp: datetime