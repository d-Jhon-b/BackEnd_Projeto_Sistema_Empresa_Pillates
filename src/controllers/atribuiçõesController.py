from sqlalchemy.orm import Session
from fastapi import HTTPException
from src.model.planosModel.planosConfig import Planos
from src.model.planosModel.contratoModel import ContratoConfig
from src.model.planosModel.AdesaoPlanoConfig import AdesaoPlanoConfig


def atribuir_plano_controller(usuario_id: int, plano_id: int, session: Session):
    plano = session.query(Planos).filter(Planos.id_plano == plano_id).first()
    if not plano:
        raise HTTPException(404, "Plano não encontrado")

    return plano


def atribuir_contrato_controller(usuario_id: int, session: Session):
    novo = ContratoConfig(
        fk_id_user=usuario_id,
        fk_id_plano=None,
        valor=0,
        moeda="BRL"
    )
    session.add(novo)
    session.commit()
    session.refresh(novo)
    return novo


def atribuir_adesao_plano_controller(usuario_id: int, plano_id: int, data_validade, session: Session):
    nova = AdesaoPlanoConfig(
        fk_id_user=usuario_id,
        fk_id_plano=plano_id,
        data_validade=data_validade
    )
    session.add(nova)
    session.commit()
    session.refresh(nova)
    return nova
