import os
import sys
from pathlib import Path
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from functools import wraps
import secrets
from datetime import datetime, timedelta
import hashlib
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', 'AIzaSyAJciP00ofIiv9NfSgt8b-9MLuYZyPtzoM')
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-lite:generateContent"

# ========== CONFIGURAÇÃO DO BANCO DE DADOS ==========
# Obter o diretório base de forma absoluta
BASE_DIR = Path(__file__).parent.resolve()
DATA_DIR = BASE_DIR / 'data'

# Criar a pasta data (com permissões)
try:
    DATA_DIR.mkdir(exist_ok=True, parents=True)
    print(f"✅ Pasta data criada em: {DATA_DIR}")
    
    # Testar permissão de escrita
    test_file = DATA_DIR / '.write_test'
    test_file.write_text('test')
    test_file.unlink()
    print(f"✅ Permissão de escrita confirmada em: {DATA_DIR}")
    
except Exception as e:
    print(f"❌ Erro na pasta data: {e}")
    # Fallback: usar diretório temporário
    import tempfile
    DATA_DIR = Path(tempfile.gettempdir()) / 'evolveglobal_data'
    DATA_DIR.mkdir(exist_ok=True, parents=True)
    print(f"⚠️ Usando diretório alternativo: {DATA_DIR}")

# Caminho completo do banco de dados
DB_PATH = DATA_DIR / 'evolveglobal.db'
DATABASE_URL = f'sqlite:///{DB_PATH}'

TEMPLATES_DIR = BASE_DIR.parent / 'templates'
STATIC_ROOT = BASE_DIR.parent

print(f"📁 Pasta do banco: {DATA_DIR}")
print(f"📄 Arquivo do banco: {DB_PATH}")
print(f"📁 Pasta de templates: {TEMPLATES_DIR}")
print(f"🔗 URL: {DATABASE_URL}")

# ========== CONFIGURAÇÃO DO FLASK ==========
class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', secrets.token_hex(16))

# Configuração do CORS
CORS(app, supports_credentials=True, origins=['*'])

# Configuração do SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'connect_args': {'check_same_thread': False},
}
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializar banco de dados
db.init_app(app)

# ========== MODELOS ==========

class Usuario(db.Model):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    senha_hash = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

class Token(db.Model):
    __tablename__ = 'tokens'
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(200), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('usuarios.id', ondelete='CASCADE'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    expires_at = db.Column(db.DateTime)
    revoked = db.Column(db.Boolean, default=False)

class Projeto(db.Model):
    __tablename__ = 'projetos'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('usuarios.id', ondelete='CASCADE'), nullable=False)
    nome = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    __table_args__ = (db.UniqueConstraint('user_id', 'nome', name='unique_user_projeto'),)

class Pasta(db.Model):
    __tablename__ = 'pastas'
    id = db.Column(db.Integer, primary_key=True)
    projeto_id = db.Column(db.Integer, db.ForeignKey('projetos.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('usuarios.id', ondelete='CASCADE'), nullable=False)
    nome = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    __table_args__ = (db.UniqueConstraint('projeto_id', 'user_id', 'nome', name='unique_projeto_pasta'),)

class Arquivo(db.Model):
    __tablename__ = 'arquivos'
    id = db.Column(db.Integer, primary_key=True)
    projeto_id = db.Column(db.Integer, db.ForeignKey('projetos.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('usuarios.id', ondelete='CASCADE'), nullable=False)
    caminho = db.Column(db.String(500), nullable=False)
    conteudo = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    __table_args__ = (db.UniqueConstraint('projeto_id', 'user_id', 'caminho', name='unique_projeto_arquivo'),)

class Tarefa(db.Model):
    __tablename__ = 'tarefas'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('usuarios.id', ondelete='CASCADE'), nullable=False)
    text = db.Column(db.String(500), nullable=False)
    subject = db.Column(db.String(100), nullable=False)
    completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.now)

class Meta(db.Model):
    __tablename__ = 'metas'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('usuarios.id', ondelete='CASCADE'), nullable=False)
    text = db.Column(db.String(500), nullable=False)
    completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.now)

