import streamlit as st
import os
import pandas as pd

__version__ = "1.0.0" # Versão inicial do aplicativo
from database import load_data, get_db_connection, load_all_users, load_user_config
from auth import generate_users, verify_login
from datetime import datetime, timedelta
from table_component import display_full_table
from filter_component import display_filters
from metric_cards_component import display_metric_cards
from config_page import display_config_page

from streamlit_option_menu import option_menu

# Configuração inicial da página
st.set_page_config(layout="wide", page_title="BPD - Sistema de Gestão")

# Carrega o CSS externo
with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# --- Funções da Aplicação ---

def show_login_screen():
    """Exibe a interface de login e gerencia a autenticação."""
    # st.markdown("<h1 style='text-align: center;'>Bem-vindo ao Dashboard de Poker</h1>", unsafe_allow_html=True)
    col_logo_left, col_logo_center, col_logo_right = st.columns([1, 1, 1])
    with col_logo_center:
        st.markdown("""<svg style='width: 50px; height: 50px; display: block; margin: auto;' id="Camada_2" data-name="Camada 2" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 143.7 179.94">  <defs>    <style>      .cls-1 {        fill: #0273a4;      }    </style>  </defs>  <g id="Camada_1-2" data-name="Camada 1">    <g>      <path class="cls-1" d="M25.71,129.08v-15.46l53.21-20.31,26.22-10.28c21.85-10.8,33.42-25.45,33.42-43.7C138.56,13.37,117.22,0,80.2,0H0v129.08h25.71ZM25.71,21.34h54.5c21.59,0,31.62,6.43,31.62,20.05s-9,21.59-29.82,29.31l-56.3,21.08V21.34Z"/>      <g>        <polygon points="108.36 81.36 108.36 81.36 108.36 81.36 108.36 81.36"/>        <path d="M105.14,83.03l-26.22,10.28,7.71,4.63c20.82,12.6,30.33,20.82,30.33,35.22,0,16.71-11.31,25.45-33.42,25.45H0v21.34h83.55c38.82,0,60.15-16.45,60.15-45.24,0-22.11-9.77-35.22-38.56-51.67Z"/>      </g>    </g>  </g></svg>""", unsafe_allow_html=True) # Centraliza o logo na tela de login
    st.markdown("<p style='text-align: center;'>Por favor, faça o login para continuar.</p>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align: center; font-size: small;'>Versão: {__version__}</p>", unsafe_allow_html=True)

    col_left, col_center, col_right = st.columns([1, 2, 1]) # Ajusta as colunas para centralizar o formulário
    with col_center:
        with st.form("login_form"):
            username = st.text_input("Usuário", key="login_username")
            password = st.text_input("Senha", type="password", key="login_password")
            submitted = st.form_submit_button("Entrar")

            if submitted:
                with st.spinner("Verificando credenciais..."):
                    users_df = load_all_users()
                    if not users_df.empty:
                        is_logged_in, user_role, user_name = verify_login(username, password, users_df)
                        
                        if is_logged_in:
                            st.session_state['logged_in'] = True
                            st.session_state['user_role'] = user_role
                            st.session_state['username'] = user_name
                            st.rerun() # Recarrega a página para mostrar o dashboard
                        else:
                            st.error("Usuário ou senha inválidos.")
                    else:
                        st.error("Não foi possível carregar os dados para verificação. Verifique a conexão com o banco.")

