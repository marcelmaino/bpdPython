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