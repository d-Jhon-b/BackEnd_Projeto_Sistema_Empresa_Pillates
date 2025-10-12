from pydantic import BaseModel, ValidationError, Field
from typing import Union, Sequence, Optional, Any, Dict, Type,List

#exporatando classes de tipo

from src.model.userModel.detailsConfig.contatoConfig import contatoConfig
# from src.model.userModel.detailsConfig.emaiConfig import EmailConfig
from src.model.userModel.detailsConfig.enderecoConfig import EnderecoConfig


class UserProfilePayload(BaseModel):
    """
    Modelo para validar um payload completo contendo listas de
    contatos, e-mails e endereços de um usuário.
    """
    # default_factory=list permite que essas chaves sejam omitidas do payload
    # sem causar um erro de validação.
    # emails: List[EmailConfig] = Field(default_factory=list)

    contatos: List[contatoConfig] = Field(default_factory=list)
    enderecos: List[EnderecoConfig] = Field(default_factory=list)

# class DataValidator():
#     @staticmethod
#     def validate_profile_data(data: Dict[str, Any]) -> Optional[UserProfilePayload]:
#         try:
#             # Pydantic automaticamente valida a estrutura inteira, incluindo
#             # cada item dentro das listas.
#             validated_payload = UserProfilePayload(**data)
#             print("Sucesso! Payload completo validado com sucesso.")
            
#             return validated_payload
#         except ValidationError as e:
#             # Pydantic fornece erros detalhados, apontando exatamente
#             # onde a validação falhou (inclusive o índice da lista).
#             print(f"Erro de Validação no Payload:\n{e}\n")
#             return None


   
        




# dados_validos = {
#     "contatos": [
#         {"tipo_contato": "RESIDENCIAL", "numero_contato": "+55 11 98765-4321"}
#     ],
#     "enderecos": [
#         {"tipo_endereco": "RESIDENCIAL", "endereco": "Rua das Palmeiras, 100", "cep": "01234-567"}
#     ]
# }
# validated_data_1 = DataValidator.validate_profile_data(dados_validos)
# if validated_data_1:
#     print(f'{validated_data_1.enderecos[0].tipo_endereco}')



    # Você pode agora acessar os dados de forma segura e tipada
    # print(f"Número de e-mails validados: {len(validated_data_1.emails)}")
    # print(f"Primeiro e-mail: {validated_data_1.emails[0].endereco_email}")
    # print(validated_data_1.model_dump_json(indent=2))

