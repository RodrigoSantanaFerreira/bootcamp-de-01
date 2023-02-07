# Bootcamp de Engenharia de Dados.

### Para rodar a aplicação de ingestão faça:

1. Provisione o RDS PostgreSQL na AWS conforme abordado em aula.
2. Crie um banco de dados, por exemplo: coins
3. Configure o arquivo model.py com o nome da tabela a ser criada, exemplo: tb_coins.
4. Edite variável `db_string` com o endpoint do RDS na AWS.
5. Altere o arquivo app.py inserindo a chave da api como argumento da função get_data (key)
6. Execute a aplicação para consumo da API e persistência no banco de dados.