def show_main_dashboard():
    """Exibe o dashboard principal após o login."""
    
    # --- Header ---
    # Ajuste: todas as colunas do header com a mesma largura
    col1, col2, col3 = st.columns(3)

    with col1:
        st.write(f"Bem-vindo, {st.session_state['username']}!")
        
    with col2:
        # 1. SETUP: Define as opções e obtém a seleção do estado da sessão
        date_options = ("Semana Atual", "Hoje", "Última semana", "Últimos 30 dias", "Mostrar tudo")
        if 'date_range_option_index' not in st.session_state:
            # Carrega o período padrão salvo do banco de dados
            saved_period_index = load_user_config(st.session_state['username'], 'default_period_index', '2')
            try:
                default_period = int(saved_period_index)
            except (ValueError, TypeError):
                default_period = 2  # Fallback para "Última semana"
            st.session_state['date_range_option_index'] = default_period

        # Define as colunas para o seletor e o status
        col_select, col_status = st.columns([5, 9])

        with col_select:
            date_range_option = st.selectbox(
                "Intervalo",
                date_options,
                index=st.session_state['date_range_option_index'],
                label_visibility="collapsed",
                key="date_range_selector"
            )
            
            # Verifica se o período foi alterado
            current_index = date_options.index(date_range_option)
            if current_index != st.session_state['date_range_option_index']:
                st.session_state['date_range_option_index'] = current_index
                st.rerun()  # Força o rerun para atualizar os dados

        # 4. LÓGICA DE DATAS
        today = datetime.now().date()
        start_date, end_date = None, None

        if date_range_option == "Semana Atual":
            start_date = today - timedelta(days=today.weekday())
            end_date = today
        elif date_range_option == "Hoje":
            start_date = today
            end_date = today
        elif date_range_option == "Última semana":
            end_of_last_week = today - timedelta(days=today.weekday() + 1)
            start_date = end_of_last_week - timedelta(days=6)
            end_date = end_of_last_week
        elif date_range_option == "Últimos 30 dias":
            start_date = today - timedelta(days=29)
            end_date = today
        elif date_range_option == "Mostrar tudo":
            start_date = None
            end_date = None

        st.session_state['start_date'] = start_date
        st.session_state['end_date'] = end_date

        # 5. EXIBIÇÃO DO STATUS
        with col_status:
            if start_date and end_date:
                period_text = f"{start_date.strftime('%d/%m/%Y')} a {end_date.strftime('%d/%m/%Y')}"
            else:
                period_text = "Todos os dados"
            st.markdown(f"<div style='padding-top: 8px;'>Período: {period_text}</div>", unsafe_allow_html=True)

    with col3:
        # st.write(f"Bem-vindo, {st.session_state['username']}!")
        if st.button("Logout"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

    # st.markdown("---") # Separador visual

    # --- Sidebar ---
    with st.sidebar:
        # Definição das opções do menu
        if st.session_state['user_role'] == 'admin':
            menu_options_list = [
                "Dashboard",
                "Usuários",
                "Configurações"
            ]
            menu_icons_list = [
                "house",
                "people",
                "gear"
            ]
        else:  # player
            menu_options_list = [
                "Dashboard",
                "Configurações"
            ]
            menu_icons_list = [
                "house",
                "gear"
            ]

        selected_option = option_menu(
            menu_title=None,  # Esconde o título do menu
            options=menu_options_list,
            icons=menu_icons_list,
            menu_icon="cast",  # Ícone do menu principal
            default_index=0,  # Opção padrão selecionada
            styles={
                "container": {"padding": "0!important", "background-color": "#fafafa"},
                "icon": {"color": "#0273a4", "font-size": "16px"},
                "nav-link": {"font-size": "12px", "text-align": "left", "margin": "0px", "--hover-color": "#eee"},
                "nav-link-selected": {"background-color": "#0273a4", "color": "white"},
            }
        )

    # --- Conteúdo principal conforme seleção ---
    if selected_option == "Dashboard":
        with st.spinner("Carregando informações do banco de dados..."):
            df_full = load_data(st.session_state['username'], st.session_state['user_role'], st.session_state['start_date'], st.session_state['end_date'])
            
            # Aplicar filtros avançados primeiro
            with st.expander("Filtros Avançados", expanded=False):
                df_filtered_by_controls = display_filters(df_full)
            
            # Exibir métricas com base nos dados filtrados
            display_metric_cards(df_filtered_by_controls, st.session_state['selected_currencies'])
            
            # Exibir tabela com dados filtrados
            display_full_table(df_filtered_by_controls, st.session_state['user_role'])
    elif selected_option == "Usuários":
        st.write("Conteúdo de gerenciamento de usuários aqui...")
    elif selected_option == "Configurações":
        display_config_page()

# --- Lógica Principal ---

# Inicializa o estado da sessão se ainda não existir
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'selected_currencies' not in st.session_state:
    st.session_state['selected_currencies'] = ["Real (R$)"] # Padrão inicial

# Decide qual tela mostrar
if st.session_state['logged_in']:
    show_main_dashboard()
else:
    show_login_screen()
