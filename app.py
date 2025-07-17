import streamlit as st
import streamlit_shadcn_ui as ui
import os
import pandas as pd

__version__ = "1.0.0" # Versão inicial do aplicativo
from database import load_data, get_db_connection, load_all_users, load_user_config, get_date_range
from auth import generate_users, verify_login
from datetime import datetime, timedelta
from table_component import display_full_table
from filter_component import display_filters
from metric_cards_component import display_metric_cards
from config_page import display_config_page
from utils import insert_google_analytics



# Configuração inicial da página
st.set_page_config(layout="wide", page_title="BPD - Sistema de Gestão")

# Insere o código do Google Analytics
insert_google_analytics()

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

    # Layout com duas colunas: Login e Instruções
    col_login, col_instructions = st.columns([1, 1])
    
    with col_login:
        st.markdown("### 🔐 Login")
        with st.form("login_form"):
            username = st.text_input("Usuário", key="login_username")
            password = st.text_input("Senha", type="password", key="login_password")
            submitted = st.form_submit_button("Entrar", type="primary")

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
    
    with col_instructions:
        st.markdown("### 📋 Instruções de Login")
        
        # Instruções para Jogadores
        with st.expander("🎮 Jogadores", expanded=True):
            st.markdown("""
            **Usuário:** Seu nome completo no sistema  
            **Senha:** Gerada automaticamente com a regra:
            
            `Primeira letra do nome em maiúscula + "2025" + últimos 4 caracteres do nome`
            
            **Exemplo:** Para o jogador "João Silva"
            - Usuário: `João Silva`
            - Senha: `J2025Silv`
            
            **Observações:**
            - Use exatamente o nome como aparece no sistema
            - A senha é case-sensitive (diferencia maiúsculas/minúsculas)
            - Jogadores veem apenas seus próprios dados
            """)
        
        # Dicas gerais
        st.markdown("### 💡 Dicas")
        st.markdown("""
        - Se não conseguir fazer login, verifique se o nome está escrito exatamente como no sistema
        - Em caso de dúvida sobre sua senha, entre em contato com o administrador
        - O sistema é responsivo e funciona em dispositivos móveis
        """)

