import streamlit as st
import mysql.connector
import pandas as pd
from datetime import datetime, timedelta
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

def test_date_logic():
    print("=== TESTE DA LÓGICA DE DATAS ===")
    
    # Simular exatamente o que o dashboard faz
    today = datetime.now().date()
    print(f"Data de hoje: {today}")
    
    # Testar "Últimos 30 dias"
    start_date_30 = today - timedelta(days=29)
    end_date_30 = today
    print(f"\nÚltimos 30 dias:")
    print(f"  Início: {start_date_30}")
    print(f"  Fim: {end_date_30}")
    
    # Conectar ao banco e testar
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
        
        # Testar filtro "Últimos 30 dias"
        print(f"\n=== TESTE FILTRO 'ÚLTIMOS 30 DIAS' ===")
        query_30 = "SELECT dia, playerName, reference FROM bpd WHERE dia BETWEEN %s AND %s ORDER BY dia DESC LIMIT 10"
        cursor.execute(query_30, (start_date_30, end_date_30))
        results_30 = cursor.fetchall()
        print(f"Query executada: {query_30}")
        print(f"Parâmetros: {start_date_30}, {end_date_30}")
        print(f"Resultados encontrados: {len(results_30)}")
        print("Primeiras 5 linhas:")
        for i, row in enumerate(results_30[:5]):
            print(f"  {i+1}. {row[0]} | {row[1]} | {row[2]}")
        
        # Testar "Mostrar tudo"
        print(f"\n=== TESTE FILTRO 'MOSTRAR TUDO' ===")
        query_all = "SELECT dia, playerName, reference FROM bpd ORDER BY dia DESC LIMIT 10"
        cursor.execute(query_all)
        results_all = cursor.fetchall()
        print(f"Query executada: {query_all}")
        print(f"Resultados encontrados: {len(results_all)}")
        print("Primeiras 5 linhas:")
        for i, row in enumerate(results_all[:5]):
            print(f"  {i+1}. {row[0]} | {row[1]} | {row[2]}")
        
        # Verificar se 2025-07-12 está dentro do período de 30 dias
        target_date = datetime(2025, 7, 12).date()
        print(f"\n=== VERIFICAÇÃO ESPECÍFICA ===")
        print(f"Data alvo: {target_date}")
        print(f"Está dentro do período de 30 dias? {start_date_30 <= target_date <= end_date_30}")
        print(f"Comparação: {start_date_30} <= {target_date} <= {end_date_30}")
        
        # Buscar especificamente por 2025-07-12
        print(f"\n=== BUSCA ESPECÍFICA POR 2025-07-12 ===")
        query_specific = "SELECT dia, playerName, reference FROM bpd WHERE dia = %s LIMIT 5"
        cursor.execute(query_specific, (target_date,))
        results_specific = cursor.fetchall()
        print(f"Registros encontrados para {target_date}: {len(results_specific)}")
        for i, row in enumerate(results_specific):
            print(f"  {i+1}. {row[0]} | {row[1]} | {row[2]}")
        
        cursor.close()
        
    except Exception as e:
        print(f"Erro: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    test_date_logic() 