import streamlit as st
from database import get_db_connection

def check_database_structure():
    """
    Verifica a estrutura atual do banco de dados.
    """
    conn = get_db_connection()
    if not conn:
        st.error("Não foi possível conectar ao banco de dados.")
        return False
    
    try:
        cursor = conn.cursor()
        
        # Listar todas as tabelas
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        
        st.markdown("### 📋 Tabelas existentes no banco:")
        for table in tables:
            table_name = table[0]
            st.write(f"- **{table_name}**")
            
            # Mostrar estrutura da tabela
            cursor.execute(f"DESCRIBE {table_name}")
            columns = cursor.fetchall()
            
            with st.expander(f"Estrutura da tabela {table_name}", expanded=False):
                for col in columns:
                    st.write(f"  - {col[0]} ({col[1]}) - {col[2]}")
        
        # Verificar especificamente a tabela users
        cursor.execute("SHOW TABLES LIKE 'users'")
        users_exists = cursor.fetchone()
        
        if users_exists:
            st.success("✅ Tabela 'users' já existe!")
            
            # Verificar estrutura da tabela users
            cursor.execute("DESCRIBE users")
            users_columns = cursor.fetchall()
            
            st.markdown("### 📊 Estrutura da tabela 'users':")
            for col in users_columns:
                st.write(f"- **{col[0]}**: {col[1]} - {col[2]}")
        else:
            st.warning("⚠️ Tabela 'users' não existe.")
        
        # Verificar se user_configs existe
        cursor.execute("SHOW TABLES LIKE 'user_configs'")
        configs_exists = cursor.fetchone()
        
        if configs_exists:
            st.success("✅ Tabela 'user_configs' já existe!")
        else:
            st.warning("⚠️ Tabela 'user_configs' não existe.")
        
        return True
        
    except Exception as e:
        st.error(f"Erro ao verificar banco de dados: {e}")
        return False
    finally:
        conn.close()

def create_user_configs_table():
    """
    Cria apenas a tabela user_configs se ela não existir.
    """
    conn = get_db_connection()
    if not conn:
        st.error("Não foi possível conectar ao banco de dados.")
        return False
    
    try:
        cursor = conn.cursor()
        
        # Verificar se a tabela já existe
        cursor.execute("SHOW TABLES LIKE 'user_configs'")
        if cursor.fetchone():
            st.info("Tabela 'user_configs' já existe!")
            return True
        
        # Criar tabela de configurações de usuário
        create_table_query = """
        CREATE TABLE user_configs (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(255) NOT NULL,
            config_type VARCHAR(100) NOT NULL,
            config_value TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            UNIQUE KEY unique_user_config (username, config_type)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """
        
        cursor.execute(create_table_query)
        conn.commit()
        
        st.success("✅ Tabela 'user_configs' criada com sucesso!")
        return True
        
    except Exception as e:
        st.error(f"Erro ao criar tabela: {e}")
        return False
    finally:
        conn.close()

def main():
    st.title("🔍 Verificação do Banco de Dados")
    st.markdown("Este script verifica a estrutura atual do banco e cria apenas o necessário.")
    
    if st.button("🔍 Verificar Estrutura", type="primary"):
        with st.spinner("Verificando banco de dados..."):
            check_database_structure()
    
    st.markdown("---")
    
    if st.button("➕ Criar Tabela user_configs", type="secondary"):
        with st.spinner("Criando tabela..."):
            if create_user_configs_table():
                st.success("Tabela criada com sucesso! Agora você pode usar as configurações.")
            else:
                st.error("Falha ao criar tabela.")

if __name__ == "__main__":
    main() 