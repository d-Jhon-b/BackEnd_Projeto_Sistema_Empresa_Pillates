from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from src.database.connPostGreNeon import CreateSessionPostGre
from src.schemas.plano_schemas import Plano, PlanoCreate
from src.model.planosModel.planoModel import PlanoModel

router = APIRouter(
    prefix="/planos",
    tags=["Planos"]
)

def get_db():
    db = CreateSessionPostGre().get_session()
    try:
        yield db
    finally:
        db.close()

@router.get("/", response_model=List[Plano])
def listar_planos(db: Session = Depends(get_db)):
    return PlanoModel.get_all_planos(db)

@router.post("/", response_model=Plano, status_code=201)
def cadastrar_plano(plano: PlanoCreate, db: Session = Depends(get_db)):
    novo_plano = PlanoModel.create_plano(db, plano)
    if not novo_plano:
        raise HTTPException(status_code=400, detail="Erro ao criar plano")
    return novo_plano
