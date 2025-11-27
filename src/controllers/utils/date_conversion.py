from typing import Dict
from src.schemas.aulas_schemas import DiaSemanaEnum # Importa o Enum

class DateConverter:

    # O Mapeamento é uma propriedade de classe (privada)
    __DIA_SEMANA_INDICE: Dict[str, int] = {
        DiaSemanaEnum.SEGUNDA.value: 0,
        DiaSemanaEnum.TERCA.value: 1,
        DiaSemanaEnum.QUARTA.value: 2,
        DiaSemanaEnum.QUINTA.value: 3,
        DiaSemanaEnum.SEXTA.value: 4,
        DiaSemanaEnum.SABADO.value: 5,
        DiaSemanaEnum.DOMINGO.value: 6,
    }

    @staticmethod
    def get_weekday_index(dia_semana_str: str) -> int:

        try:
            return DateConverter.__DIA_SEMANA_INDICE[dia_semana_str]
        except KeyError:
            raise ValueError(f"Dia da semana inválido fornecido: {dia_semana_str}. Esperado um dos valores do Enum.")