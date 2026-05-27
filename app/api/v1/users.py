from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi_cache.decorator import cache

from app.api.dependencies import get_db, get_current_user
from app.models.user import User
from app.crud import user as crud_user
from app.schemas.clinic import ClinicResponse
from app.schemas.user import UserResponse, UserUpdate, UserCreate

router = APIRouter()

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_in: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    **Criar um novo usuário no sistema.**

    Permite o registro de um novo usuário na plataforma (Paciente, Médico, Secretária ou Administrador). A senha enviada será armazenada de forma segura (hash bcrypt).

    ### 📌 Requisitos de Segurança
    * Rota de acesso para auto-cadastro (*sign-up*) via aplicativo móvel da clínica.

    ### 📥 Parâmetros de Entrada
    * Corpo da requisição contendo obrigatoriamente: `email`, `name`, `password`, `clinic_id` e o `role`.

    ### 📤 Retornos esperados
    * **`201 CREATED`**: Retorna os dados completos do novo usuário recém-criado.
    * **`400 BAD REQUEST`**: Já existe um usuário cadastrado com o e-mail informado.
    """
    existing_user = await crud_user.get_user_by_email(db, email=user_in.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email already exists in the system."
        )
        
    new_user = await crud_user.create_user(db, user_in=user_in)
    return new_user

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    **Recuperar informações detalhadas do perfil de um usuário.**

    Este endpoint obtém os dados cadastrais do usuário correspondente ao identificador fornecido. 

    ### 📌 Requisitos de Segurança
    * Requer cabeçalho HTTP **`Authorization: Bearer <access_token>`** válido.
    * Qualquer usuário autenticado pode obter as próprias informações ou as de outros usuários do sistema (sujeito a regras de confidencialidade adicionais no frontend).

    ### 📥 Parâmetros de Entrada
    * `user_id` *(UUID, na URL)*: Identificador único universal do usuário desejado.

    ### 📤 Retornos esperados
    * **`200 OK`**: Retorna os dados completos do usuário (ID, Nome, Email, Papel/Role, Telefone, Data de Nascimento, Avatar, ID da Clínica e status ativo/inativo).
    * **`401 UNAUTHORIZED`**: Token de acesso inválido ou expirado.
    * **`404 NOT FOUND`**: Usuário com o `user_id` fornecido não foi encontrado no banco de dados.
    """
    user = await crud_user.get_user_by_id(db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: UUID,
    user_in: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    **Atualizar dados cadastrais do perfil de um usuário.**

    Permite que um usuário modifique seus próprios dados de contato e de identificação (como nome, telefone e foto de avatar).

    ### 📌 Requisitos de Segurança
    * Requer cabeçalho HTTP **`Authorization: Bearer <access_token>`** válido.
    * **Restrição de Acesso**: O usuário logado só pode modificar o próprio perfil (`current_user.id == user_id`), a menos que possua o papel funcional de **`admin`**.

    ### 📥 Parâmetros de Entrada
    * `user_id` *(UUID, na URL)*: Identificador único universal do usuário a ser atualizado.
    * `name` *(string, opcional, no corpo)*: Novo nome completo do usuário.
    * `phone` *(string, opcional, no corpo)*: Novo número de telefone formatado.
    * `avatar_url` *(string, opcional, no corpo)*: Nova URL da imagem de avatar do usuário.

    ### 📤 Retornos esperados
    * **`200 OK`**: Retorna os dados do usuário atualizados com sucesso e o carimbo de data/hora da modificação (`updated_at`).
    * **`401 UNAUTHORIZED`**: Token de acesso inválido ou expirado.
    * **`403 FORBIDDEN`**: Tentativa de atualizar o perfil de outro usuário sem possuir a role `admin`.
    * **`404 NOT FOUND`**: Usuário com o `user_id` fornecido não foi encontrado.
    """
    if current_user.id != user_id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not enough permissions")
        
    user = await crud_user.get_user_by_id(db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    user = await crud_user.update_user(db, db_user=user, user_in=user_in)
    return user

@router.get("/{user_id}/clinic", response_model=ClinicResponse)
@cache(expire=300)  # Faz o cache dessa resposta no Redis por 5 minutos
async def get_user_clinic(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    **Obter informações completas sobre a clínica associada ao usuário.**

    Este recurso é vital para aplicações SaaS *white-label*, retornando os metadados visuais, cores primárias/secundárias, logotipo e informações de contato da clínica à qual o usuário pertence.

    ### 📌 Requisitos de Segurança & Performance
    * Requer cabeçalho HTTP **`Authorization: Bearer <access_token>`** válido.
    * **Caching Otimizado**: Esta rota implementa cache automático no **Redis** com expiração de **5 minutos (300 segundos)** para reduzir a latência de rede e a carga no banco de dados.

    ### 📥 Parâmetros de Entrada
    * `user_id` *(UUID, na URL)*: Identificador único do usuário cujo vínculo com a clínica será consultado.

    ### 📤 Retornos esperados
    * **`200 OK`**: Informações da clínica (ID, Nome, URL do logo, Paleta de cores, Endereço completo, Telefone, Email e Website).
    * **`401 UNAUTHORIZED`**: Token de acesso inválido ou expirado.
    * **`404 NOT FOUND`**: Usuário não encontrado ou clínica não associada ao usuário informado.
    """
    user = await crud_user.get_user_by_id(db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    clinic = await crud_user.get_clinic_by_id(db, clinic_id=user.clinic_id)
    if not clinic:
        raise HTTPException(status_code=404, detail="Clinic not found")
        
    return clinic
