from pydantic import BaseModel, ValidationError
from typing import Dict

#importando metodos para inserir/criar user: 
from src.model.userModel.operationsDB.insertModel import InsertValues
from src.model.userModel.operationsDB.selectModel import SelectValues


#exportando tipos de user: 
from src.model.userModel.admPlusModel import AdmPlus

#Importando values
from src.model.userModel.detailsConfig.enderecoConfig import EnderecoConfig
# from src.model.userModel.userConfig.userConfig import UserConfig
from src.model.userModel.userConfig.userConfigCompleto import UserConfigCompleto

class UserModel():
    def __init__(self, tipoUser:str, **data):
        self.tabelaUser = "usuario"
        self.tipo_logica = tipoUser.lower()
        
        # Mantém os dados brutos
        self.data_raw = data 

        try:
            # Validação
            # Valida todos os dados (User, Endereço, Contato, Email)
            self.user_data_validated = UserConfigCompleto(**data)
            
            #Separação dos Dados Validados
            self.usuario_data = self.user_data_validated.model_dump(
                exclude={
                    'enderecos',         # Detalhes aninhados
                    'contatos',          # Detalhes aninhados
                    'emails',            # Detalhes aninhados
                    'id_user_post_gre',  # ID gerado pelo DB/Não deve ser inserido
                    'id_user_mongo',     # ID do Mongo/Não é coluna do SQL
                    'tipo_logica'        # Campo de controle/Não é coluna do DB
                }
            )
            
            self.enderecos_data = self.user_data_validated.enderecos
            self.contatos_data = self.user_data_validated.contatos
            self.emails_data = self.user_data_validated.emails
            
        except ValidationError as e:
            # Captura erros de validação Pydantic
            print(f"Erro de Validação dos Dados: {e}")
            raise # Interrompe a criação se os dados forem inválidos
            
        print(f"Dados validados com sucesso para {self.tipo_logica}.")


    def _inserir_detalhes(self, fk_id_user: int) -> bool:
        instance_Insert = InsertValues()
        success = True

        for endereco_model in self.enderecos_data:
            data = endereco_model.model_dump()
            # Adiciona a Chave Estrangeira
            data['fk_id_user'] = fk_id_user 
            
            # Assumindo que a tabela é 'endereco'
            if not instance_Insert.insert('endereco', **data):
                success = False

        for contato_model in self.contatos_data:
            data = contato_model.model_dump()
            data['fk_id_user'] = fk_id_user
            # Assumindo que a tabela é 'contato'
            if not instance_Insert.insert('contato', **data):
                success = False
                
        for email_model in self.emails_data:
            data = email_model.model_dump()
            data['fk_id_user'] = fk_id_user
            # Assumindo que a tabela é 'email'
            if not instance_Insert.insert('email', **data):
                success = False

        return success
    


    def criar_novo_usuario(self):
        match self.tipo_logica:
            case "adm_supremo":
                self.instance_Insert = InsertValues()
                
                #INSERIR O USUÁRIO
                user_id = self.instance_Insert.insert(self.tabelaUser, **self.usuario_data)
                
                if not user_id:
                    print("Falha ao criar o usuário.")
                    return None
                
                #INSERIR OS DETALHES
                if not self._inserir_detalhes(user_id):
                    print(f"Atenção: Usuário criado (ID: {user_id}), mas houve falha na inserção dos detalhes.")
                    # Rollback da transação principal aqui
                    return user_id 

                print(f"Usuário e detalhes criados com sucesso. User ID: {user_id}")
                return user_id
            

            case "aluno":
                return
            # case "professor":
            # case "adm":
            # case "recepcionista":



    
        

data = {
    # Campos da tabela 'usuario'
    'name_user':'Carlos', 
    'foto_user':'', 
    'nasc_user':'2025-09-09', 
    'tipo_doc_user':'cnpj', 
    'num_doc_user':'00005171111', 
    'lv_acesso':'colaborador',

    # Campos das tabelas de detalhes (deve ser uma lista)
    "enderecos": [
        {
            "tipo_endereco": "RESIDENCIAL",
            "endereco": "Rua Principal, 55",
            "cep": "01234-567"
        }
    ],
    "contatos": [
        {
            "tipo_contato": "COMERCIAL",
            "numero_contato": "11999998888"
        }
    ],
    "emails": [
        {
            "tipo_email": "PESSOAL",
            "endereco_email": "jhon.teste@empresa.com"
        }
    ]
}
UserNovo = UserModel("adm_supremo", **data)
UserADm = UserNovo.criar_novo_usuario()



# # userNovo agora é uma instância validada de UserModel
# print(UserNovo.name_user)
# print(UserNovo.foto_user)
# print(UserNovo.tipo_logica) # Novo atributo extra


#testando validação:



