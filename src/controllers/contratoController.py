from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from src.model.planosModel.contratoModel import ContratoModel, ContratoConfig


def criar_contrato_controller(dados: dict, session: Session):
    contrato = ContratoConfig(**dados)
    session.add(contrato)
    session.commit()
    session.refresh(contrato)
    return contrato


def listar_contratos_usuario_controller(user_id: int, session: Session):
    return session.query(ContratoConfig).filter(
        ContratoConfig.fk_id_user == user_id
    ).all()
