from pydantic import BaseModel, ValidationError
from typing import Type, Optional, Any

# Importe seus modelos Pydantic
from src.model.userModel.detailsConfig.contatoConfig import contatoConfig
from src.model.userModel.detailsConfig.emaiConfig import EmailConfig
from src.model.userModel.detailsConfig.enderecoConfig import EnderecoConfig

class DataValidator:
    """
    Classe centralizada para validar dicionários de dados
    contra modelos Pydantic específicos.
    """

    @staticmethod
    def validate(data: dict, model: Type[BaseModel]) -> Optional[BaseModel]:
        """
        Valida um dicionário de dados contra um modelo Pydantic específico.

        Args:
            data (dict): O dicionário com os dados a serem validados.
            model (Type[BaseModel]): A classe do modelo Pydantic a ser usada.

        Returns:
            Optional[BaseModel]: Uma instância do modelo validado se for bem-sucedido,
                                 ou None se ocorrer um erro de validação.
        """
        try:
            # Tenta criar uma instância do modelo com os dados fornecidos
            validated_object = model(**data)
            print(f"Sucesso: Dados validados com o modelo '{model.__name__}'.")
            return validated_object
        except ValidationError as e:
            # Captura o erro específico de validação do Pydantic
            print(f"Erro de Validação para o modelo '{model.__name__}':\n{e}\n")
            return None
        




        
dados_endereco_validos = {
    "tipo_endereco": "RESIDENCIAL",
    "endereco": "Rua das Flores, 123",
    "cep": "12345-678"
}
endereco_obj = DataValidator.validate(data=dados_endereco_validos, model=EnderecoConfig)

if endereco_obj:
    #transforma para string (model_dump_json)
    print("Objeto validado retornado:", endereco_obj.model_dump_json(indent=2))

