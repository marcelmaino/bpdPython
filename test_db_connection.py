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
                `linha_id`, ` dia`, ` reference`, ` share`, ` moeda`, ` upline`,
                ` club`, ` playerID`, ` playerName`, ` agentName`, ` agentId`,
                ` superAgentName`, ` superagentId`, ` localWins`, ` localFee`,
                ` hands`, ` dolarWins`, ` dolarFee`, ` dolarRakeback`,
                ` dolarRebate`, ` realWins`, ` realFee`, ` realRakeback`,
                ` realRebate`, ` realAgentSett`, ` dolarAgentSett`,
                ` realRevShare`, ` realBPFProfit`, ` deal`, ` rebate`
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

if __name__ == "__main__":
    test_db_query_and_returned_columns()
