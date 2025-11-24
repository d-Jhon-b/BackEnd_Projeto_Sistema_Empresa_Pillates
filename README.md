Repositório Backend - Sistema de Gestão de Pilates
Sobre o Projeto
Este repositório contém o código-fonte do backend


Configuração e Primeiros Passos
1. Ambiente Virtual (venv)
Recomendamos o uso de um ambiente virtual para isolar as dependências do projeto.
`python -m venv venv	Cria o ambiente virtual.`

Ativa o ambiente em sistemas Unix/macOS. 🚀
`source venv/bin/activate`  

Ativa o ambiente no Windows (CMD/PowerShell). 🚀
`venv\Scripts\activate`	

para desativar:
`deactivate`

2. Instalação de Dependências
Com o ambiente ativado, instale as bibliotecas necessárias:

Bash
`pip install -r requirements.txt` 🚀



3. Configuração do Banco de Dados (.env)
O projeto utiliza um arquivo de ambiente (.env) para gerenciar as credenciais do banco de dados (PostgreSQL).

Crie um arquivo chamado .env na raiz do projeto.

Defina a URL de conexão do SQLAlchemy:
DATABASE_URL="postgresql+psycopg2://USUARIO:SENHA@HOST:PORTA/NOMEDOBANCO"
# Exemplo: postgresql+psycopg2://user:password@localhost:5432/pilatesdb

(A localização exata da configuração é: src/database/envConfig/envPostGre.py)


Migrações com Alembic
O Alembic é utilizado para gerenciar as migrações (mudanças estruturais) do banco de dados de forma segura.

Instalação
A instalação já deve estar inclusa no requirements.txt, mas se precisar:
`pip install alembic` 

Inicialização (Feita Apenas uma Vez)
Para iniciar o projeto Alembic no repositório:
`alembic init alembic` 🚀
Nota: Se você está configurando o projeto pela primeira vez, verifique se a URL de conexão em alembic.ini está correta, ou se o arquivo alembic/env.py está configurado para buscar a variável de ambiente .env (como é o caso neste projeto).

Criação de Novas Migrações 🚀
Sempre que houver mudanças nos modelos ORM (tabelas e colunas):
`alembic revision -m "descrição_clara_da_mudanca"` 
# Exemplo: alembic revision -m "Adicionar coluna de histórico médico ao Estudante"
Este comando criará um novo arquivo Python para você editar as funções upgrade() e downgrade().


Aplicação das Migrações
`alembic upgrade head`:	Aplica todas as migrações pendentes até a mais recente. (Uso Comum)
`alembic downgrade -1`:	Desfaz a última migração aplicada.
`alembic current`:	Mostra a revisão atual aplicada no banco de dados.
`alembic history`:	Exibe o histórico de todas as migrações.


4. Inicializar projeto 🚀
Dentro do ambiente virtual aplicado no passo 1, aplicamos o comnado:
`uvicorn main:app --reload`


Tecnologias Utilizadas
Python: Linguagem de programação principal.
FastAPI: Framework de alto desempenho para a construção da API.
SQLAlchemy: ORM (Object-Relational Mapper) para interação com o banco de dados.
PostgreSQL (NEON): Banco de dados relacional.
Alembic: Ferramenta de migração de banco de dados.
Pydantic: Para validação e serialização de dados (Schemas).


5. Instalações de bibliotecas offline para desenvolvimento
# Comando para instalação:
5.1. Verifique que a pasta packages está em seu diretorio:
    -Nesta pasta se encontram as bibliotecas usadas no projeto, com versões compativeis para aplicação
    -Verifique que o arquivo `instacoes_offline.txt` está em seu diretório principal
-Em seu Diretório principal rode o comando:
`pip install --no-index --find-links=packages -r instacoes_offline.txt` ->

