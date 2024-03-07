from flask import Flask, request, render_template, redirect, session, url_for
import pymysql

app = Flask(__name__)
app.secret_key = 'teste123'

db_host = 'localhost'
db_user = 'root'
db_password = ''
db_name = 'locacaolab'

conn = pymysql.connect(host=db_host, user=db_user, password=db_password, database=db_name)

class Coordenador:
    def __init__(self, id, email, senha):
        self.id = id
        self.email = email
        self.senha = senha

# Rota para exibir o formulário de login
@app.route('/', methods=['GET', 'POST'])
def realizar_login():
    if request.method == 'POST':
        usuario = request.form.get('usuario')
        senha = request.form['senha']

        # Verificação do login do administrador
        if usuario == 'admin' and senha == '12345':
            session['usuario'] = usuario
            return redirect('/dashboard_diretor')
        # Verificação do login do coordenador
        else: 
            email = request.form.get('usuario')
            senha = request.form['senha']

            if not email:
                return render_template('login.html', error_message='Acesso negado, email não fornecido.')

            print("Dados do formulário: ", email, senha)

            cursor = conn.cursor(pymysql.cursors.DictCursor)
            cursor.execute('SELECT * FROM coordenadores WHERE email = %s AND senha = %s', (email, senha))
            coordenador = cursor.fetchone()
            cursor.close()

            if coordenador:
                session['coordenador'] = coordenador['email']
                return redirect('/dashboard_coordenador')
            else: 
                print("Nenhum coordenador encontrado com essas credenciais.")
                return render_template('login.html', error_message='Acesso negado, email ou senha incorretos.')
    else:
        return render_template('login.html')

# Rota para o dashboard (página protegida)
@app.route('/dashboard_diretor')
def dashboard():
    if 'usuario' in session:
        return render_template('/dashboard_diretor.html')
    else:
        return redirect('/')

@app.route('/dashboard_coordenador')
def dashboard_coordenador():
    if 'coordenador' in session:
        return render_template('/dashboard_coordenador.html')
    else:
        return redirect('/')

# Rota para o cadastro dos laboratorios (página protegida)
@app.route('/cadastrar_laboratorio_form')
def cadastrar_laboratorio_form():
    if 'usuario' in session:
        return render_template('/cadastrar_laboratorio.html')
    else:
        return redirect('/')

# Rota para o cadastro dos coordenadores (página protegida)
@app.route('/cadastrar_coordenador_form')
def cadastrar_coordenador_form():
    if 'usuario' in session:
        return render_template('/cadastrar_coordenador.html')
    else:
        return redirect('/')

# Rota para o cadastro dos responsaveis (página protegida)
@app.route('/cadastrar_responsavel_form')
def cadastrar_responsavel_form():
    if 'usuario' in session:
        return render_template('/cadastrar_responsavel.html')
    else:
        return redirect('/')
            
# Rota para cadastrar um laboratório
@app.route('/cadastrar_laboratorio', methods=['POST'])
def cadastrar_laboratorio():
    if 'usuario' in session:
        nome_laboratorio = request.form['nome_laboratorio']
        quantidade_computadores = request.form['quantidade_computadores']
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM laboratorios WHERE nome = %s', (nome_laboratorio))
        laboratorio_existente = cursor.fetchone()
        cursor.close()
        if laboratorio_existente:
            return render_template('cadastrar_laboratorio.html', laboratorio_existente = True)
        else:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO Laboratorios (nome, quantidade_computadores) VALUES (%s, %s)", 
                            (nome_laboratorio, quantidade_computadores))
            conn.commit()
            cursor.close()
            return redirect(url_for('cadastrar_laboratorio_form', success='true')) 
    else:
        return redirect('/')

# Rota para cadastrar um coordenador
@app.route('/cadastrar_coordenador', methods=['POST'])
def cadastrar_coordenador():
    if 'usuario' in session:
        nome_coordenador = request.form['nome_coordenador']
        email_coordenador = request.form['email_coordenador']
        senha_coordenador = request.form['senha_coordenador']
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM coordenadores WHERE email = %s', (email_coordenador))
        coordenador_existente = cursor.fetchone()
        cursor.close()
        if coordenador_existente:
            return render_template('cadastrar_coordenador.html', coordenador_existente = True)
        else:
            cursor = conn.cursor()
            cursor.execute('INSERT INTO coordenadores (nome, email, senha) VALUES (%s,%s,%s)', 
                            (nome_coordenador, email_coordenador, senha_coordenador))
            conn.commit()
            cursor.close()
            return redirect(url_for('cadastrar_coordenador_form', success='true'))
    else:
        return redirect('/')

# Rota para cadastrar um responsavel
@app.route('/cadastrar_responsavel', methods=['POST'])
def cadastrar_responsavel():
    if 'usuario' in session:
        nome_responsavel = request.form['nome_responsavel']
        email_responsavel = request.form['email_responsavel']
        senha_responsavel = request.form['senha_responsavel']
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM responsavel_ti WHERE email = %s', (email_responsavel))
        responsavel_existente = cursor.fetchone()
        cursor.close()
        if responsavel_existente:
            return render_template('cadastrar_responsavel.html', email_existente = True)
        else:
            cursor = conn.cursor()
            cursor.execute('INSERT INTO responsavel_ti (responsavel, email, senha) VALUES (%s, %s, %s)',
                           (nome_responsavel, email_responsavel, senha_responsavel))
            conn.commit()
            cursor.close()
            return redirect(url_for('cadastrar_responsavel_form', success='true'))
    else:
        return redirect('/')

# Rota para fazer logout
@app.route('/logout')
def logout():
    session.pop('usuario', None)
    session.pop('coordenador', None)
    return redirect('/')

if __name__ == '__main__':
        app.run(debug=True)
