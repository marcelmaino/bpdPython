import streamlit as st
import mysql.connector
import os

def load_secrets_for_test():
    secrets_path = os.path.join(os.path.dirname(__file__), '.streamlit', 'secrets.toml')
    secrets = {}
    try:
        with open(secrets_path, 'r') as f:
            content = f.read()
            lines = content.split('\n')
            current_section = None
            for line in lines:
                line = line.strip()
                if line.startswith('[') and line.endswith(']'):
                    current_section = line[1:-1]
                    secrets[current_section] = {}
                elif current_section and '=' in line:
                    key, value = line.split('=', 1)
                    secrets[current_section][key.strip()] = value.strip().strip('\'\"')
    except FileNotFoundError:
        print(f"Erro: Arquivo secrets.toml não encontrado em {secrets_path}")
        return None
    except Exception as e:
        print(f"Erro ao ler secrets.toml: {e}")
        return None
    return secrets

class MockSecrets:
    def __init__(self):
        self._data = load_secrets_for_test()

    def __getitem__(self, key):
        if self._data is None:
            raise KeyError(f"Secrets not loaded. Check secrets.toml path and content.")
        return self._data[key]

st.secrets = MockSecrets()

def test_db_query_and_returned_columns():
    print("\n--- Testando Query SQL e Colunas Retornadas ---")
    conn = None
    try:
        conn = mysql.connector.connect(
            host=st.secrets["mysql"]["host"],
            user=st.secrets["mysql"]["user"],
            password=st.secrets["mysql"]["password"],
            database=st.secrets["mysql"]["database"],
            port=st.secrets["mysql"]["port"]
        )
        if conn.is_connected():
            print("Conexão com o banco de dados estabelecida com sucesso!")
            cursor = conn.cursor()

            query = """
            SELECT
                `linha_id`, `dia`, `reference`, `share`, `moeda`, `upline`,
                `club`, `playerID`, `playerName`, `agentName`, `agentId`,
                `superAgentName`, `superagentId`, `localWins`, `localFee`,
                `hands`, `dolarWins`, `dolarFee`, `dolarRakeback`,
                `dolarRebate`, `realWins`, `realFee`, `realRakeback`,
                `realRebate`, `realAgentSett`, `dolarAgentSett`,
                `realRevShare`, `realBPFProfit`, `deal`, `rebate`
            FROM bpd;
            """
            print(f"\nExecutando a query:\n{query}")

            cursor.execute(query)

            print("\nColunas retornadas pelo cursor (description):")
            if cursor.description:
                for column in cursor.description:
                    print(f"- '{column[0]}'")
            else:
                print("Nenhuma coluna retornada (tabela vazia ou erro na query).")

            cursor.close()
        else:
            print("Erro: Não foi possível conectar ao banco de dados.")
    except KeyError as e:
        print(f"Erro: Credencial MySQL faltando ou secrets.toml mal formatado: {e}")
        print("Por favor, verifique se .streamlit/secrets.toml contém as chaves [mysql], host, user, password, database e port.")
    except mysql.connector.Error as err:
        print(f"Erro de conexão com o MySQL: {err}")
        print("Verifique as credenciais no secrets.toml e se o servidor MySQL está acessível.")
    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")
    finally:
        if conn:
            conn.close()
            print("Conexão fechada.")

def show_bpd_count_and_sample():
    import mysql.connector
    conn = None
    try:
        conn = mysql.connector.connect(
            host=st.secrets["mysql"]["host"],
            user=st.secrets["mysql"]["user"],
            password=st.secrets["mysql"]["password"],
            database=st.secrets["mysql"]["database"],
            port=st.secrets["mysql"]["port"]
        )
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM bpd")
        count = cursor.fetchone()[0]
        print(f"\nTotal de linhas na tabela bpd: {count}")
        if count > 0:
            cursor.execute("SELECT * FROM bpd LIMIT 5")
            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            print("\nPrimeiras linhas:")
            print(columns)
            for row in rows:
                print(row)
        cursor.close()
    except Exception as e:
        print(f"Erro ao consultar tabela bpd: {e}")
    finally:
        if conn:
            conn.close()

