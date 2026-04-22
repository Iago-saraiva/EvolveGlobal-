import hashlib
import secrets
from datetime import datetime, timedelta

class AuthManager:
    def __init__(self, db):
        self.db = db
    
    def hash_password(self, password):
        """Cria hash da senha usando SHA-256 + salt"""
        salt = secrets.token_hex(16)
        hash_obj = hashlib.sha256((password + salt).encode())
        return f"{salt}:{hash_obj.hexdigest()}"
    
    def verify_password(self, password, stored_hash):
        """Verifica se a senha corresponde ao hash armazenado"""
        try:
            salt, hash_value = stored_hash.split(':')
            hash_obj = hashlib.sha256((password + salt).encode())
            return hash_obj.hexdigest() == hash_value
        except:
            return False
    
    def create_user(self, nome, email, senha):
        """Cria um novo usuário com senha hash"""
        senha_hash = self.hash_password(senha)
        return self.db.create_user(nome, email, senha_hash)
    
    def authenticate_user(self, email, senha):
        """Autentica um usuário e retorna seus dados se bem-sucedido"""
        user = self.db.get_user_by_email(email)
        
        if user and self.verify_password(senha, user['senha_hash']):
            return {
                'id': user['id'],
                'nome': user['nome'],
                'email': user['email']
            }
        return None
    
    def authenticate_user_by_id(self, user_id, senha):
        """Autentica um usuário pelo ID"""
        user = self.db.get_user_by_id(user_id)
        
        if user and self.verify_password(senha, user['senha_hash']):
            return True
        return False
    
    def generate_token(self, user_id):
        """Gera um token de autenticação"""
        token = secrets.token_urlsafe(32)
        expires_at = datetime.now() + timedelta(days=7)  # Token expira em 7 dias
        self.db.save_token(token, user_id, expires_at)
        return token
    
    def verify_token(self, token):
        """Verifica se o token é válido e não expirou"""
        token_data = self.db.get_token(token)
        
        if not token_data:
            return False
        
        # Verificar expiração
        if token_data['expires_at']:
            expires_at = datetime.fromisoformat(token_data['expires_at'])
            if datetime.now() > expires_at:
                return False
        
        return True
    
    def get_user_id_from_token(self, token):
        """Obtém o ID do usuário a partir do token"""
        token_data = self.db.get_token(token)
        return token_data['user_id'] if token_data else None
    
    def revoke_token(self, token):
        """Revoga um token"""
        self.db.revoke_token(token)
    
    def update_password(self, user_id, new_password):
        """Atualiza a senha do usuário"""
        new_hash = self.hash_password(new_password)
        self.db.update_password(user_id, new_hash)
        # Revoga todos os tokens após mudança de senha (opcional)
        # self.db.revoke_all_user_tokens(user_id)