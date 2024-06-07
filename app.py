from flask import Flask, request, render_template, redirect, session, url_for, jsonify, flash
import pymysql
from datetime import timedelta
from flask_bcrypt import Bcrypt

app = Flask(__name__)
bcrypt = Bcrypt(app)
app.secret_key = 'teste123'

db_host = 'localhost'
db_user = 'root'
db_password = ''
db_name = 'locacao_lab'

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

@app.route('/', methods=['GET', 'POST'])
def realizar_login():
    if request.method == 'POST':
        usuario = request.form.get('usuario')
        senha = request.form['senha']

        if not usuario or not senha:
            return render_template('login.html', error_message='Acesso negado, email ou senha não fornecidos.')

        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute('SELECT * FROM coordenadores WHERE email = %s', (usuario,))
        coordenador = cursor.fetchone()
        cursor.close()

        if coordenador and bcrypt.check_password_hash(coordenador['senha'], senha):
            session['coordenador'] = coordenador['email']
            return redirect('/dashboard_coordenador')

        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute('SELECT * FROM responsavel_ti WHERE email = %s', (usuario,))
        responsavel = cursor.fetchone()
        cursor.close()

        if responsavel and bcrypt.check_password_hash(responsavel['senha'], senha):
            session['responsavel'] = responsavel['email']
            return redirect('/dashboard_responsavel')

        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute('SELECT * FROM professores WHERE email = %s', (usuario,))
        professor = cursor.fetchone()
        cursor.close()

        if professor and bcrypt.check_password_hash(professor['senha'], senha):
            session['professor'] = professor['email']
            return redirect('/dashboard_professor')

        if usuario == 'admin' and bcrypt.check_password_hash(bcrypt.generate_password_hash('12345').decode('utf-8'), senha):
            session['usuario'] = usuario
            return redirect('/dashboard_diretor')

        return render_template('login.html', error_message='Acesso negado, email ou senha incorretos.')
    else:
        return render_template('login.html')

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
    
@app.route('/cadastrar_laboratorio_form')
def cadastrar_laboratorio_form():
    if 'usuario' in session:
        laboratorios = get_laboratorios()
        return render_template('cadastrar_laboratorio.html', laboratorios=laboratorios)
    else:
        return redirect('/')

@app.route('/cadastrar_coordenador_form')
def cadastrar_coordenador_form():
    if 'usuario' in session:
        coordenadores = get_coordenadores()
        return render_template('/cadastrar_coordenador.html', coordenadores = coordenadores)
    else:
        return redirect('/')

@app.route('/cadastrar_responsavel_form')
def cadastrar_responsavel_form():
    if 'usuario' in session:
        responsaveis = get_responsaveis()
        return render_template('/cadastrar_responsavel.html', responsaveis = responsaveis)
    else:
        return redirect('/')

@app.route('/cadastrar_professor_form')
def cadastrar_professor_form():
    if 'usuario' in session:
        professores = get_professores()
        return render_template('/cadastrar_professor.html', professores = professores)
    else:
        return redirect('/')
    
@app.route('/alocar_laboratorio_form')
def alocar_laboratorio_form():
    cursor = conn.cursor()
    cursor.execute("SELECT nome FROM laboratorios")
    laboratorios = [row[0] for row in cursor.fetchall()]
    cursor.execute("SELECT nome FROM disciplinas")
    disciplinas = [row[0] for row in cursor.fetchall()]
    cursor.close()
    return render_template('alocar_laboratorio.html', laboratorios=laboratorios, disciplinas=disciplinas)

@app.route('/aprovar_alocacao_form', methods=['GET', 'POST'])
def aprovar_alocacao_form():
    if 'usuario' in session:
        return render_template('/aprovar_alocacao.html')
    else:
        return redirect('/')
    
@app.route('/cadastrar_laboratorio', methods=['POST'])
def cadastrar_laboratorio():
    if 'usuario' in session:
        nome_laboratorio = request.form['nome_laboratorio']
        quantidade_computadores = request.form['quantidade_computadores']
        if int(quantidade_computadores) <= 0:
            return redirect(url_for('cadastrar_laboratorio_form', success='invalid'))
        cpu = request.form.getlist('cpus')
        ram = request.form.getlist('rams')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM laboratorios WHERE nome = %s', (nome_laboratorio,))
        laboratorio_existente = cursor.fetchone()
        cursor.close()
        if laboratorio_existente:
            return render_template('cadastrar_laboratorio.html', laboratorio_existente=True)
        else:
            cursor = conn.cursor()
            cpus_str = ','.join(cpu)
            rams_str = ','.join(ram)
            hardwares_str = f"CPU: {cpus_str} | RAM: {rams_str}"
            cursor.execute("INSERT INTO laboratorios (nome, quantidade_computadores, hardware_computador) VALUES (%s, %s, %s)", 
                            (nome_laboratorio, quantidade_computadores, hardwares_str))
            conn.commit()
            cursor.close()
            return redirect(url_for('cadastrar_laboratorio_form', success='true'))
    else:
        return redirect('/')

