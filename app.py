from flask import Flask, request, render_template, redirect, session, url_for, jsonify, flash
import pymysql
import datetime

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

def get_coordenadores():
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute('SELECT nome, email FROM coordenadores')
    coordenadores = cursor.fetchall()
    cursor.close()
    return coordenadores

def get_responsaveis():
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute('SELECT nome, email FROM responsavel_ti')
    responsaveis = cursor.fetchall()
    cursor.close()
    return responsaveis

def get_professores():
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute('SELECT nome, email FROM professores')
    professores = cursor.fetchall()
    cursor.close()
    return professores

@app.route('/obter_laboratorios', methods=['GET'])
def obter_laboratorios():
    cursor = conn.cursor()
    cursor.execute('SELECT nome FROM laboratorios')
    laboratorios = [row[0] for row in cursor.fetchall()]
    cursor.close()
    return jsonify(laboratorios=laboratorios)

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
        laboratorios = get_laboratorios()
        return render_template('cadastrar_laboratorio.html', laboratorios=laboratorios)
    else:
        return redirect('/')

# Rota para o cadastro dos coordenadores (página protegida)
@app.route('/cadastrar_coordenador_form')
def cadastrar_coordenador_form():
    if 'usuario' in session:
        coordenadores = get_coordenadores()
        return render_template('/cadastrar_coordenador.html', coordenadores = coordenadores)
    else:
        return redirect('/')

# Rota para o cadastro dos responsaveis (página protegida)
@app.route('/cadastrar_responsavel_form')
def cadastrar_responsavel_form():
    if 'usuario' in session:
        responsaveis = get_responsaveis()
        return render_template('/cadastrar_responsavel.html', responsaveis = responsaveis)
    else:
        return redirect('/')
    
# Rota para o cadastro dos professores (página protegida)
@app.route('/cadastrar_professor_form')
def cadastrar_professor_form():
    if 'usuario' in session:
        professores = get_professores()
        return render_template('/cadastrar_professor.html', professores = professores)
    else:
        return redirect('/')
    
@app.route('/alocar_laboratorio_form', methods=['GET'])
def alocar_laboratorio_form():
    if 'professor' in session:
        cursor = conn.cursor()
        cursor.execute('SELECT nome FROM disciplinas')
        disciplinas = [row[0] for row in cursor.fetchall()]
        cursor.close()
        return render_template('alocar_laboratorio.html')
    else:
        return redirect('/')

@app.route('/aprovar_alocacao_form', methods=['GET', 'POST'])
def aprovar_alocacao_form():
    if 'usuario' in session:
        return render_template('/aprovar_alocacao.html')
    else:
        return redirect('/')
    
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

@app.route('/editar_laboratorio/<nome_laboratorio>', methods=['POST'])
def editar_laboratorio(nome_laboratorio):
    # Obtenha os dados do formulário enviado pelo frontend
    edit_nome_laboratorio = request.form['edit_nome_laboratorio']
    edit_quantidade_computadores = request.form['edit_quantidade_computadores']
    edit_hardwares = request.form.getlist('edit_hardwares')

    # Realize a operação de edição no banco de dados usando o nome do laboratório
    cursor = conn.cursor()
    edit_hardwares_str = ','.join(edit_hardwares)
    cursor.execute("UPDATE laboratorios SET nome = %s, quantidade_computadores = %s, hardware_computador = %s WHERE nome = %s",
                    (edit_nome_laboratorio, edit_quantidade_computadores, edit_hardwares_str, nome_laboratorio))
    conn.commit()
    cursor.close()

    # Redirecione para a página de cadastro com a lista atualizada
    return redirect(url_for('cadastrar_laboratorio_form', success='updated'))

@app.route('/remover_laboratorio/<nome_laboratorio>', methods=['POST'])
def remover_laboratorio(nome_laboratorio):
    if 'usuario' in session:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM laboratorios WHERE nome = %s", (nome_laboratorio,))
        conn.commit()
        cursor.close()

        # Após remover o laboratório, redirecione para a página de cadastro com a lista atualizada
        return redirect(url_for('cadastrar_laboratorio_form', success='deleted'))
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
            cursor.execute('INSERT INTO professores (nome, email, senha) VALUES (%s, %s, %s)',
                           (nome_professor, email_professor, senha_professor))
            conn.commit()
            cursor.close()
            return redirect(url_for('cadastrar_professor_form', success='true'))
    else:
        return redirect('/')

@app.route('/visualizar_alocacoes_pendentes_form')
def visualizar_alocacoes_pendentes_form():
    if 'usuario' in session:
        solicitacoes = get_solicitacoes()
        return render_template('visualizar_alocacoes_pendentes.html', solicitacoes = solicitacoes)
    else:
        return redirect('/')

