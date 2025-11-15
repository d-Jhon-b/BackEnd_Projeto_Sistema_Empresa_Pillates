from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.database.connPostGreNeon import CreateSessionPostGre
from src.model.planosModel.contratoModel import (
    ContratoModel,
    ContratoStatus,
)

router = APIRouter(
    prefix="/contratos",
    tags=["Contratos"]
)

def get_db():
    create = CreateSessionPostGre()
    db = create.get_session()
    try:
        yield db
    finally:
        db.close()


# ============================
# Criar contrato
# ============================
@router.post("/", status_code=status.HTTP_201_CREATED)
def criar_contrato(dados: dict):
    try:
        novo = ContratoModel.criar_contrato(dados)
        return novo.to_dict()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============================
# Buscar por ID
# ============================
@router.get("/{contrato_id}")
def buscar_contrato(contrato_id: int):
    contrato = ContratoModel.buscar_por_id(contrato_id)
    if not contrato:
        raise HTTPException(status_code=404, detail="Contrato não encontrado")
    return contrato.to_dict()


# ============================
# Buscar contratos do usuário
# ============================
@router.get("/usuario/{user_id}")
def buscar_por_usuario(user_id: int):
    contratos = ContratoModel.buscar_por_usuario(user_id)
    return [c.to_dict() for c in contratos]


# ============================
# Atualizar status
# ============================
@router.patch("/{contrato_id}/status")
def atualizar_status(contrato_id: int, body: dict):

    if "status" not in body:
        raise HTTPException(status_code=400, detail="Campo 'status' requerido")

    try:
        status_enum = ContratoStatus(body["status"])
    except:
        raise HTTPException(
            status_code=400,
            detail=f"Status inválido. Opções: {[s.value for s in ContratoStatus]}"
        )

    atualizado = ContratoModel.atualizar_status(contrato_id, status_enum)
    if not atualizado:
        raise HTTPException(status_code=404, detail="Contrato não encontrado")

    return atualizado.to_dict()


# ============================
# Atualizar campos (plano, valor, moeda, data_fim)
# ============================
@router.patch("/{contrato_id}")
def atualizar_campos(contrato_id: int, campos: dict):

    atualizado = ContratoModel.atualizar_campos(contrato_id, campos)
    if not atualizado:
        raise HTTPException(status_code=404, detail="Contrato não encontrado")

    return atualizado.to_dict()


# ============================
# Deletar contrato
# ============================
@router.delete("/{contrato_id}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_contrato(contrato_id: int):
    sucesso = ContratoModel.deletar_contrato(contrato_id)

    if not sucesso:
        raise HTTPException(status_code=404, detail="Contrato não encontrado")

    return {"message": "Contrato deletado com sucesso"}
