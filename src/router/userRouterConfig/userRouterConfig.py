from pydantic import BaseModel, Field, EmailStr
from typing import Dict, Any


class LoginRequest(BaseModel):
    email: EmailStr = Field(..., title="Email do Usuário")
    senha: str = Field(..., title="Senha em texto puro")
    
class LoginResponse(BaseModel):
    message: str
    access_token: str
    token_type: str = "bearer"
    user_data: Dict[str, Any]
