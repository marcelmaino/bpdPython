import streamlit as st
import mysql.connector
import pandas as pd
from datetime import date

def get_db_connection():
    """
    Estabelece e retorna uma conexão com o banco de dados MySQL usando as credenciais do Streamlit secrets.
    """
    try:
        conn = mysql.connector.connect(
            host=st.secrets["mysql"]["host"],
            user=st.secrets["mysql"]["user"],
            password=st.secrets["mysql"]["password"],
            database=st.secrets["mysql"]["database"],
            port=st.secrets["mysql"]["port"]
        )
        return conn
    except Exception as e:
        st.error(f"Erro ao conectar ao banco de dados: {e}")
        return None

# @st.cache_data(ttl=3600) # Cache por 1 hora - Temporariamente desativado para depuração
def load_data(username: str = None, user_role: str = None, start_date: date = None, end_date: date = None):
    """
    Carrega os dados da tabela 'bpd' do MySQL para um DataFrame Pandas.
    Realiza limpeza inicial dos dados e filtra por usuário/papel e intervalo de datas se fornecido.
    """
    conn = get_db_connection()
    if conn:
        try:
            # Atenção: Colunas com espaços nos nomes devem ser envolvidas em crases (`)
            query = """
            SELECT
                `linha_id`, `dia`, `reference`, `share`, `moeda`, `upline`,
                `club`, `playerID`, `playerName`, `agentName`, `agentId`,
                `superAgentName`, `superagentId`, `localWins`, `localFee`,
                `hands`, `dolarWins`, `dolarFee`, `dolarRakeback`,
                `dolarRebate`, `realWins`, `realFee`, `realRakeback`,
                `realRebate`, `realAgentSett`, `dolarAgentSett`,
                `realRevShare`, `realBPFProfit`, `deal`, `rebate`
            FROM bpd
            """
            
            where_clauses = []
            params = []

            if user_role == 'Jogador' and username:
                where_clauses.append(" playerName = %s")
                params.append(username)
            
            if start_date and end_date:
                where_clauses.append(" STR_TO_DATE(dia, '%d/%b/%y') BETWEEN %s AND %s")
                params.append(start_date)
                params.append(end_date)

            if where_clauses:
                query += " WHERE " + " AND ".join(where_clauses)

            df = pd.read_sql(query, conn, params=params)

            # Limpeza inicial: remover espaços dos nomes das colunas
            # Esta linha é crucial para que o pandas possa acessar as colunas sem o espaço
            df.columns = df.columns.str.strip()

            # Converter a coluna 'dia' para datetime usando o formato correto
            df['dia'] = pd.to_datetime(df['dia'], format='%d/%b/%y', errors='coerce')

            # Remover linhas com datas inválidas (NaT) na coluna 'dia'
            df.dropna(subset=['dia'], inplace=True)

            return df
        except Exception as e:
            st.error(f"Erro ao carregar dados do banco de dados: {e}")
            return pd.DataFrame() # Retorna um DataFrame vazio em caso de erro
        finally:
            conn.close()
    return pd.DataFrame() # Retorna um DataFrame vazio se a conexão falhar

def save_user_config(username: str, config_type: str, config_value: str):
    """
    Salva as configurações específicas do usuário no banco de dados.
    """
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            
            # Cria a tabela de configurações se não existir
            create_table_query = """
            CREATE TABLE IF NOT EXISTS user_configs (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(255) NOT NULL,
                config_type VARCHAR(100) NOT NULL,
                config_value TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                UNIQUE KEY unique_user_config (username, config_type)
            )
            """
            cursor.execute(create_table_query)
            
            # Insere ou atualiza a configuração
            query = """
            INSERT INTO user_configs (username, config_type, config_value) 
            VALUES (%s, %s, %s) 
            ON DUPLICATE KEY UPDATE config_value = %s, updated_at = CURRENT_TIMESTAMP
            """
            cursor.execute(query, (username, config_type, config_value, config_value))
            conn.commit()
            return True
        except Exception as e:
            st.error(f"Erro ao salvar configuração do usuário: {e}")
            return False
        finally:
            conn.close()
    return False

def load_user_config(username: str, config_type: str, default_value=None):
    """
    Carrega uma configuração específica do usuário do banco de dados.
    """
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            query = "SELECT config_value FROM user_configs WHERE username = %s AND config_type = %s"
            cursor.execute(query, (username, config_type))
            result = cursor.fetchone()
            
            if result:
                return result[0]
            else:
                return default_value
        except Exception as e:
            st.error(f"Erro ao carregar configuração do usuário: {e}")
            return default_value
        finally:
            conn.close()
    return default_value

def save_config(config_data):
    """
    Salva as configurações no banco de dados.
    """
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            # Exemplo: Inserir ou atualizar uma configuração simples
            # Adapte esta lógica para a sua tabela de configuração
            query = "INSERT INTO config (key_name, value) VALUES (%s, %s) ON DUPLICATE KEY UPDATE value = %s"
            for key, value in config_data.items():
                cursor.execute(query, (key, str(value), str(value)))
            conn.commit()
            st.success("Configurações salvas com sucesso!")
        except Exception as e:
            st.error(f"Erro ao salvar configurações: {e}")
        finally:
            conn.close()