def get_solicitacoes():
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute('SELECT * FROM solicitacoes_alocacao')
    solicitacoes = cursor.fetchall()
    cursor.close()
    return solicitacoes

@app.route('/visualizar_alocacoes_pendentes')
def visualizar_alocacoes_pendentes():
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM solicitacoes_alocacao")
    solicitacoes = cursor.fetchall()
    cursor.close()
    return redirect(url_for('visualizar_alocacoes_pendentes_form'))

@app.route('/realizar_alocacao', methods=['GET', 'POST'])
def realizar_alocacao():
    if 'professor' in session:
        if request.method == 'POST':
            laboratorio_selecionado = request.form['laboratorio_selecionado']
            disciplina = request.form['disciplina_selecionada']
            data_selecionada = request.form['data']
            hora_selecionada = request.form['hora']
            
            # Verificar se o laboratório já foi solicitado para a data e hora especificadas
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM solicitacoes_aceitas WHERE laboratorio = %s AND data = %s AND hora = %s", 
                           (laboratorio_selecionado, data_selecionada, hora_selecionada))
            existe_solicitacao = cursor.fetchone()
            cursor.close()
            
            if existe_solicitacao:
                # Se existir uma solicitação aceita para o laboratório na mesma data e hora, retornar uma mensagem de erro
                return redirect(url_for('alocar_laboratorio_form', success='alocado'))
            else:
                # Se o laboratório ainda não foi solicitado para a data e hora especificadas, inserir a nova solicitação
                cursor = conn.cursor()
                cursor.execute("INSERT INTO solicitacoes_alocacao (laboratorio, disciplina, data, hora, estado) VALUES (%s, %s, %s, %s, 'pendente')", 
                               (laboratorio_selecionado, disciplina, data_selecionada, hora_selecionada))
                conn.commit()
                cursor.close()
                return redirect(url_for('alocar_laboratorio_form', success='true'))
        else:
            return render_template('alocar_laboratorio.html')
    else:
        return redirect('/')

@app.route('/aceitar_solicitacao', methods=['POST'])
def aceitar_solicitacao():
    if request.method == 'POST':
        solicitacao_id = request.form['solicitacao_id']
        cursor = conn.cursor()
        # Selecionar os dados da solicitação aceita
        cursor.execute("SELECT * FROM solicitacoes_alocacao WHERE id = %s", (solicitacao_id,))
        solicitacao = cursor.fetchone()
        if solicitacao:
            # Inserir os dados da solicitação aceita na tabela de solicitações aceitas
            cursor.execute("INSERT INTO solicitacoes_aceitas (laboratorio, disciplina, data, hora, estado) VALUES (%s, %s, %s, %s, %s)",
               (solicitacao[1], solicitacao[5], solicitacao[2], solicitacao[3], 'aceito'))
            conn.commit()
            # Excluir a solicitação da tabela original
            cursor.execute("DELETE FROM solicitacoes_alocacao WHERE id = %s", (solicitacao_id,))
            conn.commit()
            cursor.close()
            return redirect(url_for('visualizar_alocacoes_pendentes_form', success='accept')) 
        else:
            cursor.close()
            # Se a solicitação não for encontrada, redirecione para algum lugar apropriado ou retorne uma mensagem de erro
            return redirect(url_for('visualizar_alocacoes_pendentes_form', error='Solicitação não encontrada'))

@app.route('/rejeitar_solicitacao', methods=['POST'])
def rejeitar_solicitacao():
    if request.method == 'POST':
        solicitacao_id = request.form['solicitacao_id']
        cursor = conn.cursor()
        # Selecionar os dados da solicitação recusada
        cursor.execute("SELECT * FROM solicitacoes_alocacao WHERE id = %s", (solicitacao_id,))
        solicitacao = cursor.fetchone()
        if solicitacao:
            # Inserir os dados da solicitação recusada na tabela de solicitações recusadas
            cursor.execute("INSERT INTO solicitacoes_recusadas (laboratorio, disciplina, data, hora, estado) VALUES (%s, %s, %s, %s, %s)",
                           (solicitacao[1], solicitacao[5], solicitacao[2], solicitacao[3], 'recusado'))
            conn.commit()
            # Excluir a solicitação da tabela original
            cursor.execute("DELETE FROM solicitacoes_alocacao WHERE id = %s", (solicitacao_id,))
            conn.commit()
            cursor.close()
            return redirect(url_for('visualizar_alocacoes_pendentes_form', success='recused')) 
        else:
            cursor.close()
            # Se a solicitação não for encontrada, redirecione para algum lugar apropriado ou retorne uma mensagem de erro
            return redirect(url_for('visualizar_alocacoes_pendentes_form', error='Solicitação não encontrada'))

