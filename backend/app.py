from flask import Flask, request, jsonify
from flask_cors import CORS
from functools import wraps
import secrets
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timedelta
import hashlib
import time
import os

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)
CORS(app, supports_credentials=True, origins=['*'])

# ========== BANCO DE DADOS COM MANEJO DE LOCK ==========

class Database:
    def __init__(self, db_name='evolveglobal.db'):
        self.db_name = db_name
        self.init_db()
    
    @contextmanager
    def get_connection(self):
        """Obtém uma conexão com timeout e retry automático"""
        max_retries = 5
        retry_delay = 0.1
        
        for attempt in range(max_retries):
            try:
                # Timeout de 20 segundos para esperar o lock
                conn = sqlite3.connect(self.db_name, timeout=20.0)
                conn.row_factory = sqlite3.Row
                # Configurações para melhor concorrência
                conn.execute('PRAGMA journal_mode=WAL')
                conn.execute('PRAGMA synchronous=NORMAL')
                conn.execute('PRAGMA cache_size=10000')
                yield conn
                conn.commit()
                break
            except sqlite3.OperationalError as e:
                if "database is locked" in str(e) and attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    retry_delay *= 2
                    continue
                raise e
            finally:
                if 'conn' in locals():
                    conn.close()
    
    def init_db(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Tabela de usuários
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS usuarios (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    senha_hash TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Tabela de tokens
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS tokens (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    token TEXT UNIQUE NOT NULL,
                    user_id INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP,
                    revoked BOOLEAN DEFAULT 0,
                    FOREIGN KEY (user_id) REFERENCES usuarios (id) ON DELETE CASCADE
                )
            ''')
            
            # Tabela de projetos
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS projetos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    nome TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES usuarios (id) ON DELETE CASCADE,
                    UNIQUE(user_id, nome)
                )
            ''')
            
            # Tabela de pastas
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS pastas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    projeto_id INTEGER NOT NULL,
                    user_id INTEGER NOT NULL,
                    nome TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (projeto_id) REFERENCES projetos (id) ON DELETE CASCADE,
                    FOREIGN KEY (user_id) REFERENCES usuarios (id) ON DELETE CASCADE,
                    UNIQUE(projeto_id, user_id, nome)
                )
            ''')
            
            # Tabela de arquivos
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS arquivos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    projeto_id INTEGER NOT NULL,
                    user_id INTEGER NOT NULL,
                    caminho TEXT NOT NULL,
                    conteudo TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (projeto_id) REFERENCES projetos (id) ON DELETE CASCADE,
                    FOREIGN KEY (user_id) REFERENCES usuarios (id) ON DELETE CASCADE,
                    UNIQUE(projeto_id, user_id, caminho)
                )
            ''')
            
            # Tabelas de estudos
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS tarefas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    text TEXT NOT NULL,
                    subject TEXT NOT NULL,
                    completed BOOLEAN DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES usuarios (id) ON DELETE CASCADE
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS metas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    text TEXT NOT NULL,
                    completed BOOLEAN DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES usuarios (id) ON DELETE CASCADE
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS materiais (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    link TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES usuarios (id) ON DELETE CASCADE
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS anotacoes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER UNIQUE NOT NULL,
                    content TEXT,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES usuarios (id) ON DELETE CASCADE
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS stats_estudos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER UNIQUE NOT NULL,
                    study_minutes_today INTEGER DEFAULT 0,
                    pomodoro_sessions INTEGER DEFAULT 0,
                    last_update DATE,
                    FOREIGN KEY (user_id) REFERENCES usuarios (id) ON DELETE CASCADE
                )
            ''')
            
            # Índices
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_email ON usuarios(email)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_token ON tokens(token)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_projetos_user ON projetos(user_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_arquivos_projeto ON arquivos(projeto_id)')
            
            print("✅ Banco de dados inicializado com sucesso!")
    
    # ========== OPERAÇÕES DE USUÁRIO ==========
    
    def create_user(self, nome, email, senha_hash):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO usuarios (nome, email, senha_hash) VALUES (?, ?, ?)',
                (nome, email, senha_hash)
            )
            return cursor.lastrowid
    
    def get_user_by_email(self, email):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM usuarios WHERE email = ?', (email,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def get_user_by_id(self, user_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM usuarios WHERE id = ?', (user_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def save_token(self, token, user_id, expires_at=None):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO tokens (token, user_id, expires_at) VALUES (?, ?, ?)',
                (token, user_id, expires_at)
            )
            return cursor.lastrowid
    
    def get_token(self, token):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM tokens WHERE token = ? AND revoked = 0', (token,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def revoke_token(self, token):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('UPDATE tokens SET revoked = 1 WHERE token = ?', (token,))
    
    # ========== OPERAÇÕES DE PROJETOS ==========
    
    def get_projetos(self, user_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT id, nome, created_at, updated_at FROM projetos WHERE user_id = ? ORDER BY updated_at DESC', (user_id,))
            return [dict(row) for row in cursor.fetchall()]
    
    def create_projeto(self, user_id, nome):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('INSERT INTO projetos (user_id, nome) VALUES (?, ?)', (user_id, nome))
            return cursor.lastrowid
    
    def update_projeto(self, projeto_id, user_id, novo_nome):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('UPDATE projetos SET nome = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ? AND user_id = ?', (novo_nome, projeto_id, user_id))
    
    def delete_projeto(self, projeto_id, user_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM projetos WHERE id = ? AND user_id = ?', (projeto_id, user_id))
    
    # ========== OPERAÇÕES DE ARQUIVOS ==========
    
    def get_arquivos(self, projeto_id, user_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT caminho, conteudo FROM arquivos WHERE projeto_id = ? AND user_id = ?', (projeto_id, user_id))
            return [dict(row) for row in cursor.fetchall()]
    
    def get_arquivo(self, projeto_id, user_id, caminho):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT conteudo FROM arquivos WHERE projeto_id = ? AND user_id = ? AND caminho = ?', (projeto_id, user_id, caminho))
            row = cursor.fetchone()
            return row['conteudo'] if row else None
    
    def save_arquivo(self, projeto_id, user_id, caminho, conteudo):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO arquivos (projeto_id, user_id, caminho, conteudo) 
                VALUES (?, ?, ?, ?)
                ON CONFLICT(projeto_id, user_id, caminho) 
                DO UPDATE SET conteudo = ?, updated_at = CURRENT_TIMESTAMP
            ''', (projeto_id, user_id, caminho, conteudo, conteudo))
    
    def delete_arquivo(self, projeto_id, user_id, caminho):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM arquivos WHERE projeto_id = ? AND user_id = ? AND caminho = ?', (projeto_id, user_id, caminho))
    
    # ========== OPERAÇÕES DE PASTAS ==========
    
    def get_pastas(self, projeto_id, user_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT nome FROM pastas WHERE projeto_id = ? AND user_id = ?', (projeto_id, user_id))
            return [dict(row) for row in cursor.fetchall()]
    
    def create_pasta(self, projeto_id, user_id, nome):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('INSERT INTO pastas (projeto_id, user_id, nome) VALUES (?, ?, ?)', (projeto_id, user_id, nome))
    
    def delete_pasta(self, projeto_id, user_id, nome):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM pastas WHERE projeto_id = ? AND user_id = ? AND nome = ?', (projeto_id, user_id, nome))
    
    # ========== OPERAÇÕES DE ESTUDOS ==========
    
    def get_tarefas(self, user_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM tarefas WHERE user_id = ? ORDER BY created_at DESC', (user_id,))
            return [dict(row) for row in cursor.fetchall()]
    
    def create_tarefa(self, user_id, text, subject, completed=False):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('INSERT INTO tarefas (user_id, text, subject, completed) VALUES (?, ?, ?, ?)', (user_id, text, subject, completed))
            return cursor.lastrowid
    
    def update_tarefa(self, tarefa_id, completed):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('UPDATE tarefas SET completed = ? WHERE id = ?', (completed, tarefa_id))
    
    def delete_tarefa(self, tarefa_id, user_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM tarefas WHERE id = ? AND user_id = ?', (tarefa_id, user_id))
    
    def get_metas(self, user_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM metas WHERE user_id = ? ORDER BY created_at DESC', (user_id,))
            return [dict(row) for row in cursor.fetchall()]
    
    def create_meta(self, user_id, text, completed=False):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('INSERT INTO metas (user_id, text, completed) VALUES (?, ?, ?)', (user_id, text, completed))
            return cursor.lastrowid
    
    def update_meta(self, meta_id, completed):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('UPDATE metas SET completed = ? WHERE id = ?', (completed, meta_id))
    
    def delete_meta(self, meta_id, user_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM metas WHERE id = ? AND user_id = ?', (meta_id, user_id))
    
    def get_materiais(self, user_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM materiais WHERE user_id = ? ORDER BY created_at DESC', (user_id,))
            return [dict(row) for row in cursor.fetchall()]
    
    def create_material(self, user_id, name, link):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('INSERT INTO materiais (user_id, name, link) VALUES (?, ?, ?)', (user_id, name, link))
            return cursor.lastrowid
    
    def delete_material(self, material_id, user_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM materiais WHERE id = ? AND user_id = ?', (material_id, user_id))
    
    def get_anotacoes(self, user_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT content FROM anotacoes WHERE user_id = ?', (user_id,))
            row = cursor.fetchone()
            return row['content'] if row else None
    
    def save_anotacoes(self, user_id, content):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO anotacoes (user_id, content) VALUES (?, ?)
                ON CONFLICT(user_id) DO UPDATE SET content = ?, updated_at = CURRENT_TIMESTAMP
            ''', (user_id, content, content))
    
    def get_stats(self, user_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM stats_estudos WHERE user_id = ?', (user_id,))
            row = cursor.fetchone()
            if row:
                return dict(row)
            return {'study_minutes_today': 0, 'pomodoro_sessions': 0}
    
    def update_stats(self, user_id, stats_data):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO stats_estudos (user_id, study_minutes_today, pomodoro_sessions, last_update)
                VALUES (?, ?, ?, DATE('now'))
                ON CONFLICT(user_id) DO UPDATE SET
                    study_minutes_today = ?,
                    pomodoro_sessions = ?,
                    last_update = DATE('now')
            ''', (user_id, stats_data.get('study_minutes_today', 0), 
                  stats_data.get('pomodoro_sessions', 0),
                  stats_data.get('study_minutes_today', 0),
                  stats_data.get('pomodoro_sessions', 0)))
    
    def reset_dados_estudos(self, user_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM tarefas WHERE user_id = ?', (user_id,))
            cursor.execute('DELETE FROM metas WHERE user_id = ?', (user_id,))
            cursor.execute('DELETE FROM materiais WHERE user_id = ?', (user_id,))
            cursor.execute('DELETE FROM anotacoes WHERE user_id = ?', (user_id,))
            cursor.execute('DELETE FROM stats_estudos WHERE user_id = ?', (user_id,))

# ========== AUTENTICAÇÃO ==========

class AuthManager:
    def __init__(self, db):
        self.db = db
    
    def hash_password(self, password):
        salt = secrets.token_hex(16)
        hash_obj = hashlib.sha256((password + salt).encode())
        return f"{salt}:{hash_obj.hexdigest()}"
    
    def verify_password(self, password, stored_hash):
        try:
            salt, hash_value = stored_hash.split(':')
            hash_obj = hashlib.sha256((password + salt).encode())
            return hash_obj.hexdigest() == hash_value
        except:
            return False
    
    def create_user(self, nome, email, senha):
        senha_hash = self.hash_password(senha)
        return self.db.create_user(nome, email, senha_hash)
    
    def authenticate_user(self, email, senha):
        user = self.db.get_user_by_email(email)
        if user and self.verify_password(senha, user['senha_hash']):
            return {'id': user['id'], 'nome': user['nome'], 'email': user['email']}
        return None
    
    def generate_token(self, user_id):
        token = secrets.token_urlsafe(32)
        expires_at = datetime.now() + timedelta(days=7)
        self.db.save_token(token, user_id, expires_at)
        return token
    
    def verify_token(self, token):
        token_data = self.db.get_token(token)
        if not token_data:
            return False
        if token_data['expires_at']:
            expires_at = datetime.fromisoformat(token_data['expires_at'])
            if datetime.now() > expires_at:
                return False
        return True
    
    def get_user_id_from_token(self, token):
        token_data = self.db.get_token(token)
        return token_data['user_id'] if token_data else None
    
    def revoke_token(self, token):
        self.db.revoke_token(token)

# ========== INSTANCIAR CLASSES ==========

db = Database()
auth = AuthManager(db)

# ========== DECORATOR ==========

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token or not auth.verify_token(token):
            return jsonify({'error': 'Não autorizado'}), 401
        return f(*args, **kwargs)
    return decorated_function

# ========== ROTAS DE AUTENTICAÇÃO ==========

@app.route('/')
def home():
    return jsonify({'message': 'EvolveGlobal API', 'status': 'online'}), 200

@app.route('/api/teste', methods=['GET'])
def teste():
    return jsonify({'message': 'API funcionando!', 'status': 'online', 'versao': '1.0'}), 200

@app.route('/api/cadastro', methods=['POST'])
def cadastro():
    try:
        data = request.json
        nome = data.get('nome', '').strip()
        email = data.get('email', '').strip().lower()
        senha = data.get('senha', '')
        
        if not nome or not email or not senha:
            return jsonify({'error': 'Todos os campos são obrigatórios'}), 400
        
        if len(senha) < 6:
            return jsonify({'error': 'A senha deve ter pelo menos 6 caracteres'}), 400
        
        if db.get_user_by_email(email):
            return jsonify({'error': 'Email já cadastrado'}), 409
        
        user_id = auth.create_user(nome, email, senha)
        
        return jsonify({'success': True, 'message': 'Cadastro realizado com sucesso', 'user_id': user_id}), 201
    except Exception as e:
        print(f"Erro no cadastro: {e}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.json
        email = data.get('email', '').strip().lower()
        senha = data.get('senha', '')
        
        if not email or not senha:
            return jsonify({'error': 'Email e senha são obrigatórios'}), 400
        
        user = auth.authenticate_user(email, senha)
        
        if user:
            token = auth.generate_token(user['id'])
            return jsonify({
                'success': True,
                'message': f'Bem-vindo, {user["nome"]}!',
                'user': {'id': user['id'], 'nome': user['nome'], 'email': user['email']},
                'token': token
            }), 200
        else:
            return jsonify({'error': 'Email ou senha incorretos'}), 401
    except Exception as e:
        print(f"Erro no login: {e}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@app.route('/api/logout', methods=['POST'])
@login_required
def logout():
    token = request.headers.get('Authorization')
    auth.revoke_token(token)
    return jsonify({'success': True, 'message': 'Logout realizado'}), 200

@app.route('/api/verificar-token', methods=['GET'])
@login_required
def verificar_token():
    return jsonify({'valid': True}), 200

# ========== ROTAS DO CODE STUDIO ==========

@app.route('/api/studio/projetos', methods=['GET'])
@login_required
def get_projetos():
    token = request.headers.get('Authorization')
    user_id = auth.get_user_id_from_token(token)
    projetos = db.get_projetos(user_id)
    return jsonify(projetos), 200

@app.route('/api/studio/projetos', methods=['POST'])
@login_required
def create_projeto():
    token = request.headers.get('Authorization')
    user_id = auth.get_user_id_from_token(token)
    data = request.json
    nome = data.get('nome', '').strip()
    
    if not nome:
        return jsonify({'error': 'Nome do projeto é obrigatório'}), 400
    
    projeto_id = db.create_projeto(user_id, nome)
    return jsonify({'id': projeto_id, 'success': True}), 201

@app.route('/api/studio/projetos/<int:projeto_id>', methods=['PUT'])
@login_required
def update_projeto(projeto_id):
    token = request.headers.get('Authorization')
    user_id = auth.get_user_id_from_token(token)
    data = request.json
    novo_nome = data.get('nome', '').strip()
    
    if not novo_nome:
        return jsonify({'error': 'Novo nome é obrigatório'}), 400
    
    db.update_projeto(projeto_id, user_id, novo_nome)
    return jsonify({'success': True}), 200

@app.route('/api/studio/projetos/<int:projeto_id>', methods=['DELETE'])
@login_required
def delete_projeto(projeto_id):
    token = request.headers.get('Authorization')
    user_id = auth.get_user_id_from_token(token)
    db.delete_projeto(projeto_id, user_id)
    return jsonify({'success': True}), 200

@app.route('/api/studio/projetos/<int:projeto_id>/arquivos', methods=['GET'])
@login_required
def get_arquivos(projeto_id):
    token = request.headers.get('Authorization')
    user_id = auth.get_user_id_from_token(token)
    arquivos = db.get_arquivos(projeto_id, user_id)
    return jsonify(arquivos), 200

@app.route('/api/studio/projetos/<int:projeto_id>/arquivos', methods=['POST'])
@login_required
def save_arquivo(projeto_id):
    token = request.headers.get('Authorization')
    user_id = auth.get_user_id_from_token(token)
    data = request.json
    caminho = data.get('caminho', '')
    conteudo = data.get('conteudo', '')
    
    if not caminho:
        return jsonify({'error': 'Caminho do arquivo é obrigatório'}), 400
    
    db.save_arquivo(projeto_id, user_id, caminho, conteudo)
    return jsonify({'success': True}), 200

@app.route('/api/studio/projetos/<int:projeto_id>/arquivos/<path:caminho>', methods=['DELETE'])
@login_required
def delete_arquivo(projeto_id, caminho):
    token = request.headers.get('Authorization')
    user_id = auth.get_user_id_from_token(token)
    db.delete_arquivo(projeto_id, user_id, caminho)
    return jsonify({'success': True}), 200

@app.route('/api/studio/projetos/<int:projeto_id>/pastas', methods=['GET'])
@login_required
def get_pastas(projeto_id):
    token = request.headers.get('Authorization')
    user_id = auth.get_user_id_from_token(token)
    pastas = db.get_pastas(projeto_id, user_id)
    return jsonify(pastas), 200

@app.route('/api/studio/projetos/<int:projeto_id>/pastas', methods=['POST'])
@login_required
def create_pasta(projeto_id):
    token = request.headers.get('Authorization')
    user_id = auth.get_user_id_from_token(token)
    data = request.json
    nome = data.get('nome', '').strip()
    
    if not nome:
        return jsonify({'error': 'Nome da pasta é obrigatório'}), 400
    
    db.create_pasta(projeto_id, user_id, nome)
    return jsonify({'success': True}), 201

@app.route('/api/studio/projetos/<int:projeto_id>/pastas', methods=['DELETE'])
@login_required
def delete_pasta(projeto_id):
    token = request.headers.get('Authorization')
    user_id = auth.get_user_id_from_token(token)
    data = request.json
    nome = data.get('nome', '').strip()
    
    if not nome:
        return jsonify({'error': 'Nome da pasta é obrigatório'}), 400
    
    db.delete_pasta(projeto_id, user_id, nome)
    return jsonify({'success': True}), 200

# ========== ROTAS DE ESTUDOS ==========

@app.route('/api/estudos/tarefas', methods=['GET'])
@login_required
def get_tarefas():
    token = request.headers.get('Authorization')
    user_id = auth.get_user_id_from_token(token)
    tarefas = db.get_tarefas(user_id)
    return jsonify(tarefas), 200

@app.route('/api/estudos/tarefas', methods=['POST'])
@login_required
def create_tarefa():
    token = request.headers.get('Authorization')
    user_id = auth.get_user_id_from_token(token)
    data = request.json
    tarefa_id = db.create_tarefa(user_id, data['text'], data['subject'], data.get('completed', False))
    return jsonify({'id': tarefa_id, 'success': True}), 201

@app.route('/api/estudos/tarefas', methods=['PUT'])
@login_required
def update_tarefa():
    token = request.headers.get('Authorization')
    user_id = auth.get_user_id_from_token(token)
    data = request.json
    db.update_tarefa(data['id'], data.get('completed'))
    return jsonify({'success': True}), 200

@app.route('/api/estudos/tarefas', methods=['DELETE'])
@login_required
def delete_tarefa():
    token = request.headers.get('Authorization')
    user_id = auth.get_user_id_from_token(token)
    tarefa_id = request.args.get('id')
    db.delete_tarefa(tarefa_id, user_id)
    return jsonify({'success': True}), 200

@app.route('/api/estudos/metas', methods=['GET'])
@login_required
def get_metas():
    token = request.headers.get('Authorization')
    user_id = auth.get_user_id_from_token(token)
    metas = db.get_metas(user_id)
    return jsonify(metas), 200

@app.route('/api/estudos/metas', methods=['POST'])
@login_required
def create_meta():
    token = request.headers.get('Authorization')
    user_id = auth.get_user_id_from_token(token)
    data = request.json
    meta_id = db.create_meta(user_id, data['text'], data.get('completed', False))
    return jsonify({'id': meta_id, 'success': True}), 201

@app.route('/api/estudos/metas', methods=['PUT'])
@login_required
def update_meta():
    token = request.headers.get('Authorization')
    user_id = auth.get_user_id_from_token(token)
    data = request.json
    db.update_meta(data['id'], data.get('completed'))
    return jsonify({'success': True}), 200

@app.route('/api/estudos/metas', methods=['DELETE'])
@login_required
def delete_meta():
    token = request.headers.get('Authorization')
    user_id = auth.get_user_id_from_token(token)
    meta_id = request.args.get('id')
    db.delete_meta(meta_id, user_id)
    return jsonify({'success': True}), 200

@app.route('/api/estudos/materiais', methods=['GET'])
@login_required
def get_materiais():
    token = request.headers.get('Authorization')
    user_id = auth.get_user_id_from_token(token)
    materiais = db.get_materiais(user_id)
    return jsonify(materiais), 200

@app.route('/api/estudos/materiais', methods=['POST'])
@login_required
def create_material():
    token = request.headers.get('Authorization')
    user_id = auth.get_user_id_from_token(token)
    data = request.json
    material_id = db.create_material(user_id, data['name'], data['link'])
    return jsonify({'id': material_id, 'success': True}), 201

@app.route('/api/estudos/materiais/<int:material_id>', methods=['DELETE'])
@login_required
def delete_material(material_id):
    token = request.headers.get('Authorization')
    user_id = auth.get_user_id_from_token(token)
    db.delete_material(material_id, user_id)
    return jsonify({'success': True}), 200

@app.route('/api/estudos/anotacoes', methods=['GET'])
@login_required
def get_anotacoes():
    token = request.headers.get('Authorization')
    user_id = auth.get_user_id_from_token(token)
    content = db.get_anotacoes(user_id)
    return jsonify({'content': content or ''}), 200

@app.route('/api/estudos/anotacoes', methods=['POST'])
@login_required
def save_anotacoes():
    token = request.headers.get('Authorization')
    user_id = auth.get_user_id_from_token(token)
    data = request.json
    db.save_anotacoes(user_id, data['content'])
    return jsonify({'success': True}), 200

@app.route('/api/estudos/stats', methods=['GET'])
@login_required
def get_stats():
    token = request.headers.get('Authorization')
    user_id = auth.get_user_id_from_token(token)
    stats = db.get_stats(user_id)
    return jsonify(stats), 200

@app.route('/api/estudos/stats', methods=['POST'])
@login_required
def update_stats():
    token = request.headers.get('Authorization')
    user_id = auth.get_user_id_from_token(token)
    data = request.json
    db.update_stats(user_id, data)
    return jsonify({'success': True}), 200

@app.route('/api/estudos/reset', methods=['POST'])
@login_required
def reset_estudos():
    token = request.headers.get('Authorization')
    user_id = auth.get_user_id_from_token(token)
    db.reset_dados_estudos(user_id)
    return jsonify({'success': True, 'message': 'Dados resetados com sucesso'}), 200

# ========== ROTA DE DEBUG ==========

@app.route('/api/studio/projetos/<int:projeto_id>/arquivos/debug', methods=['GET'])
@login_required
def debug_arquivos(projeto_id):
    token = request.headers.get('Authorization')
    user_id = auth.get_user_id_from_token(token)
    arquivos = db.get_arquivos(projeto_id, user_id)
    return jsonify({
        'projeto_id': projeto_id,
        'user_id': user_id,
        'arquivos': arquivos
    }), 200

# ========== INICIAR SERVIDOR ==========

if __name__ == '__main__':
    print("\n" + "="*50)
    print("🚀 SERVIDOR EVOLVEGLOBAL")
    print("="*50)
    print("\n✅ Banco de dados inicializado")
    print("📱 API disponível em: http://localhost:5000")
    print("\n📋 Rotas disponíveis:")
    print("   POST   /api/cadastro")
    print("   POST   /api/login")
    print("   GET    /api/verificar-token")
    print("   GET    /api/studio/projetos")
    print("   POST   /api/studio/projetos")
    print("   PUT    /api/studio/projetos/<id>")
    print("   DELETE /api/studio/projetos/<id>")
    print("   GET    /api/studio/projetos/<id>/arquivos")
    print("   POST   /api/studio/projetos/<id>/arquivos")
    print("   DELETE /api/studio/projetos/<id>/arquivos/<path>")
    print("   GET    /api/studio/projetos/<id>/pastas")
    print("   POST   /api/studio/projetos/<id>/pastas")
    print("   DELETE /api/studio/projetos/<id>/pastas")
    print("\n" + "="*50)
    print("🔥 Servidor rodando em http://localhost:5000")
    print("="*50 + "\n")
    
    # Usar threaded=True para melhor concorrência
    app.run(debug=True, host='0.0.0.0', port=5000, threaded=True)