import streamlit as st
import pandas as pd

def display_filters(df_original: pd.DataFrame) -> pd.DataFrame:
    df_filtered = df_original.copy() # Começa com o DataFrame original

    # Inicializa o session_state para os filtros se não existirem
    if "player_filter_value" not in st.session_state:
        st.session_state["player_filter_value"] = ["Todos os Jogadores"]
    if "reference_filter_value" not in st.session_state:
        st.session_state["reference_filter_value"] = ["Todas as Referências"]
    if "club_filter_value" not in st.session_state:
        st.session_state["club_filter_value"] = ["Todos os Clubes"]
    if "agent_filter_value" not in st.session_state:
        st.session_state["agent_filter_value"] = ["Todos os Agentes"]
    
    # Verifica se os dados mudaram significativamente (mudança de período)
    # Se sim, limpa os filtros para evitar valores inválidos
    current_data_hash = hash(str(df_original.shape) + str(sorted(df_original['playerName'].dropna().unique()[:10])))
    if "last_data_hash" not in st.session_state:
        st.session_state["last_data_hash"] = current_data_hash
    elif st.session_state["last_data_hash"] != current_data_hash:
        # Dados mudaram, limpar filtros
        st.session_state["player_filter_value"] = ["Todos os Jogadores"]
        st.session_state["reference_filter_value"] = ["Todas as Referências"]
        st.session_state["club_filter_value"] = ["Todos os Clubes"]
        st.session_state["agent_filter_value"] = ["Todos os Agentes"]
        st.session_state["last_data_hash"] = current_data_hash

    # --- Botão Limpar Filtros ---
    if st.button("Limpar Filtros", key="clear_filters_button"):
        st.session_state["player_filter_value"] = ["Todos os Jogadores"]
        st.session_state["reference_filter_value"] = ["Todas as Referências"]
        st.session_state["club_filter_value"] = ["Todos os Clubes"]
        st.session_state["agent_filter_value"] = ["Todos os Agentes"]
        st.rerun() # Recarregar a página para aplicar o reset

    # --- Indicador de Filtros Ativos ---
    active_filters = []
    if "Todos os Jogadores" not in st.session_state.get("player_filter_value", ["Todos os Jogadores"]):
        active_filters.append("Jogadores")
    if "Todas as Referências" not in st.session_state.get("reference_filter_value", ["Todas as Referências"]):
        active_filters.append("Referências")
    if "Todos os Clubes" not in st.session_state.get("club_filter_value", ["Todos os Clubes"]):
        active_filters.append("Clubes")
    if "Todos os Agentes" not in st.session_state.get("agent_filter_value", ["Todos os Agentes"]):
        active_filters.append("Agentes")
    
    if active_filters:
        st.info(f"🎯 Filtros ativos: {', '.join(active_filters)}")

    # --- Layout dos Filtros ---
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        # --- Filtro por Jogador ---
        unique_players = ["Todos os Jogadores"] + sorted(df_original['playerName'].dropna().unique().tolist())
        
        # Valida se os valores padrão estão disponíveis nas opções atuais
        valid_default_players = [player for player in st.session_state["player_filter_value"] if player in unique_players]
        if not valid_default_players:
            valid_default_players = ["Todos os Jogadores"]
            st.session_state["player_filter_value"] = valid_default_players
        
        selected_players = st.multiselect(
            "Filtrar por Jogador:",
            options=unique_players,
            default=valid_default_players,
            key="player_filter"
        )
        
        # Verifica se o filtro foi alterado
        if selected_players != st.session_state["player_filter_value"]:
            st.session_state["player_filter_value"] = selected_players
            st.rerun()  # Força atualização das métricas

    with col2:
        # --- Filtro por Clube ---
        unique_clubs = ["Todos os Clubes"] + sorted(df_original['club'].dropna().unique().tolist())
        
        # Valida se os valores padrão estão disponíveis nas opções atuais
        valid_default_clubs = [club for club in st.session_state["club_filter_value"] if club in unique_clubs]
        if not valid_default_clubs:
            valid_default_clubs = ["Todos os Clubes"]
            st.session_state["club_filter_value"] = valid_default_clubs
        
        selected_clubs = st.multiselect(
            "Filtrar por Clube:",
            options=unique_clubs,
            default=valid_default_clubs,
            key="club_filter"
        )
        
        # Verifica se o filtro foi alterado
        if selected_clubs != st.session_state["club_filter_value"]:
            st.session_state["club_filter_value"] = selected_clubs
            st.rerun()  # Força atualização das métricas

    with col3:
        # --- Filtro por Referência ---
        unique_references = ["Todas as Referências"] + sorted(df_original['reference'].dropna().unique().tolist())
        
        # Valida se os valores padrão estão disponíveis nas opções atuais
        valid_default_references = [ref for ref in st.session_state["reference_filter_value"] if ref in unique_references]
        if not valid_default_references:
            valid_default_references = ["Todas as Referências"]
            st.session_state["reference_filter_value"] = valid_default_references
        
        selected_references = st.multiselect(
            "Filtrar por Referência:",
            options=unique_references,
            default=valid_default_references,
            key="reference_filter"
        )
        
        # Verifica se o filtro foi alterado
        if selected_references != st.session_state["reference_filter_value"]:
            st.session_state["reference_filter_value"] = selected_references
            st.rerun()  # Força atualização das métricas

    with col4:
        # --- Filtro por Agente ---
        unique_agents = ["Todos os Agentes"] + sorted(df_original['agentName'].dropna().unique().tolist())
        
        # Valida se os valores padrão estão disponíveis nas opções atuais
        valid_default_agents = [agent for agent in st.session_state["agent_filter_value"] if agent in unique_agents]
        if not valid_default_agents:
            valid_default_agents = ["Todos os Agentes"]
            st.session_state["agent_filter_value"] = valid_default_agents
        
        selected_agents = st.multiselect(
            "Filtrar por Agente:",
            options=unique_agents,
            default=valid_default_agents,
            key="agent_filter"
        )
        
        # Verifica se o filtro foi alterado
        if selected_agents != st.session_state["agent_filter_value"]:
            st.session_state["agent_filter_value"] = selected_agents
            st.rerun()  # Força atualização das métricas

    # --- Lógica de Filtragem ---

    # 1. Aplicar Filtro por Jogador
    if "Todos os Jogadores" not in selected_players and 'playerName' in df_filtered.columns:
        mask = df_filtered['playerName'].isin(selected_players)
        df_filtered = df_filtered[mask].copy()

    # 2. Aplicar Filtro por Referência
    if "Todas as Referências" not in selected_references and 'reference' in df_filtered.columns:
        mask = df_filtered['reference'].isin(selected_references)
        df_filtered = df_filtered[mask].copy()

    # 3. Aplicar Filtro por Clube
    if "Todos os Clubes" not in selected_clubs and 'club' in df_filtered.columns:
        mask = df_filtered['club'].isin(selected_clubs)
        df_filtered = df_filtered[mask].copy()

    # 4. Aplicar Filtro por Agente
    if "Todos os Agentes" not in selected_agents and 'agentName' in df_filtered.columns:
        mask = df_filtered['agentName'].isin(selected_agents)
        df_filtered = df_filtered[mask].copy()

    return df_filtered
