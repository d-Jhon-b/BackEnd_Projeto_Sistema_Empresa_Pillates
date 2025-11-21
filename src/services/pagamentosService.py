from datetime import datetime, timedelta
from decimal import Decimal
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import Dict, Union, Optional, Any

from src.controllers.validations.permissionValidation import UserValidation
from src.model.financasModel.pagamentoConfig import Pagamento
from src.model.planosModel.contratoConfig import Contrato 
from src.model.financasModel.vendaExtraConfig import VendaExtra
from src.model.userModel.typeUser.aluno import Estudante 
from src.model.AlunoModel import AlunoModel

class PagamentoService:

    def __init__(self, session_db: Session):
        self.db = session_db

    def gerar_pagamentos_contrato(self, contrato: Contrato, current_user: Dict[str, Any]):
        UserValidation._check_aluno_or_admin_permission(current_user=current_user)

        valor_total = contrato.valor_final
        data_inicio:datetime = contrato.data_inicio
        data_termino:datetime = contrato.data_termino
        
        duracao_dias = (data_termino - data_inicio).days
        num_parcelas = max(1, round(duracao_dias / 30.0)) 
        
        valor_parcela:Decimal = valor_total / Decimal(num_parcelas)
        
        parcelas_criadas = []
        
        for i in range(num_parcelas):
            data_vencimento = data_inicio.replace(day=data_inicio.day) + timedelta(days=30 * (i + 1))
            
            novo_pagamento = Pagamento(
                fk_id_contrato=contrato.id_contrato,
                fk_id_estudante=contrato.fk_id_estudante,
                fk_id_venda_extra=None, 
                valor_pagamento=valor_parcela.quantize(Decimal('0.01')),
                data_pagamento=None,
                data_vencimento=data_vencimento,
                metodo_pagamento=None,
                status_pagamento='pendente',
                descricao_pagamento=f"Parcela {i+1} de {num_parcelas} - Contrato #{contrato.id_contrato}"
            )
            self.db.add(novo_pagamento)
            parcelas_criadas.append(novo_pagamento)

        self.db.commit()
        return parcelas_criadas

    def get_pagamento_by_id(self, pagamento_id: int, current_user:Dict[str, Any])->Optional[Pagamento]:        
        pagamento = self.db.query(Pagamento).filter(Pagamento.id_pagamento == pagamento_id).first()

        # if current_user is not None:
        #     target_user_id = pagamento.fk_id_estudante
        #     UserValidation.check_self_or_admin_permission(current_user=current_user, target_user_id=target_user_id)
        if not pagamento:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail=f"Pagamento com ID {pagamento_id} não encontrado."
            )
        fk_id_estudante = pagamento.fk_id_estudante
        estudante_model = AlunoModel(db_session=self.db)
        target_user_id = estudante_model.select_id_user_by_fk_id_estudante(fk_id_estudante)

        if not target_user_id:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                detail="Pagamento encontrado, mas usuário associado não localizado."
            )
        
        UserValidation.check_self_or_admin_permission(current_user=current_user, target_user_id=target_user_id)
        return pagamento

    def registrar_pagamento(self, pagamento_id: int, metodo: str, current_user: Dict[str, Any]):

        pagamento_db:Pagamento = self.get_pagamento_by_id(pagamento_id, current_user=current_user)
        # target_user_id = pagamento_db.fk_id_estudante
        # UserValidation.check_self_or_admin_permission(current_user=current_user, target_user_id=target_user_id)

        if pagamento_db.status_pagamento == 'pago':
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Este pagamento já foi registrado como pago."
            )

        pagamento_db.status_pagamento = 'pago'
        pagamento_db.metodo_pagamento = metodo
        pagamento_db.data_pagamento = datetime.now()

        self.db.commit()
        self.db.refresh(pagamento_db)
        
        return pagamento_db
    

