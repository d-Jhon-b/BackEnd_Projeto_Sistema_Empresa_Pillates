#  Repositório do backEnd - Empresa Pilates


#  Sobre a contruçãp
    #  Sobre o ambiente virtual(venv)
    #  Sobre a biblioteca alembic (parte de migration)
        # instalação:
            #  pip install alembic  
        # Uso:
            
        # Comandos: 
            # Criar uma nova etapa: 
                -Inciar projeto com alembic para as migration
                alembic init alembic  
                    *Alterar seus dados de conexão no arquivo: alembic.ini. Procure o valor "sqlalchemy.url" e altere para seu banco de dados


                -(Optional) EM nosso caso, alteramos o arquivo env.py. A razão dessa alteração é dado por conta de uma lógica próprio do nosso projeto
                que busca os dados de arquivos .env
                local: src/database/envCOnfig/ (arquivo para a configuração do env, seja mongo ou sql)

                -Criar nova migration
                #  alembic revision -m "create tabela usuarios"

                Isso criara um novo arquivo para determinar uma nova migração
                Ao terminar de editar as funções upgrade e downgrade no novo arquivo criado você pode aplicar ele.
                -Aplicação:
                    para aplicar upgrade: alembic upgrade head (caso)
                    para aplicar um downgrade: alembic downgrade head
                    para verificar o status do upgrade ou downgrade: alembic history
                    para mostrar a revisão do conteúdo: alembic current 
