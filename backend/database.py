import sqlite3
from contextlib import contextmanager
from datetime import datetime

class Database:
    def __init__(self, db_name='evolveglobal.db'):
        self.db_name = db_name
        self.init_db()
    
    @contextmanager
    def get_connection(self):
        conn = sqlite3.connect(self.db_name)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def init_db(self):
        """Inicializa o banco de dados com todas as tabelas necessárias"""
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
            
            # Tabela de tokens (para logout/sessões)
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
        # Tabela de tarefas/checklist
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
        
        # Tabela de metas
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
        
        # Tabela de materiais
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
        
        # Tabela de anotações
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS anotacoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER UNIQUE NOT NULL,
                content TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES usuarios (id) ON DELETE CASCADE
            )
        ''')
        
        # Tabela de estatísticas
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
                
        # Índices
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_tarefas_user ON tarefas(user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_metas_user ON metas(user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_materiais_user ON materiais(user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_anotacoes_user ON anotacoes(user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_stats_user ON stats_estudos(user_id)')

        print("✅ Banco de dados inicializado com sucesso!")
    
    # ========== OPERAÇÕES DE USUÁRIO ==========
    
    def create_user(self, nome, email, senha_hash):
        """Cria um novo usuário"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO usuarios (nome, email, senha_hash) VALUES (?, ?, ?)',
                (nome, email, senha_hash)
            )
            return cursor.lastrowid
    
    def get_user_by_email(self, email):
        """Busca usuário por email"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM usuarios WHERE email = ?', (email,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def get_user_by_id(self, user_id):
        """Busca usuário por ID"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM usuarios WHERE id = ?', (user_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def update_user(self, user_id, nome=None, email=None):
        """Atualiza dados do usuário"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if nome:
                cursor.execute(
                    'UPDATE usuarios SET nome = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?',
                    (nome, user_id)
                )
            if email:
                cursor.execute(
                    'UPDATE usuarios SET email = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?',
                    (email, user_id)
                )
    
    def update_password(self, user_id, senha_hash):
        """Atualiza a senha do usuário"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'UPDATE usuarios SET senha_hash = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?',
                (senha_hash, user_id)
            )
    
    # ========== OPERAÇÕES DE TOKEN ==========
    
    def save_token(self, token, user_id, expires_at=None):
        """Salva um token no banco"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO tokens (token, user_id, expires_at) VALUES (?, ?, ?)',
                (token, user_id, expires_at)
            )
            return cursor.lastrowid
    
    def get_token(self, token):
        """Busca um token"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'SELECT * FROM tokens WHERE token = ? AND revoked = 0',
                (token,)
            )
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def revoke_token(self, token):
        """Revoga um token (logout)"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'UPDATE tokens SET revoked = 1 WHERE token = ?',
                (token,)
            )
    
    def revoke_all_user_tokens(self, user_id):
        """Revoga todos os tokens de um usuário"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'UPDATE tokens SET revoked = 1 WHERE user_id = ?',
                (user_id,)
            )
        # Métodos para Tarefas
def get_tarefas(self, user_id):
    with self.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM tarefas WHERE user_id = ? ORDER BY created_at DESC', (user_id,))
        return [dict(row) for row in cursor.fetchall()]

def create_tarefa(self, user_id, text, subject, completed=False):
    with self.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO tarefas (user_id, text, subject, completed) VALUES (?, ?, ?, ?)',
            (user_id, text, subject, completed)
        )
        return cursor.lastrowid

def update_tarefa(self, tarefa_id, completed):
    with self.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('UPDATE tarefas SET completed = ? WHERE id = ?', (completed, tarefa_id))

def delete_tarefa(self, tarefa_id, user_id):
    with self.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM tarefas WHERE id = ? AND user_id = ?', (tarefa_id, user_id))

# Métodos para Metas
def get_metas(self, user_id):
    with self.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM metas WHERE user_id = ? ORDER BY created_at DESC', (user_id,))
        return [dict(row) for row in cursor.fetchall()]

def create_meta(self, user_id, text, completed=False):
    with self.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO metas (user_id, text, completed) VALUES (?, ?, ?)',
            (user_id, text, completed)
        )
        return cursor.lastrowid

def update_meta(self, meta_id, completed):
    with self.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('UPDATE metas SET completed = ? WHERE id = ?', (completed, meta_id))

def delete_meta(self, meta_id, user_id):
    with self.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM metas WHERE id = ? AND user_id = ?', (meta_id, user_id))

# Métodos para Materiais
# Métodos para Materiais
def get_materiais(self, user_id):
    with self.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM materiais WHERE user_id = ? ORDER BY created_at DESC', (user_id,))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

def create_material(self, user_id, name, link):
    with self.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO materiais (user_id, name, link) VALUES (?, ?, ?)',
            (user_id, name, link)
        )
        conn.commit()
        return cursor.lastrowid

def delete_material(self, material_id, user_id):
    with self.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM materiais WHERE id = ? AND user_id = ?', (material_id, user_id))
        conn.commit()
        
# Métodos para Anotações
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

# Métodos para Estatísticas
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

# ========== OPERAÇÕES DO CODE STUDIO ==========

def get_projetos(self, user_id):
    with self.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, nome, created_at, updated_at 
            FROM projetos 
            WHERE user_id = ? 
            ORDER BY updated_at DESC
        ''', (user_id,))
        return [dict(row) for row in cursor.fetchall()]

