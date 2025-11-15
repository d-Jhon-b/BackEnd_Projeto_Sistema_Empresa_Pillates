from fastapi import APIRouter, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime

from src.database.connPostGreNeon import CreateSessionPostGre
from src.model.planosModel.AdesaoPlanoConfig import AdesaoPlanoConfig

router = APIRouter(
    prefix="/adesao",
    tags=["Adesão de Plano"]
)


def get_db():
    create = CreateSessionPostGre()
    db = create.get_session()
    try:
        yield db
    finally:
        db.close()


# ===========================================================
# Criar adesão de plano
# ===========================================================
@router.post("/", status_code=status.HTTP_201_CREATED)
def criar_adesao(dados: dict):

    required = ["fk_id_user", "data_validade"]

    for campo in required:
        if campo not in dados:
            raise HTTPException(
                status_code=400,
                detail=f"Campo obrigatório ausente: {campo}"
            )

    try:
        db: Session = next(get_db())

        nova = AdesaoPlanoConfig(
            fk_id_user=dados["fk_id_user"],
            data_validade=datetime.fromisoformat(dados["data_validade"])
        )

        db.add(nova)
        db.commit()
        db.refresh(nova)

        return {
            "id_adesao_plano": nova.id_adesao_plano,
            "fk_id_user": nova.fk_id_user,
            "data_adesao": nova.data_adesao,
            "data_validade": nova.data_validade
        }

    except Exception as e:
        raise HTTPException(400, detail=str(e))


# ===========================================================
# Buscar adesão por ID
# ===========================================================
@router.get("/{adesao_id}")
def buscar_por_id(adesao_id: int):
    db: Session = next(get_db())
    adesao = db.query(AdesaoPlanoConfig).filter_by(id_adesao_plano=adesao_id).first()

    if not adesao:
        raise HTTPException(404, detail="Adesão não encontrada")

    return {
        "id_adesao_plano": adesao.id_adesao_plano,
        "fk_id_user": adesao.fk_id_user,
        "data_adesao": adesao.data_adesao,
        "data_validade": adesao.data_validade
    }


# ===========================================================
# Buscar todas adesões de um usuário
# ===========================================================
@router.get("/usuario/{user_id}")
def buscar_por_usuario(user_id: int):
    db: Session = next(get_db())

    adesoes = db.query(AdesaoPlanoConfig).filter_by(fk_id_user=user_id).all()

    return [
        {
            "id_adesao_plano": a.id_adesao_plano,
            "fk_id_user": a.fk_id_user,
            "data_adesao": a.data_adesao,
            "data_validade": a.data_validade
        }
        for a in adesoes
    ]


# ===========================================================
# Atualizar data de validade
# ===========================================================
@router.patch("/{adesao_id}")
def atualizar_data_validade(adesao_id: int, body: dict):
    if "data_validade" not in body:
        raise HTTPException(400, detail="Campo 'data_validade' é obrigatório")

    db: Session = next(get_db())
    adesao = db.query(AdesaoPlanoConfig).filter_by(id_adesao_plano=adesao_id).first()

    if not adesao:
        raise HTTPException(404, detail="Adesão não encontrada")

    try:
        adesao.data_validade = datetime.fromisoformat(body["data_validade"])
        db.commit()
        db.refresh(adesao)
    except Exception as e:
        raise HTTPException(400, detail=str(e))

    return {
        "id_adesao_plano": adesao.id_adesao_plano,
        "fk_id_user": adesao.fk_id_user,
        "data_adesao": adesao.data_adesao,
        "data_validade": adesao.data_validade
    }


# ===========================================================
# Deletar adesão
# ===========================================================
@router.delete("/{adesao_id}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_adesao(adesao_id: int):
    db: Session = next(get_db())

    adesao = db.query(AdesaoPlanoConfig).filter_by(id_adesao_plano=adesao_id).first()

    if not adesao:
        raise HTTPException(404, detail="Adesão não encontrada")

    db.delete(adesao)
    db.commit()

    return {"message": "Adesão deletada com sucesso"}