# Rota para cadastrar uma disciplina
@app.route('/cadastrar_disciplina_form')
def cadastrar_disciplina_form():
    if 'coordenador' in session:
        cursor = conn.cursor()
        cursor.execute('SELECT nome FROM disciplinas')
        disciplinas = [row[0] for row in cursor.fetchall()]
        cursor.close()
        return render_template('cadastrar_disciplina.html', disciplinas=disciplinas)
    else:
        return redirect('/')
    
@app.route('/get_disciplinas', methods=['GET'])
def get_disciplinas():
    cursor = conn.cursor()
    cursor.execute('SELECT nome FROM disciplinas')
    disciplinas = [row[0] for row in cursor.fetchall()]
    cursor.close()
    return jsonify(disciplinas=disciplinas)

@app.route('/get_professores', methods=['GET'])
def obter_professores():
    cursor = conn.cursor()
    cursor.execute('SELECT nome FROM professores')
    professores = [row[0] for row in cursor.fetchall()]
    cursor.close()
    return jsonify(professores=professores)

@app.route('/cadastrar_aplicacao_form')
def cadastrar_aplicacao_form():
    if 'responsavel' in session:
        cursor = conn.cursor()
        cursor.execute('SELECT nome FROM laboratorios')
        laboratorios = [row[0] for row in cursor.fetchall()]
        cursor.close()
        return render_template('cadastrar_aplicacao.html', laboratorios=laboratorios)
    else:
        return redirect('/')


@app.route('/get_requisitos', methods=['GET'])
def get_requisitos():
    disciplina_selecionada = request.form['disciplina_selecionada']
    cursor = conn.cursor()
    cursor.execute('SELECT requisito FROM requisitos_disciplina WHERE nome_materia = %s', (disciplina_selecionada,))
    requisitos = [row[0] for row in cursor.fetchall()]
    cursor.close()
    return jsonify(requisitos=requisitos)

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
        professor = request.form['professor_materia']
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
            cursor.execute('INSERT INTO disciplinas (nome, quantidade_alunos, duracao, professor, horario_inicio, horario_fim) VALUES (%s, %s, %s, %s, %s, %s)',
                           (nome_disciplina, quantidade_alunos, duracao, professor, horario_inicio, horario_fim))
            conn.commit()
            cursor.close()
            return redirect(url_for('cadastrar_disciplina_form', success='true'))
    else:
        return redirect('/')
    
@app.route('/cadastrar_requisitos', methods=['POST'])
def cadastrar_requisitos():
    if 'coordenador' in session:
        nome_disciplina = request.form['disciplina_selecionada']
        nome_requisito = request.form['nome_requisito'] 
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM disciplinas WHERE nome = %s", (nome_disciplina,))
        disciplina_id = cursor.fetchone()
        if disciplina_id:
            cursor.execute("INSERT INTO requisitos_disciplina (nome_materia, requisito) VALUES (%s, %s)",
                           (nome_disciplina, nome_requisito))
            conn.commit()
            cursor.close()
            return redirect(url_for('cadastrar_requisitos_form', success='true'))
        else:
            cursor.close()
            return render_template('cadastrar_requisitos.html')
    else:
        return redirect('/')

@app.route('/cadastrar_aplicacao', methods=['POST'])
def cadastrar_aplicacao():
    if 'responsavel' in session:
        nome_laboratorio = request.form['laboratorio_selecionado']
        nome_aplicacao = request.form['nome_aplicacao']
        
        # Verificar se a aplicação já está cadastrada para o laboratório selecionado
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM aplicacoes_laboratorios WHERE nome_aplicacao = %s AND laboratorio_id = (SELECT id FROM laboratorios WHERE nome = %s)', (nome_aplicacao, nome_laboratorio))
        aplicacao_existente = cursor.fetchone()
        cursor.close()
        
        if aplicacao_existente:
            flash('Esta aplicação já está cadastrada para o laboratório selecionado.')
            return redirect(url_for('cadastrar_aplicacao_form'))
        
        # Se a aplicação não existir, continue com o cadastro
        else:
            versao_aplicacao = request.form['versao']
            cursor = conn.cursor()
            cursor.execute('SELECT id FROM laboratorios WHERE nome = %s', (nome_laboratorio,))
            laboratorio_id = cursor.fetchone()[0]
            cursor.execute('INSERT INTO aplicacoes_laboratorios (nome_aplicacao, versao, laboratorio_id) VALUES (%s, %s, %s)',
                           (nome_aplicacao, versao_aplicacao, laboratorio_id))
            conn.commit()
            cursor.close()
            return redirect(url_for('cadastrar_aplicacao_form', success='true'))

    else:
        return redirect('/')

# Rota para fazer logout
@app.route('/logout')
def logout():
    session.pop('usuario', None)
    session.pop('coordenador', None)
    session.pop('responsavel', None)
    session.pop('professor', None)
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
    