def check_date_range():
    import mysql.connector
    from datetime import datetime, timedelta
    conn = None
    try:
        conn = mysql.connector.connect(
            host=st.secrets["mysql"]["host"],
            user=st.secrets["mysql"]["user"],
            password=st.secrets["mysql"]["password"],
            database=st.secrets["mysql"]["database"],
            port=st.secrets["mysql"]["port"]
        )
        cursor = conn.cursor()
        
        # Verificar datas mínimas e máximas
        cursor.execute("SELECT MIN(dia), MAX(dia) FROM bpd")
        min_date, max_date = cursor.fetchone()
        print(f"\nDatas no banco:")
        print(f"Data mínima: {min_date}")
        print(f"Data máxima: {max_date}")
        
        # Verificar dados dos últimos 30 dias
        today = datetime.now().date()
        thirty_days_ago = today - timedelta(days=29)
        print(f"\nÚltimos 30 dias: {thirty_days_ago} até {today}")
        
        cursor.execute("SELECT COUNT(*) FROM bpd WHERE dia BETWEEN %s AND %s", (thirty_days_ago, today))
        count_30_days = cursor.fetchone()[0]
        print(f"Dados nos últimos 30 dias: {count_30_days} linhas")
        
        if count_30_days > 0:
            cursor.execute("SELECT DISTINCT dia FROM bpd WHERE dia BETWEEN %s AND %s ORDER BY dia DESC LIMIT 10", (thirty_days_ago, today))
            recent_dates = cursor.fetchall()
            print("Datas recentes encontradas:")
            for date in recent_dates:
                print(f"  - {date[0]}")
        
        # Verificar dados da última semana
        end_of_last_week = today - timedelta(days=today.weekday() + 1)
        start_of_last_week = end_of_last_week - timedelta(days=6)
        print(f"\nÚltima semana: {start_of_last_week} até {end_of_last_week}")
        
        cursor.execute("SELECT COUNT(*) FROM bpd WHERE dia BETWEEN %s AND %s", (start_of_last_week, end_of_last_week))
        count_last_week = cursor.fetchone()[0]
        print(f"Dados na última semana: {count_last_week} linhas")
        
        if count_last_week > 0:
            cursor.execute("SELECT DISTINCT dia FROM bpd WHERE dia BETWEEN %s AND %s ORDER BY dia", (start_of_last_week, end_of_last_week))
            week_dates = cursor.fetchall()
            print("Datas da última semana:")
            for date in week_dates:
                print(f"  - {date[0]}")
        
        cursor.close()
    except Exception as e:
        print(f"Erro ao verificar datas: {e}")
    finally:
        if conn:
            conn.close()

def check_column_type_and_test_filters():
    import mysql.connector
    from datetime import datetime, timedelta
    conn = None
    try:
        conn = mysql.connector.connect(
            host=st.secrets["mysql"]["host"],
            user=st.secrets["mysql"]["user"],
            password=st.secrets["mysql"]["password"],
            database=st.secrets["mysql"]["database"],
            port=st.secrets["mysql"]["port"]
        )
        cursor = conn.cursor()
        
        # Verificar o tipo da coluna 'dia'
        cursor.execute("DESCRIBE bpd")
        columns = cursor.fetchall()
        print("\n=== ESTRUTURA DA TABELA BPD ===")
        for column in columns:
            if column[0] == 'dia':
                print(f"Coluna 'dia': {column[1]} ({column[2]})")
                break
        
        # Testar filtros de período
        today = datetime.now().date()
        
        # Teste 1: Últimos 30 dias
        thirty_days_ago = today - timedelta(days=29)
        print(f"\n=== TESTE 1: ÚLTIMOS 30 DIAS ===")
        print(f"Período: {thirty_days_ago} até {today}")
        
        cursor.execute("SELECT COUNT(*) FROM bpd WHERE dia BETWEEN %s AND %s", (thirty_days_ago, today))
        count_30 = cursor.fetchone()[0]
        print(f"Resultado: {count_30} linhas")
        
        if count_30 > 0:
            cursor.execute("SELECT DISTINCT dia FROM bpd WHERE dia BETWEEN %s AND %s ORDER BY dia DESC LIMIT 5", (thirty_days_ago, today))
            dates_30 = cursor.fetchall()
            print("Datas encontradas:")
            for date in dates_30:
                print(f"  - {date[0]}")
        
        # Teste 2: Última semana
        end_of_last_week = today - timedelta(days=today.weekday() + 1)
        start_of_last_week = end_of_last_week - timedelta(days=6)
        print(f"\n=== TESTE 2: ÚLTIMA SEMANA ===")
        print(f"Período: {start_of_last_week} até {end_of_last_week}")
        
        cursor.execute("SELECT COUNT(*) FROM bpd WHERE dia BETWEEN %s AND %s", (start_of_last_week, end_of_last_week))
        count_week = cursor.fetchone()[0]
        print(f"Resultado: {count_week} linhas")
        
        if count_week > 0:
            cursor.execute("SELECT DISTINCT dia FROM bpd WHERE dia BETWEEN %s AND %s ORDER BY dia", (start_of_last_week, end_of_last_week))
            dates_week = cursor.fetchall()
            print("Datas encontradas:")
            for date in dates_week:
                print(f"  - {date[0]}")
        
        # Teste 3: Hoje
        print(f"\n=== TESTE 3: HOJE ===")
        print(f"Data: {today}")
        
        cursor.execute("SELECT COUNT(*) FROM bpd WHERE dia = %s", (today,))
        count_today = cursor.fetchone()[0]
        print(f"Resultado: {count_today} linhas")
        
        # Teste 4: Semana atual
        start_current_week = today - timedelta(days=today.weekday())
        print(f"\n=== TESTE 4: SEMANA ATUAL ===")
        print(f"Período: {start_current_week} até {today}")
        
        cursor.execute("SELECT COUNT(*) FROM bpd WHERE dia BETWEEN %s AND %s", (start_current_week, today))
        count_current_week = cursor.fetchone()[0]
        print(f"Resultado: {count_current_week} linhas")
        
        cursor.close()
    except Exception as e:
        print(f"Erro ao verificar coluna e testar filtros: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    test_db_query_and_returned_columns()
    show_bpd_count_and_sample()
    check_date_range()
    check_column_type_and_test_filters()