@app.route('/editar_laboratorio/<nome_laboratorio>', methods=['POST'])
def editar_laboratorio(nome_laboratorio):
    if 'usuario' in session:
        try:
            edit_nome_laboratorio = request.form['edit_nome_laboratorio']
            edit_quantidade_computadores = request.form['edit_quantidade_computadores']
            edit_cpu = request.form['edit_cpu']
            edit_rams = request.form.getlist('edit_rams')
        except KeyError as e:
            return redirect(url_for('cadastrar_laboratorio_form', success='invalid'))
        if int(edit_quantidade_computadores) <= 0:
            return redirect(url_for('cadastrar_laboratorio_form', success='invalid'))
        rams_str = ', '.join(edit_rams)
        hardwares_str = f"CPU: {edit_cpu} | RAMs: {rams_str}"
        cursor = conn.cursor()
        cursor.execute("UPDATE laboratorios SET nome = %s, quantidade_computadores = %s, hardware_computador = %s WHERE nome = %s",
                        (edit_nome_laboratorio, edit_quantidade_computadores, hardwares_str, nome_laboratorio))
        conn.commit()
        cursor.close()
        return redirect(url_for('cadastrar_laboratorio_form', success='updated'))
    else:
        return redirect('/')

@app.route('/remover_laboratorio/<nome_laboratorio>', methods=['POST'])
def remover_laboratorio(nome_laboratorio):
    if 'usuario' in session:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM laboratorios WHERE nome = %s", (nome_laboratorio,))
        laboratorio = cursor.fetchone()
        if laboratorio:
            laboratorio_id = laboratorio[0]
            cursor.execute("DELETE FROM aplicacoes_laboratorios WHERE laboratorio_id = %s", (laboratorio_id,))
            cursor.execute("DELETE FROM laboratorios WHERE id = %s", (laboratorio_id,))
            conn.commit()
            cursor.close()
        return redirect(url_for('cadastrar_laboratorio_form', success='deleted'))
    else:
        return redirect('/')

@app.route('/cadastrar_coordenador', methods=['POST'])
def cadastrar_coordenador():
    if 'usuario' in session:
        nome_coordenador = request.form['nome_coordenador']
        email_coordenador = request.form['email_coordenador']
        senha_coordenador = request.form['senha_coordenador']
        senha_hash = bcrypt.generate_password_hash(senha_coordenador).decode('utf-8')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM coordenadores WHERE email = %s', (email_coordenador,))
        coordenador_existente = cursor.fetchone()
        cursor.close()
        if coordenador_existente:
            return render_template('cadastrar_coordenador.html', coordenador_existente=True)
        else:
            cursor = conn.cursor()
            cursor.execute('INSERT INTO coordenadores (nome, email, senha) VALUES (%s,%s,%s)', 
                            (nome_coordenador, email_coordenador, senha_hash))
            conn.commit()
            cursor.close()
            return redirect(url_for('cadastrar_coordenador_form', success='true'))
    else:
        return redirect('/')
    
@app.route('/remover_coordenador/<nome_coordenador>', methods=['POST'])
def remover_coordenador(nome_coordenador):
    if 'usuario' in session:
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT id FROM coordenadores WHERE nome = %s", (nome_coordenador,))
            coordenador = cursor.fetchone()
            if coordenador:
                coordenador_id = coordenador[0]
                cursor.execute("DELETE FROM coordenadores WHERE id = %s", (coordenador_id,))
                conn.commit()
            return redirect(url_for('cadastrar_coordenador_form', success='deleted'))
        except Exception as e:
            print(f"Erro ao remover coordenador: {e}")
            return redirect(url_for('cadastrar_coordenador_form', success='error'))
        finally:
            cursor.close()
    else:
        return redirect('/')

@app.route('/cadastrar_responsavel', methods=['POST'])
def cadastrar_responsavel():
    if 'usuario' in session:
        nome_responsavel = request.form['nome_responsavel']
        email_responsavel = request.form['email_responsavel']
        senha_responsavel = request.form['senha_responsavel']
        senha_hash = bcrypt.generate_password_hash(senha_responsavel).decode('utf-8')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM responsavel_ti WHERE email = %s', (email_responsavel))
        responsavel_existente = cursor.fetchone()
        cursor.close()
        if responsavel_existente:
            return render_template('cadastrar_responsavel.html', email_existente = True)
        else:
            cursor = conn.cursor()
            cursor.execute('INSERT INTO responsavel_ti (nome, email, senha) VALUES (%s, %s, %s)',
                           (nome_responsavel, email_responsavel, senha_hash))
            conn.commit()
            cursor.close()
            return redirect(url_for('cadastrar_responsavel_form', success='true'))
    else:
        return redirect('/')
    
