from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.api.dependencies import get_db, get_current_user
import jwt
from app.core.security import verify_password, create_access_token, create_refresh_token, ALGORITHM
from app.core.config import settings
from app.models.user import User
from app.schemas.auth import LoginRequest, Token, RefreshRequest, AccessTokenResponse
from app.schemas.user import UserResponse

router = APIRouter()

@router.post("/login", response_model=Token)
async def login(
    request: LoginRequest, 
    db: AsyncSession = Depends(get_db)
):
    """
    **Autenticar usuário na plataforma utilizando email e senha.**

    Este endpoint realiza a validação das credenciais de acesso do usuário. Em caso de sucesso, gera um par de tokens JWT (JSON Web Token) criptografados e assina a sessão.

    ### 📌 Requisitos de Segurança
    * Rota **Pública** (não requer cabeçalhos de autorização prévios).
    * Protegida por limitador de taxa (**Rate Limiting**) para mitigar ataques de força bruta.

    ### 📥 Parâmetros de Entrada
    * `email` *(string, obrigatório)*: Endereço de email registrado do usuário.
    * `password` *(string, obrigatório)*: Senha associada à conta.

    ### 📤 Retornos esperados
    * **`200 OK`**: Retorna os tokens JWT de acesso (`access_token`), atualização (`refresh_token`), tipo do token (`bearer`) e o payload com os dados cadastrais básicos do usuário.
    * **`401 UNAUTHORIZED`**: Credenciais incorretas (email ou senha inválidos).
    * **`400 BAD REQUEST`**: Conta de usuário desativada (`is_active` igual a falso).
    """
    result = await db.execute(select(User).where(User.email == request.email))
    user = result.scalar_one_or_none()
    
    if not user or not verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
        
    access_token = create_access_token(subject=user.id, role=user.role)
    refresh_token = create_refresh_token(subject=user.id, role=user.role)
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": user
    }

@router.post("/refresh", response_model=AccessTokenResponse)
async def refresh_token(request: RefreshRequest):
    """
    **Renovar o token de acesso usando o refresh token.**

    Permite que o cliente obtenha um novo `access_token` sem exigir nova autenticação com email e senha. O `refresh_token` deve ter sido obtido originalmente via `/auth/login`.

    ### 📌 Requisitos de Segurança
    * Rota **Pública** — não requer `Authorization` header.
    * O `refresh_token` deve conter o campo `"type": "refresh"` no payload.

    ### 📤 Retornos esperados
    * **`200 OK`**: Novo `access_token` gerado com sucesso.
    * **`401 UNAUTHORIZED`**: Token inválido, expirado ou não é do tipo refresh.
    """
    try:
        payload = jwt.decode(request.refresh_token, settings.SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.PyJWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired refresh token")

    if payload.get("type") != "refresh":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is not a refresh token")

    subject = payload.get("sub")
    role = payload.get("role")
    if not subject or not role:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")

    access_token = create_access_token(subject=subject, role=role)
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/logout")
async def logout(current_user: User = Depends(get_current_user)):
    """
    **Encerrar a sessão ativa do usuário.**

    Como a autenticação JWT é essencialmente *stateless*, este endpoint atua como uma sinalização para que o cliente descarte com segurança os tokens armazenados localmente.

    ### 📌 Requisitos de Segurança
    * Requer cabeçalho HTTP **`Authorization: Bearer <access_token>`** válido.

    ### 📤 Retornos esperados
    * **`200 OK`**: Confirmação de encerramento de sessão bem-sucedida.
    * **`401 UNAUTHORIZED`**: Token de acesso inválido ou expirado.
    """
    return {"message": "Logged out successfully"}
