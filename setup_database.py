import streamlit as st
import mysql.connector
from database import get_db_connection

def setup_database():
    """
    Configura as tabelas necessárias no banco de dados.
    """
    conn = get_db_connection()
    if not conn:
        st.error("Não foi possível conectar ao banco de dados.")
        return False
    
    try:
        cursor = conn.cursor()
        
        # 1. Criar tabela de configurações de usuário
        create_user_configs_table = """
        CREATE TABLE IF NOT EXISTS user_configs (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(255) NOT NULL,
            config_type VARCHAR(100) NOT NULL,
            config_value TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            UNIQUE KEY unique_user_config (username, config_type)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """
        
        # 2. Criar tabela de usuários (se não existir)
        create_users_table = """
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(255) NOT NULL UNIQUE,
            password_hash VARCHAR(255) NOT NULL,
            user_role ENUM('admin', 'player', 'agent') NOT NULL DEFAULT 'player',
            email VARCHAR(255),
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            last_login TIMESTAMP NULL,
            INDEX idx_username (username),
            INDEX idx_role (user_role)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """
        
        # 3. Criar tabela de configurações globais
        create_global_configs_table = """
        CREATE TABLE IF NOT EXISTS global_configs (
            id INT AUTO_INCREMENT PRIMARY KEY,
            config_key VARCHAR(100) NOT NULL UNIQUE,
            config_value TEXT,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """
        
        # Executar as criações
        st.info("Criando tabela de configurações de usuário...")
        cursor.execute(create_user_configs_table)
        
        st.info("Criando tabela de usuários...")
        cursor.execute(create_users_table)
        
        st.info("Criando tabela de configurações globais...")
        cursor.execute(create_global_configs_table)
        
        # Commit das alterações
        conn.commit()
        
        st.success("✅ Todas as tabelas foram criadas com sucesso!")
        
        # Verificar se as tabelas foram criadas
        cursor.execute("SHOW TABLES LIKE 'user_configs'")
        if cursor.fetchone():
            st.success("✅ Tabela 'user_configs' criada e verificada")
        
        cursor.execute("SHOW TABLES LIKE 'users'")
        if cursor.fetchone():
            st.success("✅ Tabela 'users' criada e verificada")
        
        cursor.execute("SHOW TABLES LIKE 'global_configs'")
        if cursor.fetchone():
            st.success("✅ Tabela 'global_configs' criada e verificada")
        
        return True
        
    except Exception as e:
        st.error(f"Erro ao configurar banco de dados: {e}")
        return False
    finally:
        conn.close()

def insert_sample_data():
    """
    Insere dados de exemplo nas tabelas.
    """
    conn = get_db_connection()
    if not conn:
        st.error("Não foi possível conectar ao banco de dados.")
        return False
    
    try:
        cursor = conn.cursor()
        
        # Inserir configurações globais de exemplo
        sample_global_configs = [
            ("app_name", "BPD - Sistema de Gestão", "Nome da aplicação"),
            ("default_period", "2", "Período padrão (0=Semana Atual, 1=Hoje, 2=Última semana, 3=Últimos 30 dias, 4=Mostrar tudo)"),
            ("default_currency", "Real (R$)", "Moeda padrão do sistema"),
            ("maintenance_mode", "false", "Modo de manutenção"),
        ]
        
        for config_key, config_value, description in sample_global_configs:
            cursor.execute("""
                INSERT IGNORE INTO global_configs (config_key, config_value, description) 
                VALUES (%s, %s, %s)
            """, (config_key, config_value, description))
        
        conn.commit()
        st.success("✅ Dados de exemplo inseridos com sucesso!")
        return True
        
    except Exception as e:
        st.error(f"Erro ao inserir dados de exemplo: {e}")
        return False
    finally:
        conn.close()

def main():
    st.title("🔧 Configuração do Banco de Dados")
    st.markdown("Este script configura as tabelas necessárias para o sistema BPD.")
    
    if st.button("🚀 Configurar Banco de Dados", type="primary"):
        with st.spinner("Configurando banco de dados..."):
            if setup_database():
                st.success("Banco de dados configurado com sucesso!")
                
                if st.button("📝 Inserir Dados de Exemplo"):
                    with st.spinner("Inserindo dados de exemplo..."):
                        insert_sample_data()
            else:
                st.error("Falha ao configurar banco de dados.")
    
    # Mostrar informações sobre as tabelas
    st.markdown("---")
    st.markdown("### 📋 Tabelas que serão criadas:")
    
    st.markdown("""
    **1. user_configs** - Configurações específicas de cada usuário
    - username: Nome do usuário
    - config_type: Tipo de configuração (ex: default_period_index)
    - config_value: Valor da configuração
    - created_at/updated_at: Timestamps
    
    **2. users** - Tabela de usuários do sistema
    - username: Nome de usuário único
    - password_hash: Hash da senha
    - user_role: Papel do usuário (admin/player/agent)
    - email: Email do usuário
    - is_active: Se o usuário está ativo
    - last_login: Último login
    
    **3. global_configs** - Configurações globais do sistema
    - config_key: Chave da configuração
    - config_value: Valor da configuração
    - description: Descrição da configuração
    """)

if __name__ == "__main__":
    main() 