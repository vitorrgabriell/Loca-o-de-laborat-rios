from flask import Flask, request, render_template, redirect, session, url_for, jsonify, flash
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

class Responsavel:
    def __init__(self, id, email, senha):
        self.id = id
        self.email = email
        self.senha = senha

class Professor:
    def __init__(self,id, email, senha):
        self.id = id
        self.email = email
        self.senha = senha

def get_laboratorios():
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute('SELECT nome, quantidade_computadores, hardware_computador FROM laboratorios')
    laboratorios = cursor.fetchall()
    cursor.close()
    return laboratorios

# Rota para exibir o formulário de login
@app.route('/', methods=['GET', 'POST'])
def realizar_login():
    if request.method == 'POST':
        usuario = request.form.get('usuario')
        senha = request.form['senha']

        if not usuario or not senha:
            return render_template('login.html', error_message='Acesso negado, email ou senha não fornecidos.')

        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute('SELECT * FROM coordenadores WHERE email = %s AND senha = %s', (usuario, senha))
        coordenador = cursor.fetchone()
        cursor.close()

        if coordenador:
            session['coordenador'] = coordenador['email']
            return redirect('/dashboard_coordenador')

        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute('SELECT * FROM responsavel_ti WHERE email = %s AND senha = %s', (usuario, senha))
        responsavel = cursor.fetchone()
        cursor.close()

        if responsavel:
            session['responsavel'] = responsavel['email']
            return redirect('/dashboard_responsavel')

        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute('SELECT * FROM professores WHERE email = %s AND senha = %s', (usuario, senha))
        professor = cursor.fetchone()
        cursor.close()

        if professor:
            session['professor'] = professor['email']
            return redirect('/dashboard_professor')

        if usuario == 'admin' and senha == '12345':
            session['usuario'] = usuario
            return redirect('/dashboard_diretor')

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

@app.route('/dashboard_responsavel')
def dashboard_responsavel():
    if 'responsavel' in session:
        return render_template('/dashboard_responsavel.html')
    else:
        return redirect('/')

@app.route('/dashboard_professor')
def dashboard_professor():
    if 'professor' in session:
        return render_template('dashboard_professor.html')
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
    
# Rota para o cadastro dos professores (página protegida)
@app.route('/cadastrar_professor_form')
def cadastrar_professor_form():
    if 'usuario' in session:
        return render_template('/cadastrar_professor.html')
    else:
        return redirect('/')
    
@app.route('/realizar_alocacao', methods=['GET', 'POST'])
def realizar_alocacao_form():
    return render_template('alocar_laboratorio.html')

            
# Rota para cadastrar um laboratório
@app.route('/cadastrar_laboratorio', methods=['POST'])
def cadastrar_laboratorio():
    if 'usuario' in session:
        nome_laboratorio = request.form['nome_laboratorio']
        quantidade_computadores = request.form['quantidade_computadores']
        hardwares = request.form.getlist('hardwares')

        cursor = conn.cursor()
        cursor.execute('SELECT * FROM laboratorios WHERE nome = %s', (nome_laboratorio,))
        laboratorio_existente = cursor.fetchone()
        cursor.close()

        if laboratorio_existente:
            return render_template('cadastrar_laboratorio.html', laboratorio_existente=True)
        else:
            cursor = conn.cursor()
            hardwares_str = ','.join(hardwares)
            cursor.execute("INSERT INTO laboratorios (nome, quantidade_computadores, hardware_computador) VALUES (%s, %s, %s)", 
                            (nome_laboratorio, quantidade_computadores, hardwares_str))
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
        cursor.execute('SELECT * FROM coordenadores WHERE email = %s', (email_coordenador,))
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
            cursor.execute('INSERT INTO responsavel_ti (nome, email, senha) VALUES (%s, %s, %s)',
                           (nome_responsavel, email_responsavel, senha_responsavel))
            conn.commit()
            cursor.close()
            return redirect(url_for('cadastrar_responsavel_form', success='true'))
    else:
        return redirect('/')
    
# Rota para cadastrar um professor
@app.route('/cadastrar_professor', methods=['POST'])
def cadastrar_professor():
    if 'usuario' in session:
        nome_professor = request.form['nome_professor']
        materia_professor = request.form['materia_professor']
        email_professor = request.form['email_professor']
        senha_professor = request.form['senha_professor']
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM professores WHERE email = %s', (email_professor,))
        professor_existente = cursor.fetchone()
        cursor.close()
        if professor_existente:
            return render_template('cadastrar_professor.html', email_existente=True)
        else:
            cursor = conn.cursor()
            cursor.execute('INSERT INTO professores (nome, materia, email, senha) VALUES (%s, %s, %s, %s)',
                           (nome_professor, materia_professor, email_professor, senha_professor))
            conn.commit()
            cursor.close()
            return redirect(url_for('cadastrar_professor_form', success='true'))
    else:
        return redirect('/')

