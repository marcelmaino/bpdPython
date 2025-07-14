import pandas as pd

def generate_users(player_names, agent_names):
    """
    Gera um DataFrame de usuários com base nos jogadores únicos e agentes fornecidos.
    Adiciona um usuário administrador estático.
    """
    users_data = []

    # Adiciona o usuário Admin estático
    users_data.append({'username': 'admin', 'password': '123', 'role': 'Admin'})

    # Gera usuários para cada jogador único
    for player_name in player_names:
        # Regra de senha: Primeira letra do nome em maiúscula + "2025" + últimos 4 caracteres do "playerName"
        # Certifica-se de que o player_name é uma string antes de tentar acessar seus caracteres
        player_name_str = str(player_name)
        # Verifica se a string não está vazia e tem pelo menos 4 caracteres
        if player_name_str and len(player_name_str) >= 4:
            password = f"{player_name_str[0].upper()}2025{player_name_str[-4:]}"
        else:
            # Atribui uma senha padrão ou gera uma de forma diferente para nomes curtos/vazios
            password = "DefaultPass2025" # Ou alguma lógica para gerar uma senha segura
        users_data.append({'username': player_name_str, 'password': password, 'role': 'Jogador'})

    # Gera usuários para cada agente único (se necessário, com uma regra de senha diferente)
    # Por enquanto, não há regra específica para agentes, então eles não serão criados como usuários de login
    # Se precisar, adicione lógica similar aqui para agent_names

    return pd.DataFrame(users_data)

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