def create_projeto(self, user_id, nome):
    with self.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO projetos (user_id, nome) 
            VALUES (?, ?)
        ''', (user_id, nome))
        conn.commit()
        return cursor.lastrowid

def update_projeto(self, projeto_id, user_id, novo_nome):
    with self.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE projetos 
            SET nome = ?, updated_at = CURRENT_TIMESTAMP 
            WHERE id = ? AND user_id = ?
        ''', (novo_nome, projeto_id, user_id))
        conn.commit()

def delete_projeto(self, projeto_id, user_id):
    with self.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM projetos WHERE id = ? AND user_id = ?', (projeto_id, user_id))
        conn.commit()

def get_arquivos(self, projeto_id, user_id):
    with self.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT caminho, conteudo, created_at, updated_at 
            FROM arquivos 
            WHERE projeto_id = ? AND user_id = ?
        ''', (projeto_id, user_id))
        return [dict(row) for row in cursor.fetchall()]

def get_arquivo(self, projeto_id, user_id, caminho):
    with self.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT conteudo FROM arquivos 
            WHERE projeto_id = ? AND user_id = ? AND caminho = ?
        ''', (projeto_id, user_id, caminho))
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
        conn.commit()

def delete_arquivo(self, projeto_id, user_id, caminho):
    with self.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            DELETE FROM arquivos 
            WHERE projeto_id = ? AND user_id = ? AND caminho = ?
        ''', (projeto_id, user_id, caminho))
        conn.commit()

def get_pastas(self, projeto_id, user_id):
    with self.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT nome FROM pastas 
            WHERE projeto_id = ? AND user_id = ?
        ''', (projeto_id, user_id))
        return [dict(row) for row in cursor.fetchall()]

def create_pasta(self, projeto_id, user_id, nome_pasta):
    with self.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO pastas (projeto_id, user_id, nome) 
            VALUES (?, ?, ?)
        ''', (projeto_id, user_id, nome_pasta))
        conn.commit()

def delete_pasta(self, projeto_id, user_id, nome_pasta):
    with self.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            DELETE FROM pastas 
            WHERE projeto_id = ? AND user_id = ? AND nome = ?
        ''', (projeto_id, user_id, nome_pasta))
        conn.commit()

# ========== OPERAÇÕES DO CHAT ==========

def get_chats(self, user_id):
    """Obtém todos os chats do usuário"""
    with self.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, titulo, created_at, updated_at 
            FROM chats 
            WHERE user_id = ? 
            ORDER BY updated_at DESC
        ''', (user_id,))
        return [dict(row) for row in cursor.fetchall()]

def create_chat(self, user_id, titulo='Nova Conversa'):
    """Cria um novo chat"""
    with self.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO chats (user_id, titulo) 
            VALUES (?, ?)
        ''', (user_id, titulo))
        return cursor.lastrowid

def delete_chat(self, chat_id, user_id):
    """Deleta um chat e todas suas mensagens"""
    with self.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM chats WHERE id = ? AND user_id = ?', (chat_id, user_id))

def get_mensagens_chat(self, chat_id, user_id):
    """Obtém todas as mensagens de um chat"""
    with self.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, role, content, created_at 
            FROM mensagens_chat 
            WHERE chat_id = ? AND user_id = ? 
            ORDER BY created_at ASC
        ''', (chat_id, user_id))
        return [dict(row) for row in cursor.fetchall()]

def save_mensagem(self, chat_id, user_id, role, content):
    """Salva uma mensagem no chat"""
    with self.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO mensagens_chat (chat_id, user_id, role, content) 
            VALUES (?, ?, ?, ?)
        ''', (chat_id, user_id, role, content))
        
        # Atualizar o updated_at do chat
        cursor.execute('''
            UPDATE chats SET updated_at = CURRENT_TIMESTAMP 
            WHERE id = ? AND user_id = ?
        ''', (chat_id, user_id))

def update_chat_titulo(self, chat_id, user_id, titulo):
    """Atualiza o título do chat baseado na primeira mensagem"""
    with self.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE chats SET titulo = ? 
            WHERE id = ? AND user_id = ?
        ''', (titulo[:50], chat_id, user_id))

def save_api_key(self, user_id, provider, api_key):
    """Salva a chave API do usuário"""
    with self.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO api_keys (user_id, provider, api_key) 
            VALUES (?, ?, ?)
            ON CONFLICT(user_id, provider) 
            DO UPDATE SET api_key = ?, updated_at = CURRENT_TIMESTAMP
        ''', (user_id, provider, api_key, api_key))

def get_api_key(self, user_id, provider):
    """Obtém a chave API do usuário"""
    with self.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT api_key FROM api_keys 
            WHERE user_id = ? AND provider = ?
        ''', (user_id, provider))
        row = cursor.fetchone()
        return row['api_key'] if row else None