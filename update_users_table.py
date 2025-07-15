import streamlit as st
from database import get_db_connection

def check_and_update_users_table():
    """
    Verifica a estrutura da tabela users e adiciona a coluna email se necessário.
    """
    conn = get_db_connection()
    if not conn:
        st.error("Não foi possível conectar ao banco de dados.")
        return False
    
    try:
        cursor = conn.cursor()
        
        # Verificar se a tabela users existe
        cursor.execute("SHOW TABLES LIKE 'users'")
        if not cursor.fetchone():
            st.error("Tabela 'users' não existe!")
            return False
        
        # Verificar estrutura atual da tabela users
        cursor.execute("DESCRIBE users")
        columns = cursor.fetchall()
        
        st.markdown("### 📊 Estrutura atual da tabela 'users':")
        column_names = []
        for col in columns:
            column_name = col[0]
            column_type = col[1]
            column_null = col[2]
            column_key = col[3]
            column_default = col[4]
            column_extra = col[5]
            
            st.write(f"- **{column_name}**: {column_type} - {column_null} - {column_key} - {column_default} - {column_extra}")
            column_names.append(column_name)
        
        # Verificar se a coluna email já existe
        if 'email' in column_names:
            st.success("✅ Coluna 'email' já existe na tabela users!")
            return True
        else:
            st.warning("⚠️ Coluna 'email' não existe. Vamos adicioná-la...")
            
            # Adicionar coluna email
            try:
                alter_query = "ALTER TABLE users ADD COLUMN email VARCHAR(255) NULL AFTER username"
                cursor.execute(alter_query)
                conn.commit()
                st.success("✅ Coluna 'email' adicionada com sucesso!")
                
                # Verificar estrutura atualizada
                cursor.execute("DESCRIBE users")
                updated_columns = cursor.fetchall()
                
                st.markdown("### 📊 Nova estrutura da tabela 'users':")
                for col in updated_columns:
                    st.write(f"- **{col[0]}**: {col[1]} - {col[2]} - {col[3]} - {col[4]} - {col[5]}")
                
                return True
                
            except Exception as e:
                st.error(f"Erro ao adicionar coluna email: {e}")
                return False
        
    except Exception as e:
        st.error(f"Erro ao verificar tabela users: {e}")
        return False
    finally:
        conn.close()

def insert_sample_user():
    """
    Insere um usuário de exemplo para teste.
    """
    conn = get_db_connection()
    if not conn:
        st.error("Não foi possível conectar ao banco de dados.")
        return False
    
    try:
        cursor = conn.cursor()
        
        # Inserir usuário de exemplo
        sample_user_query = """
        INSERT IGNORE INTO users (username, email, password_hash, user_role) 
        VALUES ('admin', 'admin@bpd.com', 'admin123', 'admin')
        """
        cursor.execute(sample_user_query)
        conn.commit()
        
        st.success("✅ Usuário de exemplo inserido com sucesso!")
        return True
        
    except Exception as e:
        st.error(f"Erro ao inserir usuário de exemplo: {e}")
        return False
    finally:
        conn.close()

def main():
    st.title("🔧 Atualizar Tabela Users")
    st.markdown("Este script verifica e atualiza a tabela users com a coluna email.")
    
    if st.button("🔍 Verificar e Atualizar Tabela", type="primary"):
        with st.spinner("Verificando e atualizando tabela users..."):
            if check_and_update_users_table():
                st.success("Tabela users verificada e atualizada com sucesso!")
                
                if st.button("👤 Inserir Usuário de Exemplo"):
                    with st.spinner("Inserindo usuário de exemplo..."):
                        insert_sample_user()
            else:
                st.error("Falha ao verificar/atualizar tabela users.")

if __name__ == "__main__":
    main() 