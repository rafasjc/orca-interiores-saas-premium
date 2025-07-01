"""
Sistema de Autenticação Limpo - Orca Interiores
Versão sem credenciais expostas na interface
"""

import sqlite3
import hashlib
import os
from datetime import datetime, timedelta
from typing import Dict, Optional

class AuthManager:
    """Gerenciador de autenticação limpo e seguro"""
    
    def __init__(self, db_path: str = "usuarios_limpo.db"):
        """Inicializa o gerenciador de autenticação"""
        self.db_path = db_path
        self.criar_banco()
        self.criar_usuarios_demo()
    
    def criar_banco(self):
        """Cria banco de dados de usuários"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tabela de usuários
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                senha_hash TEXT NOT NULL,
                plano TEXT NOT NULL DEFAULT 'basico',
                ativo BOOLEAN DEFAULT 1,
                data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ultimo_login TIMESTAMP,
                orcamentos_usados INTEGER DEFAULT 0,
                limite_orcamentos INTEGER DEFAULT 5
            )
        ''')
        
        # Tabela de sessões
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario_id INTEGER,
                token TEXT UNIQUE,
                data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                data_expiracao TIMESTAMP,
                ativo BOOLEAN DEFAULT 1,
                FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
            )
        ''')
        
        # Tabela de logs
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS logs_acesso (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario_id INTEGER,
                acao TEXT,
                ip_address TEXT,
                user_agent TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def criar_usuarios_demo(self):
        """Cria usuários demo sem expor credenciais"""
        
        usuarios_demo = [
            {
                'nome': 'Usuário Demo',
                'email': 'demo@orcainteriores.com',
                'senha': 'demo123',
                'plano': 'profissional',
                'limite_orcamentos': 50
            },
            {
                'nome': 'Arquiteto Teste',
                'email': 'arquiteto@teste.com',
                'senha': 'arq123',
                'plano': 'basico',
                'limite_orcamentos': 5
            },
            {
                'nome': 'Marceneiro Teste',
                'email': 'marceneiro@teste.com',
                'senha': 'marc123',
                'plano': 'empresarial',
                'limite_orcamentos': 999999
            }
        ]
        
        for usuario in usuarios_demo:
            self.criar_usuario(
                nome=usuario['nome'],
                email=usuario['email'],
                senha=usuario['senha'],
                plano=usuario['plano'],
                limite_orcamentos=usuario['limite_orcamentos']
            )
    
    def hash_senha(self, senha: str) -> str:
        """Gera hash seguro da senha"""
        return hashlib.sha256(senha.encode()).hexdigest()
    
    def criar_usuario(self, nome: str, email: str, senha: str, 
                     plano: str = 'basico', limite_orcamentos: int = 5) -> bool:
        """Cria novo usuário"""
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Verificar se email já existe
            cursor.execute('SELECT id FROM usuarios WHERE email = ?', (email,))
            if cursor.fetchone():
                conn.close()
                return False  # Email já existe
            
            # Inserir usuário
            senha_hash = self.hash_senha(senha)
            cursor.execute('''
                INSERT INTO usuarios (nome, email, senha_hash, plano, limite_orcamentos)
                VALUES (?, ?, ?, ?, ?)
            ''', (nome, email, senha_hash, plano, limite_orcamentos))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Erro ao criar usuário: {e}")
            return False
    
    def fazer_login(self, email: str, senha: str) -> Optional[Dict]:
        """Realiza login do usuário"""
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Buscar usuário
            senha_hash = self.hash_senha(senha)
            cursor.execute('''
                SELECT id, nome, email, plano, ativo, orcamentos_usados, limite_orcamentos
                FROM usuarios 
                WHERE email = ? AND senha_hash = ? AND ativo = 1
            ''', (email, senha_hash))
            
            usuario = cursor.fetchone()
            
            if usuario:
                # Atualizar último login
                cursor.execute('''
                    UPDATE usuarios 
                    SET ultimo_login = CURRENT_TIMESTAMP 
                    WHERE id = ?
                ''', (usuario[0],))
                
                # Log de acesso
                cursor.execute('''
                    INSERT INTO logs_acesso (usuario_id, acao)
                    VALUES (?, 'login')
                ''', (usuario[0],))
                
                conn.commit()
                conn.close()
                
                return {
                    'id': usuario[0],
                    'nome': usuario[1],
                    'email': usuario[2],
                    'plano': usuario[3],
                    'ativo': usuario[4],
                    'orcamentos_usados': usuario[5],
                    'limite_orcamentos': usuario[6]
                }
            
            conn.close()
            return None
            
        except Exception as e:
            print(f"Erro no login: {e}")
            return None
    
    def verificar_limite_orcamentos(self, usuario_id: int) -> bool:
        """Verifica se usuário pode fazer mais orçamentos"""
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT orcamentos_usados, limite_orcamentos
                FROM usuarios 
                WHERE id = ?
            ''', (usuario_id,))
            
            resultado = cursor.fetchone()
            conn.close()
            
            if resultado:
                usados, limite = resultado
                return usados < limite
            
            return False
            
        except Exception as e:
            print(f"Erro ao verificar limite: {e}")
            return False
    
    def incrementar_orcamento(self, usuario_id: int) -> bool:
        """Incrementa contador de orçamentos do usuário"""
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE usuarios 
                SET orcamentos_usados = orcamentos_usados + 1
                WHERE id = ?
            ''', (usuario_id,))
            
            # Log da ação
            cursor.execute('''
                INSERT INTO logs_acesso (usuario_id, acao)
                VALUES (?, 'orcamento_gerado')
            ''', (usuario_id,))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Erro ao incrementar orçamento: {e}")
            return False
    
    def obter_estatisticas_usuario(self, usuario_id: int) -> Dict:
        """Obtém estatísticas do usuário"""
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Dados básicos
            cursor.execute('''
                SELECT nome, email, plano, data_criacao, ultimo_login,
                       orcamentos_usados, limite_orcamentos
                FROM usuarios 
                WHERE id = ?
            ''', (usuario_id,))
            
            usuario = cursor.fetchone()
            
            if not usuario:
                conn.close()
                return {}
            
            # Contagem de logins
            cursor.execute('''
                SELECT COUNT(*) FROM logs_acesso 
                WHERE usuario_id = ? AND acao = 'login'
            ''', (usuario_id,))
            
            total_logins = cursor.fetchone()[0]
            
            # Último orçamento
            cursor.execute('''
                SELECT timestamp FROM logs_acesso 
                WHERE usuario_id = ? AND acao = 'orcamento_gerado'
                ORDER BY timestamp DESC LIMIT 1
            ''', (usuario_id,))
            
            ultimo_orcamento = cursor.fetchone()
            
            conn.close()
            
            return {
                'nome': usuario[0],
                'email': usuario[1],
                'plano': usuario[2],
                'data_criacao': usuario[3],
                'ultimo_login': usuario[4],
                'orcamentos_usados': usuario[5],
                'limite_orcamentos': usuario[6],
                'total_logins': total_logins,
                'ultimo_orcamento': ultimo_orcamento[0] if ultimo_orcamento else None,
                'percentual_uso': (usuario[5] / usuario[6] * 100) if usuario[6] > 0 else 0
            }
            
        except Exception as e:
            print(f"Erro ao obter estatísticas: {e}")
            return {}
    
    def listar_usuarios(self) -> list:
        """Lista todos os usuários (admin)"""
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, nome, email, plano, ativo, data_criacao,
                       orcamentos_usados, limite_orcamentos
                FROM usuarios 
                ORDER BY data_criacao DESC
            ''')
            
            usuarios = cursor.fetchall()
            conn.close()
            
            return [
                {
                    'id': u[0],
                    'nome': u[1],
                    'email': u[2],
                    'plano': u[3],
                    'ativo': u[4],
                    'data_criacao': u[5],
                    'orcamentos_usados': u[6],
                    'limite_orcamentos': u[7]
                }
                for u in usuarios
            ]
            
        except Exception as e:
            print(f"Erro ao listar usuários: {e}")
            return []
    
    def alterar_plano(self, usuario_id: int, novo_plano: str) -> bool:
        """Altera plano do usuário"""
        
        planos_limites = {
            'basico': 5,
            'profissional': 50,
            'empresarial': 999999
        }
        
        if novo_plano not in planos_limites:
            return False
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE usuarios 
                SET plano = ?, limite_orcamentos = ?
                WHERE id = ?
            ''', (novo_plano, planos_limites[novo_plano], usuario_id))
            
            # Log da alteração
            cursor.execute('''
                INSERT INTO logs_acesso (usuario_id, acao)
                VALUES (?, ?)
            ''', (usuario_id, f'plano_alterado_para_{novo_plano}'))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Erro ao alterar plano: {e}")
            return False
    
    def resetar_contador_orcamentos(self, usuario_id: int) -> bool:
        """Reseta contador de orçamentos (renovação mensal)"""
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE usuarios 
                SET orcamentos_usados = 0
                WHERE id = ?
            ''', (usuario_id,))
            
            # Log da ação
            cursor.execute('''
                INSERT INTO logs_acesso (usuario_id, acao)
                VALUES (?, 'contador_resetado')
            ''', (usuario_id,))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Erro ao resetar contador: {e}")
            return False
    
    def obter_logs_acesso(self, usuario_id: int = None, limite: int = 100) -> list:
        """Obtém logs de acesso"""
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            if usuario_id:
                cursor.execute('''
                    SELECT l.timestamp, l.acao, u.nome, u.email
                    FROM logs_acesso l
                    JOIN usuarios u ON l.usuario_id = u.id
                    WHERE l.usuario_id = ?
                    ORDER BY l.timestamp DESC
                    LIMIT ?
                ''', (usuario_id, limite))
            else:
                cursor.execute('''
                    SELECT l.timestamp, l.acao, u.nome, u.email
                    FROM logs_acesso l
                    JOIN usuarios u ON l.usuario_id = u.id
                    ORDER BY l.timestamp DESC
                    LIMIT ?
                ''', (limite,))
            
            logs = cursor.fetchall()
            conn.close()
            
            return [
                {
                    'timestamp': log[0],
                    'acao': log[1],
                    'nome': log[2],
                    'email': log[3]
                }
                for log in logs
            ]
            
        except Exception as e:
            print(f"Erro ao obter logs: {e}")
            return []

# Exemplo de uso
if __name__ == "__main__":
    # Criar gerenciador
    auth = AuthManager()
    
    print("✅ Sistema de autenticação limpo criado!")
    print("📊 Usuários demo disponíveis:")
    
    usuarios = auth.listar_usuarios()
    for usuario in usuarios:
        print(f"  - {usuario['nome']} ({usuario['email']}) - Plano: {usuario['plano']}")
    
    # Teste de login
    print("\n🧪 Testando login demo...")
    usuario = auth.fazer_login("demo@orcainteriores.com", "demo123")
    
    if usuario:
        print(f"✅ Login bem-sucedido: {usuario['nome']}")
        print(f"📊 Orçamentos: {usuario['orcamentos_usados']}/{usuario['limite_orcamentos']}")
    else:
        print("❌ Falha no login")

