# --- src/utils/date_calculators.py (REVISADO) ---

from datetime import datetime
from dateutil.relativedelta import relativedelta
from typing import Any

class ValidityCalculator:
    
    @staticmethod
    def calculate_validity_date(
        tipo_plano: str, 
        is_personalizado: bool, 
        plano_obj: Any,
        start_date: datetime 
    ) -> datetime:

        
        if (is_personalizado and 
            plano_obj and 
            hasattr(plano_obj, 'is_temporario') and plano_obj.is_temporario and 
            hasattr(plano_obj, 'data_validade') and plano_obj.data_validade):
            
            return plano_obj.data_validade 
            
        # 2. Trata planos com duração relativa, usando a data injetada
        if tipo_plano == 'mensal':
            return start_date + relativedelta(months=1)
        elif tipo_plano == 'trimestral':
            return start_date + relativedelta(months=3)
        elif tipo_plano == 'semestral':
            return start_date + relativedelta(months=6)
        elif tipo_plano == 'anual':
            return start_date + relativedelta(months=12)
        else:
            # Padrão de 1 mês
            return start_date + relativedelta(months=1)