@app.route('/visualizar_laboratorios')
def visualizar_laboratorios():
    if 'usuario' in session:
        laboratorios = get_laboratorios()
        return render_template('visualizar_laboratorios.html', laboratorios=laboratorios)
    else:
        return redirect('/')

@app.route('/visualizar_alocacoes_pendentes')
def visualizar_alocacoes_pendentes():
    if 'usuario' in session:
        return render_template('aprovar_alocacao.html')
    else:
        return redirect('/')


# Rota para cadastrar uma disciplina
@app.route('/cadastrar_disciplina_form')
def cadastrar_disciplina_form():
    if 'coordenador' in session:
        return render_template('cadastrar_disciplina.html')
    else:
        return redirect('/')

@app.route('/cadastrar_aplicacao_form')
def cadastrar_aplicacao_form():
    if 'responsavel' in session:
        return render_template('cadastrar_aplicacao.html')
    else:
        return redirect('/')

@app.route('/cadastrar_requisitos_form')
def cadastrar_requisitos_form():
    if 'coordenador' in session:
        return render_template('cadastrar_requisitos.html')
    else:
        return redirect('/')

@app.route('/cadastrar_disciplina', methods=['POST'])
def cadastrar_disciplina():
    if 'coordenador' in session:
        nome_disciplina = request.form['nome_disciplina']
        quantidade_alunos = request.form['quantidade_alunos']
        duracao = request.form['duracao']
        horario_inicio = request.form['horario_inicio']
        horario_fim = request.form['horario_fim']
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM disciplinas WHERE nome = %s', (nome_disciplina,))
        disciplina_existente = cursor.fetchone()
        cursor.close()
        if disciplina_existente:
            return render_template('cadastrar_disciplina.html', disciplina_existente=True)
        else:
            cursor = conn.cursor()
            cursor.execute('INSERT INTO disciplinas (nome, quantidade_alunos, duracao, horario_inicio, horario_fim) VALUES (%s, %s, %s, %s, %s)',
                           (nome_disciplina, quantidade_alunos, duracao, horario_inicio, horario_fim))
            conn.commit()
            cursor.close()
            return redirect(url_for('cadastrar_disciplina_form', success='true'))
    else:
        return redirect('/')

@app.route('/cadastrar_aplicacao', methods=['POST'])
def cadastrar_aplicacao():
    if 'responsavel' in session:
        nome_laboratorio = request.form['nome_laboratorio']
        nome_aplicacao = request.form['nome_aplicacao']
        versao = request.form['versao']
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM laboratorios WHERE nome = %s", (nome_laboratorio,))
        laboratorio = cursor.fetchone()
        if laboratorio:
            laboratorio_id = laboratorio[0]
            cursor.execute("INSERT INTO aplicacoes_laboratorios (nome_aplicacao, versao, laboratorio_id) VALUES (%s, %s, %s)",
                            (nome_aplicacao, versao, laboratorio_id))
            conn.commit()
            cursor.close()
            return redirect(url_for('cadastrar_aplicacao_form', success='true'))
        else:
            flash("Erro ao cadastrar aplicação: Laboratório não registrado.")
            return redirect(url_for('cadastrar_aplicacao_form'))
    else:
        return redirect('/')

@app.route('/cadastrar_requisitos', methods=['POST'])
def cadastrar_requisitos():
    if 'coordenador' in session:
        nome_disciplina = request.form['nome_disciplina']
        nome_aplicacao = request.form['nome_aplicacao']
        nome_laboratorio = request.form['nome_laboratorio'] 
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM disciplinas WHERE nome = %s", (nome_disciplina,))
        disciplina_id = cursor.fetchone()
        cursor.execute("SELECT id FROM aplicacoes_laboratorios WHERE nome_aplicacao = %s", (nome_aplicacao,))
        aplicacao_id = cursor.fetchone()
        cursor.execute("SELECT id FROM laboratorios WHERE nome = %s", (nome_laboratorio,))
        laboratorio_id = cursor.fetchone()

        if disciplina_id and aplicacao_id and laboratorio_id:
            cursor.execute("INSERT INTO requisitos_software (disciplina_id, aplicacao_id, laboratorio_id) VALUES (%s, %s, %s)",
                           (disciplina_id, aplicacao_id, laboratorio_id))
            conn.commit()
            conn.close()
            return redirect(url_for('cadastrar_requisitos_form', success='true'))
        else:
            conn.close()
            return "Erro: Disciplina, aplicação ou laboratório não encontrados no banco de dados."
    else:
        return redirect('/')

# Rota para fazer logout
@app.route('/logout')
def logout():
    session.pop('usuario', None)
    session.pop('coordenador', None)
    session.pop('responsavel', None)
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
    
