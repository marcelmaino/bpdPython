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
                where_clauses.append(" dia BETWEEN %s AND %s")
                params.append(start_date)
                params.append(end_date)

            if where_clauses:
                query += " WHERE " + " AND ".join(where_clauses)

            df = pd.read_sql(query, conn, params=params)

            # Limpeza inicial: remover espaços dos nomes das colunas
            # Esta linha é crucial para que o pandas possa acessar as colunas sem o espaço
            df.columns = df.columns.str.strip()

            # Converter a coluna 'dia' para datetime
            df['dia'] = pd.to_datetime(df['dia'], errors='coerce')

            # Remover linhas com datas inválidas (NaT) na coluna 'dia'
            df.dropna(subset=['dia'], inplace=True)

            return df
        except Exception as e:
            st.error(f"Erro ao carregar dados do banco de dados: {e}")
            return pd.DataFrame() # Retorna um DataFrame vazio em caso de erro
        finally:
            conn.close()
    return pd.DataFrame() # Retorna um DataFrame vazio se a conexão falhar

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