@app.route('/remover_responsavel/<nome_responsavel>', methods=['POST'])
def remover_responsavel(nome_responsavel):
    if 'usuario' in session:
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT id FROM responsavel_ti WHERE nome = %s", (nome_responsavel,))
            responsavel = cursor.fetchone()
            if responsavel:
                responsavel_id = responsavel[0]
                cursor.execute("DELETE FROM responsavel_ti WHERE id = %s", (responsavel_id,))
                conn.commit()
            return redirect(url_for('cadastrar_responsavel_form', success='deleted'))
        except Exception as e:
            print(f"Erro ao remover responsavel: {e}")
            return redirect(url_for('cadastrar_responsavel_form', success='error'))
        finally:
            cursor.close()
    else:
        return redirect('/')

@app.route('/cadastrar_professor', methods=['POST'])
def cadastrar_professor():
    if 'usuario' in session:
        nome_professor = request.form['nome_professor']
        email_professor = request.form['email_professor']
        senha_professor = request.form['senha_professor']
        senha_hash = bcrypt.generate_password_hash(senha_professor).decode('utf-8')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM professores WHERE email = %s', (email_professor,))
        professor_existente = cursor.fetchone()
        cursor.close()
        if professor_existente:
            return render_template('cadastrar_professor.html', email_existente=True)
        else:
            cursor = conn.cursor()
            cursor.execute('INSERT INTO professores (nome, email, senha) VALUES (%s, %s, %s)',
                           (nome_professor, email_professor, senha_hash))
            conn.commit()
            cursor.close()
            return redirect(url_for('cadastrar_professor_form', success='true'))
    else:
        return redirect('/')
    
@app.route('/remover_professor/<nome_professor>', methods=['POST'])
def remover_professor(nome_professor):
    if 'usuario' in session:
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT id FROM professores WHERE nome = %s", (nome_professor,))
            professor = cursor.fetchone()
            if professor:
                professor_id = professor[0]
                cursor.execute("DELETE FROM professores WHERE id = %s", (professor_id,))
                conn.commit()
            return redirect(url_for('cadastrar_professor_form', success='deleted'))
        except Exception as e:
            print(f"Erro ao remover professor: {e}")
            return redirect(url_for('cadastrar_professor_form', success='error'))
        finally:
            cursor.close()
    else:
        return redirect('/')

@app.route('/visualizar_alocacoes_pendentes_form')
def visualizar_alocacoes_pendentes_form():
    if 'usuario' in session:
        solicitacoes = get_solicitacoes()
        return render_template('visualizar_alocacoes_pendentes.html', solicitacoes = solicitacoes)
    else:
        return redirect('/')
    
@app.route('/visualizar_alocacoes_aceitas_form')
def visualizar_alocacoes_aceitas_form():
    if 'usuario' or 'professor' in session:
        solicitacoes_aceitas = get_solicitacoes_aceitas()
        return render_template('visualizar_alocacoes_aceitas.html', solicitacoes_aceitas = solicitacoes_aceitas)
    
@app.route('/visualizar_alocacoes_aceitas', methods=['GET'])
def visualizar_alocacoes_aceitas():
    if 'usuario' in session:
        filtro = request.args.get('filtro', '')
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        if filtro:
            query = """
                SELECT * FROM solicitacoes_aceitas 
                WHERE laboratorio LIKE %s 
                OR disciplina LIKE %s 
                OR DATE_FORMAT(data, '%%d-%%m-%%Y') LIKE %s 
                OR hora LIKE %s
            """
            like_filter = '%' + filtro + '%'
            cursor.execute(query, (like_filter, like_filter, like_filter, like_filter))
        else:
            cursor.execute("SELECT * FROM solicitacoes_aceitas")
        solicitacoes_aceitas = cursor.fetchall()
        cursor.close()
        return render_template('visualizar_alocacoes_aceitas.html', solicitacoes_aceitas=solicitacoes_aceitas)
    else:
        return redirect('/')

def get_solicitacoes_aceitas():
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute('SELECT * FROM solicitacoes_aceitas')
    solicitacoes_aceitas = cursor.fetchall()
    cursor.close()
    return solicitacoes_aceitas
                   
def get_solicitacoes():
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute('SELECT * FROM solicitacoes_alocacao')
    solicitacoes = cursor.fetchall()
    cursor.close()
    return solicitacoes

