from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from src.model.planosModel.AdesaoPlanoConfig import AdesaoPlanoConfig
from src.model.planosModel.planosConfig import Planos


def criar_adesao_controller(usuario_id: int, plano_id: int, data_validade: datetime, session: Session):
    plano = session.query(Planos).filter(Planos.id_plano == plano_id).first()
    if not plano:
        raise HTTPException(status_code=404, detail="Plano não encontrado.")

    nova = AdesaoPlanoConfig(
        fk_id_user=usuario_id,
        fk_id_plano=plano_id,
        data_validade=data_validade
    )

    session.add(nova)
    session.commit()
    session.refresh(nova)
    return nova


def listar_adesoes_usuario_controller(usuario_id: int, session: Session):
    return session.query(AdesaoPlanoConfig).filter(
        AdesaoPlanoConfig.fk_id_user == usuario_id
    ).all()

