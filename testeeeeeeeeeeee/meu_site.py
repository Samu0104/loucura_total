# Importação das bibliotecas necessárias
from flask import Flask, render_template, request, redirect 
import sqlite3

# Criação da aplicação Flask
app = Flask(__name__)

# Função para obter a conexão com o banco de dados SQLite
def get_db_connection():
    # Conecta ao banco de dados SQLite chamado 'BancoDeDados.db'
    conn = sqlite3.connect('BancoDeDados.db')
    # Define que as linhas retornadas sejam acessadas como dicionários
    conn.row_factory = sqlite3.Row
    return conn

# Função para criar as tabelas 'conta' e 'compra' no banco de dados, caso não existam
def create_table():
    # Obtém a conexão com o banco de dados
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Criação da tabela 'conta' se não existir, para armazenar informações dos usuários
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS conta (
            id INTEGER PRIMARY KEY AUTOINCREMENT,  
            nome_sobrenome TEXT NOT NULL,          
            data_nasc TEXT NOT NULL,              
            email TEXT NOT NULL UNIQUE,           
            senha TEXT NOT NULL                   
        )
    ''')
    
    # Criação da tabela 'compra' para armazenar as compras realizadas pelos usuários
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS compra (
            id INTEGER PRIMARY KEY AUTOINCREMENT,  
            nome TEXT NOT NULL,                   
            email TEXT NOT NULL,                   
            nTelefone TEXT NOT NULL,              
            cep TEXT NOT NULL,                     
            nCasa TEXT NOT NULL,                   
            idproduto INTEGER NOT NULL,            
            qtd INTEGER NOT NULL,                  
            FOREIGN KEY (idproduto) REFERENCES Produto(id)  
        )
    ''')
    
    # Comita as alterações no banco de dados
    conn.commit()
    # Fecha a conexão com o banco de dados
    conn.close()

# Rota para a página inicial (home)
@app.route('/')
def homepage():
    return render_template("index.html")  # Renderiza o template 'index.html'

# Rota para a página de produtos femininos
@app.route('/feminino')
def feminino():
    return render_template("feminino.html")  # Renderiza o template 'feminino.html'

# Rota para a página de produtos masculinos
@app.route('/masculino')
def masculino():
    return render_template("masculino.html")  # Renderiza o template 'masculino.html'

# Rota para a página de produtos infantis
@app.route('/infantil')
def infantil():
    return render_template("infantil.html")  # Renderiza o template 'infantil.html'

# Rota para a página de produtos plus size
@app.route('/plus-size')
def plusSize():
    return render_template("plus-size.html")  # Renderiza o template 'plus-size.html'

