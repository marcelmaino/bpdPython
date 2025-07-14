import streamlit as st
import pandas as pd

def display_filters(df_original: pd.DataFrame):
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

    # --- Botão Limpar Filtros ---
    if st.button("Limpar Filtros", key="clear_filters_button"):
        st.session_state["player_filter_value"] = ["Todos os Jogadores"]
        st.session_state["reference_filter_value"] = ["Todas as Referências"]
        st.session_state["club_filter_value"] = ["Todos os Clubes"]
        st.session_state["agent_filter_value"] = ["Todos os Agentes"]
        st.rerun() # Recarregar a página para aplicar o reset

    # --- Layout dos Filtros ---
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        # --- Filtro por Jogador ---
        unique_players = ["Todos os Jogadores"] + sorted(df_original['playerName'].dropna().unique().tolist())
        selected_players = st.multiselect(
            "Filtrar por Jogador:",
            options=unique_players,
            default=st.session_state["player_filter_value"],
            key="player_filter"
        )
        st.session_state["player_filter_value"] = selected_players

    with col2:
        # --- Filtro por Clube ---
        unique_clubs = ["Todos os Clubes"] + sorted(df_original['club'].dropna().unique().tolist())
        selected_clubs = st.multiselect(
            "Filtrar por Clube:",
            options=unique_clubs,
            default=st.session_state["club_filter_value"],
            key="club_filter"
        )
        st.session_state["club_filter_value"] = selected_clubs

    with col3:
        # --- Filtro por Referência ---
        unique_references = ["Todas as Referências"] + sorted(df_original['reference'].dropna().unique().tolist())
        selected_references = st.multiselect(
            "Filtrar por Referência:",
            options=unique_references,
            default=st.session_state["reference_filter_value"],
            key="reference_filter"
        )
        st.session_state["reference_filter_value"] = selected_references

    with col4:
        # --- Filtro por Agente ---
        unique_agents = ["Todos os Agentes"] + sorted(df_original['agentName'].dropna().unique().tolist())
        selected_agents = st.multiselect(
            "Filtrar por Agente:",
            options=unique_agents,
            default=st.session_state["agent_filter_value"],
            key="agent_filter"
        )
        st.session_state["agent_filter_value"] = selected_agents

    # --- Lógica de Filtragem ---

    # 1. Aplicar Filtro por Jogador
    if "Todos os Jogadores" not in selected_players:
        df_filtered = df_filtered[df_filtered['playerName'].isin(selected_players)]

    # 2. Aplicar Filtro por Referência
    if "Todas as Referências" not in selected_references:
        df_filtered = df_filtered[df_filtered['reference'].isin(selected_references)]

    # 3. Aplicar Filtro por Clube
    if "Todos os Clubes" not in selected_clubs:
        df_filtered = df_filtered[df_filtered['club'].isin(selected_clubs)]

    # 4. Aplicar Filtro por Agente
    if "Todos os Agentes" not in selected_agents:
        df_filtered = df_filtered[df_filtered['agentName'].isin(selected_agents)]

    return df_filtered