@app.route('/visualizar_alocacoes_pendentes', methods=['GET'])
def visualizar_alocacoes_pendentes():
    if 'usuario' in session:
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute("SELECT * FROM solicitacoes_alocacao")
        solicitacoes = cursor.fetchall()
        cursor.close()
        return render_template('visualizar_alocacoes_pendentes.html', solicitacoes=solicitacoes)
    else:
        return redirect('/')

import datetime
from datetime import timedelta

@app.route('/realizar_alocacao', methods=['GET', 'POST'])
def realizar_alocacao():
    if 'professor' in session:
        if request.method == 'POST':
            laboratorio_selecionado = request.form['laboratorio_selecionado']
            disciplina = request.form['disciplina_selecionada']
            data_selecionada = request.form['data']
            hora_selecionada = request.form['hora']
            saida = request.form['saida']
            marcar_proximas_aulas = request.form.get('marcar_proximas_aulas', 'false') == 'true'
            cursor = conn.cursor()

            def inserir_solicitacao(data):
                cursor.execute("SELECT * FROM solicitacoes_aceitas WHERE laboratorio = %s AND data = %s AND hora = %s AND saida = %s", 
                               (laboratorio_selecionado, data, hora_selecionada, saida))
                existe_solicitacao = cursor.fetchone()
                if existe_solicitacao:
                    return False
                cursor.execute("INSERT INTO solicitacoes_alocacao (laboratorio, disciplina, data, hora, estado, saida) VALUES (%s, %s, %s, %s, %s, %s)", 
                               (laboratorio_selecionado, disciplina, data, hora_selecionada, 'Pendente', saida))
                return True

            datas_a_solicitar = [data_selecionada]
            if marcar_proximas_aulas:
                data_base = datetime.datetime.strptime(data_selecionada, "%Y-%m-%d")
                for i in range(1, 4):
                    proxima_data = data_base + timedelta(days=i * 7)
                    datas_a_solicitar.append(proxima_data.strftime("%Y-%m-%d"))

            for data in datas_a_solicitar:
                if not inserir_solicitacao(data):
                    cursor.close()
                    return redirect(url_for('alocar_laboratorio_form', success='alocado'))

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
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute("SELECT * FROM solicitacoes_alocacao WHERE id = %s", (solicitacao_id,))
        solicitacao = cursor.fetchone()
        if solicitacao:
            cursor.execute("INSERT INTO solicitacoes_aceitas (laboratorio, disciplina, data, hora, estado, saida) VALUES (%s, %s, %s, %s, %s, %s)",
               (solicitacao['laboratorio'], solicitacao['disciplina'], solicitacao['data'], solicitacao['hora'], 'Aceito', solicitacao['saida']))
            conn.commit()
            cursor.execute("DELETE FROM solicitacoes_alocacao WHERE id = %s", (solicitacao_id,))
            conn.commit()
            cursor.close()
            return redirect(url_for('visualizar_alocacoes_pendentes', success='accept')) 
        else:
            cursor.close()
            return redirect(url_for('visualizar_alocacoes_pendentes', error='Solicitação não encontrada'))

@app.route('/rejeitar_solicitacao', methods=['POST'])
def rejeitar_solicitacao():
    if request.method == 'POST':
        solicitacao_id = request.form['solicitacao_id']
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM solicitacoes_alocacao WHERE id = %s", (solicitacao_id,))
        solicitacao = cursor.fetchone()
        if solicitacao:
            cursor.execute("INSERT INTO solicitacoes_recusadas (laboratorio, disciplina, data, hora, estado) VALUES (%s, %s, %s, %s, %s)",
                           (solicitacao[1], solicitacao[5], solicitacao[2], solicitacao[3], 'Recusado'))
            conn.commit()
            cursor.execute("DELETE FROM solicitacoes_alocacao WHERE id = %s", (solicitacao_id,))
            conn.commit()
            cursor.close()
            return redirect(url_for('visualizar_alocacoes_pendentes_form', success='recused')) 
        else:
            cursor.close()
            return redirect(url_for('visualizar_alocacoes_pendentes_form', error='Solicitação não encontrada'))

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
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM aplicacoes_laboratorios WHERE nome_aplicacao = %s AND laboratorio_id = (SELECT id FROM laboratorios WHERE nome = %s)', (nome_aplicacao, nome_laboratorio))
        aplicacao_existente = cursor.fetchone()
        cursor.close()
        if aplicacao_existente:
            flash('Esta aplicação já está cadastrada para o laboratório selecionado.')
            return redirect(url_for('cadastrar_aplicacao_form'))
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

@app.route('/logout')
def logout():
    session.pop('usuario', None)
    session.pop('coordenador', None)
    session.pop('responsavel', None)
    session.pop('professor', None)
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
    