def display_users_page():
    """Exibe a página de gerenciamento de usuários para administradores."""
    st.markdown("## 👥 Gerenciamento de Usuários")
    st.markdown("Gerencie os usuários do sistema, visualize informações e busque por usuários específicos.")
    
    # Carregar todos os usuários
    with st.spinner("Carregando usuários..."):
        users_df = load_all_users()
    
    if users_df.empty:
        st.warning("Nenhum usuário encontrado no sistema.")
        return
    
    # Mecanismo de busca
    st.markdown("### 🔍 Buscar Usuários")
    col_search1, col_search2, col_search3 = st.columns([2, 2, 1])
    
    with col_search1:
        search_username = st.text_input("Buscar por nome de usuário", placeholder="Digite o nome...")
    
    with col_search2:
        search_role = st.selectbox("Filtrar por tipo", ["Todos", "Admin", "Jogador"])
    
    with col_search3:
        if st.button("🔍 Buscar", type="primary"):
            st.session_state['users_search_username'] = search_username
            st.session_state['users_search_role'] = search_role
            st.rerun()
    
    # Aplicar filtros
    filtered_df = users_df.copy()
    
    # Filtro por nome de usuário
    if 'users_search_username' in st.session_state and st.session_state['users_search_username']:
        search_term = st.session_state['users_search_username'].lower()
        filtered_df = filtered_df[filtered_df['username'].str.lower().str.contains(search_term, na=False)]
    
    # Filtro por tipo de usuário
    if 'users_search_role' in st.session_state and st.session_state['users_search_role'] != "Todos":
        role_filter = "Admin" if st.session_state['users_search_role'] == "Admin" else "Jogador"
        filtered_df = filtered_df[filtered_df['role'] == role_filter]
    
    # Estatísticas com Cards Modernos
    col_stats1, col_stats2, col_stats3, col_stats4 = st.columns(4)
    
    with col_stats1:
        total_users = len(users_df)
        st.markdown(f'''
        <div class="metric-card-improved">
            <div class="metric-content">
                <div class="metric-label">Total de Usuários</div>
                <div class="metric-value">{total_users}</div>
                <div class="metric-description">Usuários cadastrados no sistema</div>
            </div>
        </div>
        ''', unsafe_allow_html=True)
    
    with col_stats2:
        admin_count = len(users_df[users_df['role'] == 'Admin'])
        st.markdown(f'''
        <div class="metric-card-improved">
            <div class="metric-content">
                <div class="metric-label">Administradores</div>
                <div class="metric-value">{admin_count}</div>
                <div class="metric-description">Usuários com privilégios admin</div>
            </div>
        </div>
        ''', unsafe_allow_html=True)
    
    with col_stats3:
        player_count = len(users_df[users_df['role'] == 'Jogador'])
        st.markdown(f'''
        <div class="metric-card-improved">
            <div class="metric-content">
                <div class="metric-label">Jogadores</div>
                <div class="metric-value">{player_count}</div>
                <div class="metric-description">Usuários jogadores</div>
            </div>
        </div>
        ''', unsafe_allow_html=True)
    
    with col_stats4:
        filtered_count = len(filtered_df)
        st.markdown(f'''
        <div class="metric-card-improved">
            <div class="metric-content">
                <div class="metric-label">Resultados</div>
                <div class="metric-value">{filtered_count}</div>
                <div class="metric-description">Usuários encontrados</div>
            </div>
        </div>
        ''', unsafe_allow_html=True)
    
    # Tabela de usuários
    st.markdown("### 📋 Lista de Usuários")
    
    if filtered_df.empty:
        st.info("Nenhum usuário encontrado com os filtros aplicados.")
    else:
        # Preparar dados para exibição
        display_df = filtered_df.copy()
        
        # Mapear tipos de usuário para ícones
        display_df['Tipo'] = display_df['role'].map({
            'Admin': '👑 Admin',
            'Jogador': '🎮 Jogador'
        })
        
        # Selecionar e renomear colunas para exibição
        display_df = display_df[['username', 'Tipo', 'email']].rename(columns={
            'username': 'Nome de Usuário',
            'email': 'E-mail'
        })
        
        # Preencher emails vazios
        display_df['E-mail'] = display_df['E-mail'].fillna('Não cadastrado')
        
        # Exibir tabela
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Nome de Usuário": st.column_config.TextColumn(
                    "Nome de Usuário",
                    width="medium"
                ),
                "Tipo": st.column_config.TextColumn(
                    "Tipo",
                    width="small"
                ),
                "E-mail": st.column_config.TextColumn(
                    "E-mail",
                    width="large"
                )
            }
        )
        
        # Botão para limpar filtros
        if st.button("🗑️ Limpar Filtros"):
            if 'users_search_username' in st.session_state:
                del st.session_state['users_search_username']
            if 'users_search_role' in st.session_state:
                del st.session_state['users_search_role']
            st.rerun()

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
        
        # Buscar a data máxima dos dados para usar como referência
        _, max_date_db = get_date_range()
        reference_date = max_date_db if max_date_db else today
        
        start_date, end_date = None, None

        if date_range_option == "Semana Atual":
            start_date = reference_date - timedelta(days=reference_date.weekday())
            end_date = reference_date
        elif date_range_option == "Hoje":
            # Para "Hoje", sempre usar a data atual do sistema, não a data máxima do banco
            start_date = today
            end_date = today
        elif date_range_option == "Última semana":
            end_of_last_week = reference_date - timedelta(days=reference_date.weekday() + 1)
            start_date = end_of_last_week - timedelta(days=6)
            end_date = end_of_last_week
        elif date_range_option == "Últimos 30 dias":
            start_date = reference_date - timedelta(days=29)
            end_date = reference_date
        elif date_range_option == "Mostrar tudo":
            start_date = None
            end_date = None

        # Diagnóstico detalhado das datas
        print(f"\n=== DIAGNÓSTICO DETALHADO DE DATAS ===")
        print(f"Opção selecionada: {date_range_option}")
        print(f"Data de hoje (sistema): {today}")
        print(f"Data máxima no banco: {max_date_db}")
        print(f"Data de referência usada: {reference_date}")
        print(f"Data de início calculada: {start_date}")
        print(f"Data de fim calculada: {end_date}")
        print(f"Tipo de start_date: {type(start_date)}")
        print(f"Tipo de end_date: {type(end_date)}")
        print("=====================================\n")

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

    # --- Menu Lateral Simples e Limpo ---
    with st.sidebar:
        # Inicializar selected_option se não existir
        if 'selected_option' not in st.session_state:
            st.session_state['selected_option'] = "Dashboard"
        
        selected_option = st.session_state['selected_option']
        
        # CSS personalizado para os botões do menu
        st.markdown("""
        <style>
        div[data-testid="stButton"] > button {
            background: transparent !important;
            border: none !important;
            text-align: left !important;
            padding: 6px 12px !important;
            margin: 2px 0 !important;
            border-radius: 6px !important;
            transition: background-color 0.2s ease !important;
            width: 100% !important;
            justify-content: flex-start !important;
            font-size: 12px !important;
            font-weight: 400 !important;
        }
        div[data-testid="stButton"] > button:hover {
            background-color: #f0f2f6 !important;
        }
        div[data-testid="stButton"] > button[kind="primary"] {
            background-color: #e6f3ff !important;
            color: #0273a4 !important;
            font-weight: 500 !important;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Menu para Admin
        if st.session_state['user_role'] == 'Admin':
            if st.button("Dashboard", use_container_width=True, type="primary" if selected_option == "Dashboard" else "secondary"):
                st.session_state['selected_option'] = "Dashboard"
                st.rerun()
            
            if st.button("Usuários", use_container_width=True, type="primary" if selected_option == "Usuários" else "secondary"):
                st.session_state['selected_option'] = "Usuários"
                st.rerun()
            
            if st.button("Configurações", use_container_width=True, type="primary" if selected_option == "Configurações" else "secondary"):
                st.session_state['selected_option'] = "Configurações"
                st.rerun()
        
        # Menu para Player
        else:
            if st.button("Dashboard", use_container_width=True, type="primary" if selected_option == "Dashboard" else "secondary"):
                st.session_state['selected_option'] = "Dashboard"
                st.rerun()
            
            if st.button("Configurações", use_container_width=True, type="primary" if selected_option == "Configurações" else "secondary"):
                st.session_state['selected_option'] = "Configurações"
                st.rerun()

    # --- Conteúdo principal conforme seleção ---
    if selected_option == "Dashboard":
        with st.spinner("Carregando informações do banco de dados..."):
            df_full = load_data(st.session_state['username'], st.session_state['user_role'], st.session_state['start_date'], st.session_state['end_date'])

            # Diagnóstico: prints no console
            print("\n=== DIAGNÓSTICO DASHBOARD ===")
            print(f"Usuário logado: {st.session_state['username']}")
            print(f"Papel: {st.session_state['user_role']}")
            print(f"Período: {st.session_state['start_date']} até {st.session_state['end_date']}")
            print(f"Linhas carregadas do banco: {len(df_full)}")
            print(f"Colunas: {list(df_full.columns)}")
            print("Primeiras linhas:")
            print(df_full.head())
            print("============================\n")

            # Aplicar filtros avançados primeiro
            with st.expander("Filtros Avançados", expanded=False):
                df_filtered_by_controls = display_filters(df_full)
            
            # Diagnóstico dos dados antes da exibição
            print(f"\n=== DIAGNÓSTICO ANTES DA EXIBIÇÃO ===")
            print(f"Dados após filtros avançados: {len(df_filtered_by_controls)} linhas")
            if not df_filtered_by_controls.empty:
                print("Primeiras 3 linhas dos dados filtrados:")
                print(df_filtered_by_controls[['dia', 'playerName', 'reference']].head(3))
            print("=====================================\n")
            
            # Exibir métricas com base nos dados filtrados
            display_metric_cards(df_filtered_by_controls, st.session_state['selected_currencies'])

            # Exibir tabela com dados filtrados
            display_full_table(df_filtered_by_controls, st.session_state['user_role'])
    elif selected_option == "Usuários":
        display_users_page()
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
