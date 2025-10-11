from pydantic import BaseModel
from typing import Union, Sequence, Optional, Any, Dict

#exporatando classes de tipo

from src.model.userModel.detailsConfig.contatoConfig import contatoConfig
from src.model.userModel.detailsConfig.emaiConfig import emailConfig
from src.model.userModel.detailsConfig.enderecoConfig import EnderecoConfig


class ValidatioTypes():
    def __init__(self):
        self.validation = {'v_endereco_type': None, 'v_email_type': None,'v_contato_type':None}


    def validationTypes(self, **data):
        try:
            self.endereco = EnderecoConfig(**data)
            if self.endereco:
                self.validation['v_endereco_type'] = True
                # print(f"Objeto validado: {self.endereco.model_dump_json(indent=2)}")
            self.contato = contatoConfig(**data)

            # self.endereco = 
        except Exception as err:
            print(f'Erro na validção: {err}')
            return None

# data={
#     "tipo_endereco": "RESIDENCIAL",  # Pydantic aceita a string do Enum
#     "endereco": "Rua das Flores, 123",
#     "cep": "01000-000"
# }

# try:
#     validation = ValidatioTypes()
#     test_validation = validation.validationTypes(**data)
   
# except:
#    print(f'erro ao validar')