# Rota para a página de compras (GET e POST)
@app.route('/comprar', methods=['GET', 'POST'])
def comprar():
    if request.method == 'POST':
        # Coleta os dados do formulário de compra via POST
        nome = request.form['name']
        email = request.form['email']
        nTelefone = request.form['telefone']
        cep = request.form['cep']
        nCasa = request.form['nCasa']
        idproduto = request.form['idproduto']
        qtd = request.form['quantidade']
        
        # Verifica se todos os campos foram preenchidos
        if not nome or not email or not nTelefone or not cep or not nCasa or not idproduto or not qtd:
            return "Erro: Todos os campos são obrigatórios."
        
        # Tenta converter os valores de idproduto e qtd para inteiros
        try:
            idproduto = int(idproduto)
            qtd = int(qtd)
        except ValueError:
            return "Erro: Produto e quantidade devem ser valores numéricos."
        
        # Obtém a conexão com o banco de dados
        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            # Verifica se o usuário existe no banco de dados
            cursor.execute('''
                SELECT * FROM conta WHERE nome_sobrenome = ? AND email = ?
            ''', (nome, email))
            usuario = cursor.fetchone()  # Retorna o primeiro resultado da consulta
            
            if not usuario:
                return "Erro: Usuário não encontrado."
            
            # Verifica se o produto existe no banco de dados
            cursor.execute('''
                SELECT * FROM Produto WHERE id = ?
            ''', (idproduto,))
            produto = cursor.fetchone()  # Retorna o primeiro resultado da consulta
            
            if not produto:
                return "Erro: Produto não encontrado."
            
            # Insere a compra no banco de dados
            cursor.execute('''
                INSERT INTO compra (nome, email, nTelefone, cep, nCasa, idproduto, qtd)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (nome, email, nTelefone, cep, nCasa, idproduto, qtd))
            conn.commit()  # Comita a transação
            return "Compra realizada com sucesso!"
        
        except sqlite3.IntegrityError as e:
            return f"Erro ao realizar a compra: {str(e)}"
        
        finally:
            conn.close()  # Fecha a conexão com o banco de dados

    return render_template('comprar.html')  # Renderiza o template 'comprar.html'

# Rota para a página de confirmação de compra
@app.route('/confirmacao')
def confirmacao():
    return render_template("confirmacao.html")  # Renderiza o template 'confirmacao.html'

@app.route('/pesquisar', methods=['GET'])
def pesquisar():
    search_term = request.args.get('search_term', '').strip()  # Obtém o termo de pesquisa
    
    if not search_term:
        return redirect('/')  # Se o termo estiver vazio, redireciona para a página inicial


    try:
        # Consulta SQL para buscar produtos com o nome que contenha o termo de pesquisa
        cursor.execute('''
            SELECT * FROM Produto WHERE nome LIKE ?
        ''', ('%' + search_term + '%',))  # '%' são usados para buscar qualquer coisa antes ou depois do termo
        
        # Obtém os resultados da pesquisa
        produtos_encontrados = cursor.fetchall()

        # Exibe os resultados da pesquisa no template
        return render_template('pesquisa.html', search_term=search_term, produtos=produtos_encontrados)

    except sqlite3.Error as e:
        return f"Erro ao realizar a pesquisa: {str(e)}"


# Rota para a página de cadastro de novos usuários (GET e POST)
@app.route('/cadastrar', methods=['GET', 'POST'])
def cadastrar():
    if request.method == 'POST':
        # Coleta os dados do formulário de cadastro
        nome_sobrenome = request.form['name']
        data_nasc = request.form['dob']
        email = request.form['email']
        senha = request.form['password']
        
        # Verifica se todos os campos foram preenchidos
        if not nome_sobrenome or not data_nasc or not email or not senha:
            return "Erro: Todos os campos são obrigatórios."
        
        # Imprime os dados recebidos no console (apenas para depuração)
        print(f"Dados recebidos: {nome_sobrenome}, {data_nasc}, {email}, {senha}")

        # Obtém a conexão com o banco de dados
        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            # Insere o novo usuário na tabela 'conta'
            cursor.execute('''
                INSERT INTO conta (nome_sobrenome, data_nasc, email, senha) 
                VALUES (?, ?, ?, ?)
            ''', (nome_sobrenome, data_nasc, email, senha))
            conn.commit()  # Comita a transação
            return "Usuário cadastrado com sucesso!"
        
        except sqlite3.IntegrityError:
            return "Erro: Este usuário ou email já está cadastrado."
        
        finally:
            conn.close()  # Fecha a conexão com o banco de dados

    return render_template('cadastrar.html')  # Renderiza o template 'cadastrar.html'

# Rota para a página de login (GET e POST)
@app.route('/entrar', methods=['GET', 'POST'])
def entrar():
    if request.method == 'POST':
        # Coleta os dados do formulário de login
        email = request.form['email']
        senha = request.form['password']
        
        # Verifica se todos os campos foram preenchidos
        if not email or not senha:
            return "Erro: Todos os campos são obrigatórios."
        
        # Imprime os dados recebidos no console (apenas para depuração)
        print(f"Dados recebidos: {email}, {senha}")

        # Obtém a conexão com o banco de dados
        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            # Verifica se o usuário existe com o e-mail e senha informados
            cursor.execute('''
                SELECT * FROM conta WHERE email = ? AND senha = ?
            ''', (email, senha))
            usuario = cursor.fetchone()  # Retorna o primeiro resultado da consulta
            
            if usuario:
                return "Usuário encontrado com sucesso!"
            else:
                return "Erro: Usuário ou senha inválidos."
        
        except sqlite3.Error as e:
            return f"Erro no banco de dados: {str(e)}"
        
        finally:
            conn.close()  # Fecha a conexão com o banco de dados

    return render_template("entrar.html")  # Renderiza o template 'entrar.html'

# Rota para a página de deletar um usuário (GET e POST)
@app.route('/deletar', methods=['GET', 'POST'])
def deletar():
    if request.method == 'POST':
        # Coleta os dados do formulário de exclusão
        email = request.form['email']
        senha = request.form['password']
        
        # Verifica se todos os campos foram preenchidos
        if not email or not senha:
            return "Erro: Todos os campos são obrigatórios."
        
        # Imprime os dados recebidos no console (apenas para depuração)
        print(f"Dados recebidos: {email}, {senha}")

        # Obtém a conexão com o banco de dados
        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            # Verifica se o usuário existe com o e-mail e senha informados
            cursor.execute('''
                SELECT * FROM conta WHERE email = ? AND senha = ?
            ''', (email, senha))
            usuario = cursor.fetchone()  # Retorna o primeiro resultado da consulta
            
            if usuario:
                # Deleta o usuário da tabela 'conta'
                cursor.execute('''
                    DELETE FROM conta WHERE email = ? AND senha = ?
                ''', (email, senha))
                conn.commit()  # Comita a transação
                return "Usuário deletado com sucesso!"
            else:
                return "Erro: Usuário ou senha inválidos."
        
        except sqlite3.Error as e:
            return f"Erro no banco de dados: {str(e)}"
        
        finally:
            conn.close()  # Fecha a conexão com o banco de dados

    return render_template("deletar.html")  # Renderiza o template 'deletar.html'

# Se este script for executado diretamente, cria as tabelas e inicia o servidor Flask
if __name__ == "__main__":
    create_table()  # Chama a função para criar as tabelas no banco de dados
    app.run(debug=True)  # Inicia o servidor Flask em modo de depuração
