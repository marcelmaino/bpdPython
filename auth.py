import pandas as pd
from database import load_all_users

def generate_users(player_names, agent_names):
    """
    Gera um DataFrame de usuários com base nos jogadores únicos e agentes fornecidos.
    Carrega todos os usuários do banco de dados, incluindo o admin.
    """
    # Carrega todos os usuários do banco de dados
    users_df = load_all_users()
    
    if users_df.empty:
        # Fallback: cria usuário admin estático se não conseguir carregar do banco
        users_data = [{'username': 'admin', 'password': '123', 'role': 'Admin'}]
        return pd.DataFrame(users_data)
    
    return users_df

def verify_login(username, password, users_df):
    """
    Verifica as credenciais do usuário no DataFrame de usuários.
    Retorna True se as credenciais forem válidas, False caso contrário, e o papel do usuário.
    """
    user_found = users_df[(users_df['username'] == username) & (users_df['password'] == password)]
    if not user_found.empty:
        user_role = user_found['role'].iloc[0]
        user_name = user_found['username'].iloc[0]
        return True, user_role, user_name
    return False, None, None