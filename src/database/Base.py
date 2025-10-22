from sqlalchemy.orm import declarative_base


class DeclarativeBase():
    """Classe declarada para manter o metodo declrative_base. 
    Método declarative_base determina e verifica a contrução da tabela, no padrão ORM 
    e valida suas caracteristica para uso e aplicação no sistema.
    Ela sempre busca o valor __tablename__ para valdiar sua presença no banco:
    exemplo de uso:
    """
    Base = declarative_base()

#Exemplo de uso:

"""
#importação de bibliotecas:
from sqlalchemy import Column, String, Integer, CheckConstraint, UniqueConstraint, Date, Enum, func, ForeignKey
from src.database.Base import DeclarativeBase as Base #ou apenas DeclarativeBase


Instancia o objeto Base que contem o método
class Pessoa(Base.Base): 
    
    #Definição obrigatória da tabela no banco de dados (ATENÇÃO ao nome singular).
    __tablesname__ = 'Pessoa'

    #Definir colunas:
    # Recomenda-se ser o mais detalhado possível, espelhando a Migration. Mesmo que se não for igual,
    # minha honesta recomendação e aplicar ao máximo as caracteristicas presentes em seu modelo de migration para o banco
    id_user = Column(Integer, nullable=False, primary_key=True)
    name = Colunm(String(255), nullable=False)
    lv_acesso = Column(Enum('supremo', 'colaborador', 'instrutor', 'aluno', name='lv_acesso_enum'), nullable=False)
    idade=Colum(Integer, nullable=False)
    
    #Definição de Constraints (Opcional, mas útil para validação ORM)
    #diferente das colunas, precisamos aplicar todas as Constraints em uma variavel 
    #denominada "__table_args__" ela vai manter todas as constraints presentes para a
    #"verficação" de existencia.
    __table_args__=(

    CheckConstraint('idade_minima >=18', name='chk_idade_minima'),
)
"""
