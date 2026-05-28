from typing import Optional
from pydantic import BaseModel, Field
from app.schemas.user import UserResponse

class Token(BaseModel):
    access_token: str = Field(..., description="Token JWT de acesso (curta duração) para autorizar requisições protegidas.", examples=["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."])
    refresh_token: str = Field(..., description="Token JWT de atualização (longa duração) para obter novos access tokens.", examples=["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."])
    token_type: str = Field(default="bearer", description="Esquema de autenticação utilizado. Sempre 'bearer'.", examples=["bearer"])
    user: UserResponse = Field(..., description="Dados resumidos do perfil do usuário autenticado.")

class TokenPayload(BaseModel):
    sub: Optional[str] = Field(None, description="Identificador único (UUID) do usuário (Subject do token JWT).")
    role: Optional[str] = Field(None, description="Nível de acesso (role) do usuário codificado no token.")

class LoginRequest(BaseModel):
    email: str = Field(..., description="Endereço de email cadastrado do usuário.", examples=["maria@clinic.com"])
    password: str = Field(..., description="Senha secreta correspondente à conta.", examples=["senha_segura123"])

class RefreshRequest(BaseModel):
    refresh_token: str = Field(..., description="Token JWT de atualização obtido no login.", examples=["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."])

class AccessTokenResponse(BaseModel):
    access_token: str = Field(..., description="Novo token JWT de acesso (curta duração).", examples=["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."])
    token_type: str = Field(default="bearer", description="Esquema de autenticação utilizado.", examples=["bearer"])