class Material(db.Model):
    __tablename__ = 'materiais'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('usuarios.id', ondelete='CASCADE'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    link = db.Column(db.String(500), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)

class Anotacao(db.Model):
    __tablename__ = 'anotacoes'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('usuarios.id', ondelete='CASCADE'), unique=True, nullable=False)
    content = db.Column(db.Text, nullable=True)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

class StatsEstudo(db.Model):
    __tablename__ = 'stats_estudos'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('usuarios.id', ondelete='CASCADE'), unique=True, nullable=False)
    study_minutes_today = db.Column(db.Integer, default=0)
    pomodoro_sessions = db.Column(db.Integer, default=0)
    last_update = db.Column(db.Date)

class Chat(db.Model):
    __tablename__ = 'chats'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('usuarios.id', ondelete='CASCADE'), nullable=False)
    titulo = db.Column(db.String(100), default='Nova Conversa')
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

class MensagemChat(db.Model):
    __tablename__ = 'mensagens_chat'
    id = db.Column(db.Integer, primary_key=True)
    chat_id = db.Column(db.Integer, db.ForeignKey('chats.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('usuarios.id', ondelete='CASCADE'), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)

class ApiKey(db.Model):
    __tablename__ = 'api_keys'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('usuarios.id', ondelete='CASCADE'), nullable=False)
    provider = db.Column(db.String(50), nullable=False)
    api_key = db.Column(db.String(500), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    __table_args__ = (db.UniqueConstraint('user_id', 'provider', name='unique_user_provider'),)

# ========== AUTENTICAÇÃO ==========

class AuthManager:
    def __init__(self):
        pass
    
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
        usuario = Usuario(nome=nome, email=email, senha_hash=senha_hash)
        db.session.add(usuario)
        db.session.commit()
        return usuario.id
    
    def authenticate_user(self, email, senha):
        user = Usuario.query.filter_by(email=email).first()
        if user and self.verify_password(senha, user.senha_hash):
            return {'id': user.id, 'nome': user.nome, 'email': user.email}
        return None
    
    def generate_token(self, user_id):
        token = secrets.token_urlsafe(32)
        expires_at = datetime.now() + timedelta(days=7)
        token_obj = Token(token=token, user_id=user_id, expires_at=expires_at)
        db.session.add(token_obj)
        db.session.commit()
        return token
    
    def verify_token(self, token):
        token_data = Token.query.filter_by(token=token, revoked=False).first()
        if not token_data:
            return False
        if token_data.expires_at and datetime.now() > token_data.expires_at:
            return False
        return True
    
    def get_user_id_from_token(self, token):
        token_data = Token.query.filter_by(token=token, revoked=False).first()
        return token_data.user_id if token_data else None
    
    def revoke_token(self, token):
        token_data = Token.query.filter_by(token=token).first()
        if token_data:
            token_data.revoked = True
            db.session.commit()

auth = AuthManager()

# ========== DECORATOR ==========

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token or not auth.verify_token(token):
            return jsonify({'error': 'Não autorizado'}), 401
        return f(*args, **kwargs)
    return decorated_function

# ========== FUNÇÕES DE BANCO DE DADOS ==========

def get_user_by_email(email):
    user = Usuario.query.filter_by(email=email).first()
    return {'id': user.id, 'nome': user.nome, 'email': user.email, 'senha_hash': user.senha_hash} if user else None

def get_user_by_id(user_id):
    user = Usuario.query.get(user_id)
    return {'id': user.id, 'nome': user.nome, 'email': user.email, 'created_at': user.created_at} if user else None

def get_projetos(user_id):
    projetos = Projeto.query.filter_by(user_id=user_id).order_by(Projeto.updated_at.desc()).all()
    return [{'id': p.id, 'nome': p.nome, 'created_at': p.created_at, 'updated_at': p.updated_at} for p in projetos]

def create_projeto(user_id, nome):
    projeto = Projeto(user_id=user_id, nome=nome)
    db.session.add(projeto)
    db.session.commit()
    return projeto.id

def update_projeto(projeto_id, user_id, novo_nome):
    projeto = Projeto.query.filter_by(id=projeto_id, user_id=user_id).first()
    if projeto:
        projeto.nome = novo_nome
        projeto.updated_at = datetime.now()
        db.session.commit()

def delete_projeto(projeto_id, user_id):
    Projeto.query.filter_by(id=projeto_id, user_id=user_id).delete()
    db.session.commit()

def get_arquivos(projeto_id, user_id):
    arquivos = Arquivo.query.filter_by(projeto_id=projeto_id, user_id=user_id).all()
    return [{'caminho': a.caminho, 'conteudo': a.conteudo} for a in arquivos]

def save_arquivo(projeto_id, user_id, caminho, conteudo):
    arquivo = Arquivo.query.filter_by(projeto_id=projeto_id, user_id=user_id, caminho=caminho).first()
    if arquivo:
        arquivo.conteudo = conteudo
        arquivo.updated_at = datetime.now()
    else:
        arquivo = Arquivo(projeto_id=projeto_id, user_id=user_id, caminho=caminho, conteudo=conteudo)
        db.session.add(arquivo)
    db.session.commit()

def delete_arquivo(projeto_id, user_id, caminho):
    Arquivo.query.filter_by(projeto_id=projeto_id, user_id=user_id, caminho=caminho).delete()
    db.session.commit()

def get_pastas(projeto_id, user_id):
    pastas = Pasta.query.filter_by(projeto_id=projeto_id, user_id=user_id).all()
    return [{'nome': p.nome} for p in pastas]

def create_pasta(projeto_id, user_id, nome):
    pasta = Pasta(projeto_id=projeto_id, user_id=user_id, nome=nome)
    db.session.add(pasta)
    db.session.commit()

def delete_pasta(projeto_id, user_id, nome):
    Pasta.query.filter_by(projeto_id=projeto_id, user_id=user_id, nome=nome).delete()
    db.session.commit()

def get_tarefas(user_id):
    tarefas = Tarefa.query.filter_by(user_id=user_id).order_by(Tarefa.created_at.desc()).all()
    return [{'id': t.id, 'text': t.text, 'subject': t.subject, 'completed': t.completed} for t in tarefas]

def create_tarefa(user_id, text, subject, completed=False):
    tarefa = Tarefa(user_id=user_id, text=text, subject=subject, completed=completed)
    db.session.add(tarefa)
    db.session.commit()
    return tarefa.id

def update_tarefa(tarefa_id, completed):
    Tarefa.query.filter_by(id=tarefa_id).update({'completed': completed})
    db.session.commit()

def delete_tarefa(tarefa_id, user_id):
    Tarefa.query.filter_by(id=tarefa_id, user_id=user_id).delete()
    db.session.commit()

def get_metas(user_id):
    metas = Meta.query.filter_by(user_id=user_id).order_by(Meta.created_at.desc()).all()
    return [{'id': m.id, 'text': m.text, 'completed': m.completed} for m in metas]

def create_meta(user_id, text, completed=False):
    meta = Meta(user_id=user_id, text=text, completed=completed)
    db.session.add(meta)
    db.session.commit()
    return meta.id

def update_meta(meta_id, completed):
    Meta.query.filter_by(id=meta_id).update({'completed': completed})
    db.session.commit()

def delete_meta(meta_id, user_id):
    Meta.query.filter_by(id=meta_id, user_id=user_id).delete()
    db.session.commit()

def get_materiais(user_id):
    materiais = Material.query.filter_by(user_id=user_id).order_by(Material.created_at.desc()).all()
    return [{'id': m.id, 'name': m.name, 'link': m.link} for m in materiais]

def create_material(user_id, name, link):
    material = Material(user_id=user_id, name=name, link=link)
    db.session.add(material)
    db.session.commit()
    return material.id

def delete_material(material_id, user_id):
    Material.query.filter_by(id=material_id, user_id=user_id).delete()
    db.session.commit()

def get_anotacoes(user_id):
    anotacao = Anotacao.query.filter_by(user_id=user_id).first()
    return anotacao.content if anotacao else None

def save_anotacoes(user_id, content):
    anotacao = Anotacao.query.filter_by(user_id=user_id).first()
    if anotacao:
        anotacao.content = content
        anotacao.updated_at = datetime.now()
    else:
        anotacao = Anotacao(user_id=user_id, content=content)
        db.session.add(anotacao)
    db.session.commit()

def get_stats(user_id):
    stats = StatsEstudo.query.filter_by(user_id=user_id).first()
    if stats:
        return {'study_minutes_today': stats.study_minutes_today, 'pomodoro_sessions': stats.pomodoro_sessions}
    return {'study_minutes_today': 0, 'pomodoro_sessions': 0}

def update_stats(user_id, stats_data):
    stats = StatsEstudo.query.filter_by(user_id=user_id).first()
    if stats:
        stats.study_minutes_today = stats_data.get('study_minutes_today', 0)
        stats.pomodoro_sessions = stats_data.get('pomodoro_sessions', 0)
        stats.last_update = datetime.now().date()
    else:
        stats = StatsEstudo(
            user_id=user_id,
            study_minutes_today=stats_data.get('study_minutes_today', 0),
            pomodoro_sessions=stats_data.get('pomodoro_sessions', 0),
            last_update=datetime.now().date()
        )
        db.session.add(stats)
    db.session.commit()

def reset_dados_estudos(user_id):
    Tarefa.query.filter_by(user_id=user_id).delete()
    Meta.query.filter_by(user_id=user_id).delete()
    Material.query.filter_by(user_id=user_id).delete()
    Anotacao.query.filter_by(user_id=user_id).delete()
    StatsEstudo.query.filter_by(user_id=user_id).delete()
    db.session.commit()

def get_chats(user_id):
    chats = Chat.query.filter_by(user_id=user_id).order_by(Chat.updated_at.desc()).all()
    return [{'id': c.id, 'titulo': c.titulo, 'created_at': c.created_at, 'updated_at': c.updated_at} for c in chats]

def create_chat(user_id, titulo='Nova Conversa'):
    chat = Chat(user_id=user_id, titulo=titulo)
    db.session.add(chat)
    db.session.commit()
    return chat.id

def delete_chat(chat_id, user_id):
    Chat.query.filter_by(id=chat_id, user_id=user_id).delete()
    db.session.commit()

def get_mensagens_chat(chat_id, user_id):
    mensagens = MensagemChat.query.filter_by(chat_id=chat_id, user_id=user_id).order_by(MensagemChat.created_at.asc()).all()
    return [{'id': m.id, 'role': m.role, 'content': m.content, 'created_at': m.created_at} for m in mensagens]

def save_mensagem(chat_id, user_id, role, content):
    mensagem = MensagemChat(chat_id=chat_id, user_id=user_id, role=role, content=content)
    db.session.add(mensagem)
    Chat.query.filter_by(id=chat_id, user_id=user_id).update({'updated_at': datetime.now()})
    db.session.commit()

def update_chat_titulo(chat_id, user_id, titulo):
    Chat.query.filter_by(id=chat_id, user_id=user_id).update({'titulo': titulo[:50]})
    db.session.commit()

# ========== ROTAS ==========

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
        
        if get_user_by_email(email):
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
def get_projetos_route():
    token = request.headers.get('Authorization')
    user_id = auth.get_user_id_from_token(token)
    projetos = get_projetos(user_id)
    return jsonify(projetos), 200

@app.route('/api/studio/projetos', methods=['POST'])
@login_required
def create_projeto_route():
    token = request.headers.get('Authorization')
    user_id = auth.get_user_id_from_token(token)
    data = request.json
    nome = data.get('nome', '').strip()
    
    if not nome:
        return jsonify({'error': 'Nome do projeto é obrigatório'}), 400
    
    projeto_id = create_projeto(user_id, nome)
    return jsonify({'id': projeto_id, 'success': True}), 201

@app.route('/api/studio/projetos/<int:projeto_id>', methods=['PUT'])
@login_required
def update_projeto_route(projeto_id):
    token = request.headers.get('Authorization')
    user_id = auth.get_user_id_from_token(token)
    data = request.json
    novo_nome = data.get('nome', '').strip()
    
    if not novo_nome:
        return jsonify({'error': 'Novo nome é obrigatório'}), 400
    
    update_projeto(projeto_id, user_id, novo_nome)
    return jsonify({'success': True}), 200

@app.route('/api/studio/projetos/<int:projeto_id>', methods=['DELETE'])
@login_required
def delete_projeto_route(projeto_id):
    token = request.headers.get('Authorization')
    user_id = auth.get_user_id_from_token(token)
    delete_projeto(projeto_id, user_id)
    return jsonify({'success': True}), 200

@app.route('/api/studio/projetos/<int:projeto_id>/arquivos', methods=['GET'])
@login_required
def get_arquivos_route(projeto_id):
    token = request.headers.get('Authorization')
    user_id = auth.get_user_id_from_token(token)
    arquivos = get_arquivos(projeto_id, user_id)
    return jsonify(arquivos), 200

@app.route('/api/studio/projetos/<int:projeto_id>/arquivos', methods=['POST'])
@login_required
def save_arquivo_route(projeto_id):
    token = request.headers.get('Authorization')
    user_id = auth.get_user_id_from_token(token)
    data = request.json
    caminho = data.get('caminho', '')
    conteudo = data.get('conteudo', '')
    
    if not caminho:
        return jsonify({'error': 'Caminho do arquivo é obrigatório'}), 400
    
    save_arquivo(projeto_id, user_id, caminho, conteudo)
    return jsonify({'success': True}), 200

@app.route('/api/studio/projetos/<int:projeto_id>/arquivos/<path:caminho>', methods=['DELETE'])
@login_required
def delete_arquivo_route(projeto_id, caminho):
    token = request.headers.get('Authorization')
    user_id = auth.get_user_id_from_token(token)
    delete_arquivo(projeto_id, user_id, caminho)
    return jsonify({'success': True}), 200

@app.route('/api/studio/projetos/<int:projeto_id>/pastas', methods=['GET'])
@login_required
def get_pastas_route(projeto_id):
    token = request.headers.get('Authorization')
    user_id = auth.get_user_id_from_token(token)
    pastas = get_pastas(projeto_id, user_id)
    return jsonify(pastas), 200

@app.route('/api/studio/projetos/<int:projeto_id>/pastas', methods=['POST'])
@login_required
def create_pasta_route(projeto_id):
    token = request.headers.get('Authorization')
    user_id = auth.get_user_id_from_token(token)
    data = request.json
    nome = data.get('nome', '').strip()
    
    if not nome:
        return jsonify({'error': 'Nome da pasta é obrigatório'}), 400
    
    create_pasta(projeto_id, user_id, nome)
    return jsonify({'success': True}), 201

@app.route('/api/studio/projetos/<int:projeto_id>/pastas', methods=['DELETE'])
@login_required
def delete_pasta_route(projeto_id):
    token = request.headers.get('Authorization')
    user_id = auth.get_user_id_from_token(token)
    data = request.json
    nome = data.get('nome', '').strip()
    
    if not nome:
        return jsonify({'error': 'Nome da pasta é obrigatório'}), 400
    
    delete_pasta(projeto_id, user_id, nome)
    return jsonify({'success': True}), 200

# ========== ROTAS DE ESTUDOS ==========

@app.route('/api/estudos/tarefas', methods=['GET'])
@login_required
def get_tarefas_route():
    token = request.headers.get('Authorization')
    user_id = auth.get_user_id_from_token(token)
    tarefas = get_tarefas(user_id)
    return jsonify(tarefas), 200

@app.route('/api/estudos/tarefas', methods=['POST'])
@login_required
def create_tarefa_route():
    token = request.headers.get('Authorization')
    user_id = auth.get_user_id_from_token(token)
    data = request.json
    tarefa_id = create_tarefa(user_id, data['text'], data['subject'], data.get('completed', False))
    return jsonify({'id': tarefa_id, 'success': True}), 201

@app.route('/api/estudos/tarefas', methods=['PUT'])
@login_required
def update_tarefa_route():
    token = request.headers.get('Authorization')
    user_id = auth.get_user_id_from_token(token)
    data = request.json
    update_tarefa(data['id'], data.get('completed'))
    return jsonify({'success': True}), 200

@app.route('/api/estudos/tarefas/<int:tarefa_id>', methods=['DELETE'])
@login_required
def delete_tarefa_route(tarefa_id):
    token = request.headers.get('Authorization')
    user_id = auth.get_user_id_from_token(token)
    delete_tarefa(tarefa_id, user_id)
    return jsonify({'success': True}), 200

@app.route('/api/estudos/metas', methods=['GET'])
@login_required
def get_metas_route():
    token = request.headers.get('Authorization')
    user_id = auth.get_user_id_from_token(token)
    metas = get_metas(user_id)
    return jsonify(metas), 200

@app.route('/api/estudos/metas', methods=['POST'])
@login_required
def create_meta_route():
    token = request.headers.get('Authorization')
    user_id = auth.get_user_id_from_token(token)
    data = request.json
    meta_id = create_meta(user_id, data['text'], data.get('completed', False))
    return jsonify({'id': meta_id, 'success': True}), 201

@app.route('/api/estudos/metas', methods=['PUT'])
@login_required
def update_meta_route():
    token = request.headers.get('Authorization')
    user_id = auth.get_user_id_from_token(token)
    data = request.json
    update_meta(data['id'], data.get('completed'))
    return jsonify({'success': True}), 200

@app.route('/api/estudos/metas/<int:meta_id>', methods=['DELETE'])
@login_required
def delete_meta_route(meta_id):
    token = request.headers.get('Authorization')
    user_id = auth.get_user_id_from_token(token)
    delete_meta(meta_id, user_id)
    return jsonify({'success': True}), 200

@app.route('/api/estudos/materiais', methods=['GET'])
@login_required
def get_materiais_route():
    token = request.headers.get('Authorization')
    user_id = auth.get_user_id_from_token(token)
    materiais = get_materiais(user_id)
    return jsonify(materiais), 200

@app.route('/api/estudos/materiais', methods=['POST'])
@login_required
def create_material_route():
    token = request.headers.get('Authorization')
    user_id = auth.get_user_id_from_token(token)
    data = request.json
    material_id = create_material(user_id, data['name'], data['link'])
    return jsonify({'id': material_id, 'success': True}), 201

@app.route('/api/estudos/materiais/<int:material_id>', methods=['DELETE'])
@login_required
def delete_material_route(material_id):
    token = request.headers.get('Authorization')
    user_id = auth.get_user_id_from_token(token)
    delete_material(material_id, user_id)
    return jsonify({'success': True}), 200

@app.route('/api/estudos/anotacoes', methods=['GET'])
@login_required
def get_anotacoes_route():
    token = request.headers.get('Authorization')
    user_id = auth.get_user_id_from_token(token)
    content = get_anotacoes(user_id)
    return jsonify({'content': content or ''}), 200

@app.route('/api/estudos/anotacoes', methods=['POST'])
@login_required
def save_anotacoes_route():
    token = request.headers.get('Authorization')
    user_id = auth.get_user_id_from_token(token)
    data = request.json
    save_anotacoes(user_id, data['content'])
    return jsonify({'success': True}), 200

@app.route('/api/estudos/stats', methods=['GET'])
@login_required
def get_stats_route():
    token = request.headers.get('Authorization')
    user_id = auth.get_user_id_from_token(token)
    stats = get_stats(user_id)
    return jsonify(stats), 200

@app.route('/api/estudos/stats', methods=['POST'])
@login_required
def update_stats_route():
    token = request.headers.get('Authorization')
    user_id = auth.get_user_id_from_token(token)
    data = request.json
    update_stats(user_id, data)
    return jsonify({'success': True}), 200

@app.route('/api/estudos/reset', methods=['POST'])
@login_required
def reset_estudos_route():
    token = request.headers.get('Authorization')
    user_id = auth.get_user_id_from_token(token)
    reset_dados_estudos(user_id)
    return jsonify({'success': True, 'message': 'Dados resetados com sucesso'}), 200

# ========== ROTAS PARA GERENCIAR CHAVE API ==========

@app.route('/api/chat/api-key', methods=['GET'])
@login_required
def get_user_api_key():
    """Obtém a chave API do usuário"""
    token = request.headers.get('Authorization')
    user_id = auth.get_user_id_from_token(token)
    
    # Buscar chave no banco
    api_key_record = ApiKey.query.filter_by(user_id=user_id, provider='gemini').first()
    
    if api_key_record:
        # Retornar apenas se existe (não mostrar a chave por segurança)
        return jsonify({'has_key': True, 'key_exists': True})
    else:
        return jsonify({'has_key': False, 'key_exists': False})

@app.route('/api/chat/api-key', methods=['POST'])
@login_required
def save_user_api_key():
    """Salva a chave API do usuário"""
    token = request.headers.get('Authorization')
    user_id = auth.get_user_id_from_token(token)
    data = request.json
    api_key = data.get('api_key', '')
    
    if not api_key:
        return jsonify({'error': 'Chave API é obrigatória'}), 400
    
    # Verificar se já existe
    existing = ApiKey.query.filter_by(user_id=user_id, provider='gemini').first()
    
    if existing:
        existing.api_key = api_key
        existing.updated_at = datetime.now()
    else:
        new_key = ApiKey(user_id=user_id, provider='gemini', api_key=api_key)
        db.session.add(new_key)
    
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Chave API salva com sucesso'}), 200

@app.route('/api/chat/api-key', methods=['DELETE'])
@login_required
def delete_user_api_key():
    """Remove a chave API do usuário"""
    token = request.headers.get('Authorization')
    user_id = auth.get_user_id_from_token(token)
    
    ApiKey.query.filter_by(user_id=user_id, provider='gemini').delete()
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Chave API removida'}), 200

# ========== ROTA DO CHAT COM GEMINI (USANDO CHAVE DO BANCO) ==========
@app.route('/api/chat/send', methods=['POST'])
@login_required
def chat_send():
    try:
        token = request.headers.get('Authorization')
        user_id = auth.get_user_id_from_token(token)
        data = request.json
        chat_id = data.get('chat_id')
        message = data.get('message', '').strip()
        
        if not chat_id:
            return jsonify({'error': 'Chat ID é obrigatório'}), 400
        if not message:
            return jsonify({'error': 'Mensagem vazia'}), 400
        
        chat = Chat.query.filter_by(id=chat_id, user_id=user_id).first()
        if not chat:
            return jsonify({'error': 'Chat não encontrado'}), 404
        
        save_mensagem(chat_id, user_id, 'user', message)
        
        # Buscar chave API do usuário no banco
        api_key_record = ApiKey.query.filter_by(user_id=user_id, provider='gemini').first()
        
        # Usar chave do usuário ou fallback para a chave padrão
        if api_key_record and api_key_record.api_key:
            api_key = api_key_record.api_key
            print(f"🔑 Usando chave do usuário {user_id}")
        else:
            api_key = GEMINI_API_KEY  # Chave padrão do sistema
            print(f"🔑 Usando chave padrão do sistema")
        
        # Chamar API do Gemini
        import requests
        url = f"{GEMINI_API_URL}?key={api_key}"
        payload = {
            "contents": [{
                "parts": [{"text": message}]
            }],
            "generationConfig": {
                "temperature": 0.7,
                "maxOutputTokens": 800
            }
        }
        
        response = requests.post(url, json=payload, timeout=30)
        result = response.json()
        
        if response.status_code == 200:
            reply = result.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', 'Desculpe, não entendi.')
            save_mensagem(chat_id, user_id, 'assistant', reply)
            return jsonify({'success': True, 'response': reply, 'chat_id': chat_id}), 200
        else:
            error_msg = result.get('error', {}).get('message', 'Erro desconhecido')
            return jsonify({'error': f'Erro na API Gemini: {error_msg}'}), 500
            
    except Exception as e:
        print(f"Erro no chat: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/chat/chats', methods=['GET'])
@login_required
def get_chats_route():
    token = request.headers.get('Authorization')
    user_id = auth.get_user_id_from_token(token)
    chats = get_chats(user_id)
    return jsonify(chats), 200

@app.route('/api/chat/chats', methods=['POST'])
@login_required
def create_chat_route():
    token = request.headers.get('Authorization')
    user_id = auth.get_user_id_from_token(token)
    data = request.json
    titulo = data.get('titulo', 'Nova Conversa')
    chat_id = create_chat(user_id, titulo)
    return jsonify({'id': chat_id, 'success': True}), 201

@app.route('/api/chat/chats/<int:chat_id>', methods=['DELETE'])
@login_required
def delete_chat_route(chat_id):
    token = request.headers.get('Authorization')
    user_id = auth.get_user_id_from_token(token)
    delete_chat(chat_id, user_id)
    return jsonify({'success': True}), 200

@app.route('/api/chat/chats/<int:chat_id>/mensagens', methods=['GET'])
@login_required
def get_mensagens_route(chat_id):
    token = request.headers.get('Authorization')
    user_id = auth.get_user_id_from_token(token)
    mensagens = get_mensagens_chat(chat_id, user_id)
    return jsonify(mensagens), 200

@app.route('/api/chat/chats/<int:chat_id>/mensagens', methods=['POST'])
@login_required
def save_mensagem_route(chat_id):
    token = request.headers.get('Authorization')
    user_id = auth.get_user_id_from_token(token)
    data = request.json
    save_mensagem(chat_id, user_id, data['role'], data['content'])
    return jsonify({'success': True}), 200

@app.route('/api/chat/chats/<int:chat_id>/titulo', methods=['PUT'])
@login_required
def update_chat_titulo_route(chat_id):
    token = request.headers.get('Authorization')
    user_id = auth.get_user_id_from_token(token)
    data = request.json
    update_chat_titulo(chat_id, user_id, data['titulo'])
    return jsonify({'success': True}), 200

# ========== ROTAS DOS TEMPLATES E ESTÁTICOS ==========

def serve_static_file(directory, filename):
    return send_from_directory(str(directory), filename)

@app.route('/')
@app.route('/index.html')
def serve_index():
    return serve_static_file(STATIC_ROOT, 'index.html')

@app.route('/login.html')
def serve_login():
    return serve_static_file(TEMPLATES_DIR, 'login.html')

@app.route('/cadastro.html')
def serve_cadastro():
    return serve_static_file(TEMPLATES_DIR, 'cadastro.html')

@app.route('/chat.html')
def serve_chat():
    return serve_static_file(TEMPLATES_DIR, 'chat.html')

@app.route('/estudo.html')
def serve_estudo():
    return serve_static_file(TEMPLATES_DIR, 'estudo.html')

@app.route('/criando.html')
def serve_criando():
    return serve_static_file(TEMPLATES_DIR, 'criando.html')

@app.route('/templates/<path:filename>')
def serve_template_files(filename):
    return serve_static_file(TEMPLATES_DIR, filename)

@app.route('/css/<path:filename>')
def serve_css(filename):
    return serve_static_file(STATIC_ROOT / 'css', filename)

@app.route('/js/<path:filename>')
def serve_js(filename):
    return serve_static_file(STATIC_ROOT / 'js', filename)

@app.route('/images/<path:filename>')
def serve_images(filename):
    return serve_static_file(STATIC_ROOT / 'images', filename)


# ========== INICIALIZAÇÃO ==========
if __name__ == '__main__':
    with app.app_context():
        try:
            # Garantir que o diretório existe antes de criar as tabelas
            DATA_DIR.mkdir(exist_ok=True, parents=True)
            
            # Criar as tabelas
            db.create_all()
            
            # Verificar se o arquivo foi criado
            if DB_PATH.exists():
                print(f"✅ Banco de dados criado com sucesso!")
                print(f"📍 Localização: {DB_PATH}")
                print(f"📊 Tamanho: {DB_PATH.stat().st_size} bytes")
            else:
                print(f"⚠️ Banco de dados NÃO foi criado em: {DB_PATH}")
                
                # Tentar criar um arquivo vazio manualmente
                try:
                    DB_PATH.touch()
                    print(f"✅ Arquivo criado manualmente em: {DB_PATH}")
                except Exception as e:
                    print(f"❌ Erro ao criar manualmente: {e}")
                    
        except Exception as e:
            print(f"❌ Erro ao criar banco de dados: {e}")
            print("🔧 Usando banco de dados em memória...")
            app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
            db.create_all()
            print("✅ Usando banco de dados em memória (dados serão perdidos ao reiniciar)")
    
    print("\n" + "="*50)
    print("🚀 SERVIDOR EVOLVEGLOBAL")
    print("="*50)
    print(f"📱 API disponível em: http://localhost:5000")
    print(f"💾 Banco de dados: {app.config['SQLALCHEMY_DATABASE_URI']}")
    print("="*50 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)