def load_config():
    """
    Carrega as configurações do banco de dados.
    """
    conn = get_db_connection()
    config = {}
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            query = "SELECT key_name, value FROM config"
            cursor.execute(query)
            for row in cursor.fetchall():
                config[row['key_name']] = row['value']
        except Exception as e:
            st.error(f"Erro ao carregar configurações: {e}")
        finally:
            conn.close()
    return config

def get_all_players(conn):
    """
    Retorna uma lista de todos os playerNames distintos da tabela bpd.
    """
    if conn:
        try:
            cursor = conn.cursor()
            query = "SELECT DISTINCT playerName FROM bpd"
            cursor.execute(query)
            players = [row[0] for row in cursor.fetchall()]
            return players
        except Exception as e:
            st.error(f"Erro ao buscar players: {e}")
            return []
    return []

def get_all_agents(conn):
    """
    Retorna uma lista de todos os agentNames distintos da tabela bpd.
    """
    if conn:
        try:
            cursor = conn.cursor()
            query = "SELECT DISTINCT agentName FROM bpd"
            cursor.execute(query)
            agents = [row[0] for row in cursor.fetchall()]
            return agents
        except Exception as e:
            st.error(f"Erro ao buscar agents: {e}")
            return []
    return []

def get_all_superagents(conn):
    """
    Retorna uma lista de todos os superAgentNames distintos da tabela bpd.
    """
    if conn:
        try:
            cursor = conn.cursor()
            query = "SELECT DISTINCT superAgentName FROM bpd"
            cursor.execute(query)
            superagents = [row[0] for row in cursor.fetchall()]
            return superagents
        except Exception as e:
            st.error(f"Erro ao buscar superagents: {e}")
            return []
    return []

def load_user_names():
    """
    Carrega apenas os nomes de jogadores e agentes da tabela bpd para uso no login.
    """
    conn = get_db_connection()
    player_names = []
    agent_names = []
    if conn:
        try:
            cursor = conn.cursor()
            # Busca playerNames
            cursor.execute("SELECT DISTINCT playerName FROM bpd")
            player_names = [row[0] for row in cursor.fetchall() if row[0] is not None]
            # Busca agentNames
            cursor.execute("SELECT DISTINCT agentName FROM bpd")
            agent_names = [row[0] for row in cursor.fetchall() if row[0] is not None]
        except Exception as e:
            st.error(f"Erro ao carregar nomes de usuários para login: {e}")
        finally:
            conn.close()
    return player_names, agent_names

def get_user_info(username: str):
    """
    Busca informações do usuário na tabela users.
    """
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            query = "SELECT username, email, password, user_type FROM users WHERE username = %s"
            cursor.execute(query, (username,))
            user_info = cursor.fetchone()
            return user_info
        except Exception as e:
            st.error(f"Erro ao buscar informações do usuário: {e}")
            return None
        finally:
            conn.close()
    return None

def update_user_password(username: str, new_password: str):
    """
    Atualiza a senha do usuário na tabela users.
    """
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            query = "UPDATE users SET password = %s WHERE username = %s"
            cursor.execute(query, (new_password, username))
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            st.error(f"Erro ao atualizar senha do usuário: {e}")
            return False
        finally:
            conn.close()
    return False

def update_user_email(username: str, email: str):
    """
    Atualiza o e-mail do usuário na tabela users.
    """
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            query = "UPDATE users SET email = %s WHERE username = %s"
            cursor.execute(query, (email, username))
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            st.error(f"Erro ao atualizar e-mail do usuário: {e}")
            return False
        finally:
            conn.close()
    return False

def create_user_if_not_exists(username: str, email: str = None, password: str = None, role: str = 'player'):
    """
    Cria um usuário na tabela users se ele não existir.
    """
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            
            # Verificar se o usuário já existe
            cursor.execute("SELECT username FROM users WHERE username = %s", (username,))
            if cursor.fetchone():
                return True  # Usuário já existe
            
            # Criar novo usuário
            query = """
            INSERT INTO users (username, email, password, user_type) 
            VALUES (%s, %s, %s, %s)
            """
            cursor.execute(query, (username, email, password, role))
            conn.commit()
            return True
            
        except Exception as e:
            st.error(f"Erro ao criar usuário: {e}")
            return False
        finally:
            conn.close()
    return False

def load_all_users():
    """
    Carrega todos os usuários da tabela users do banco de dados.
    Retorna um DataFrame com username, password, user_type e email.
    """
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            query = "SELECT username, password, user_type, email FROM users"
            cursor.execute(query)
            users = cursor.fetchall()
            
            # Converte para DataFrame
            users_df = pd.DataFrame(users)
            
            # Mapeia user_type para role (admin -> Admin, player -> Jogador)
            users_df['role'] = users_df['user_type'].map({'admin': 'Admin', 'player': 'Jogador'})
            
            return users_df
        except Exception as e:
            st.error(f"Erro ao carregar usuários do banco: {e}")
            return pd.DataFrame()
        finally:
            conn.close()
    return pd.DataFrame()