import streamlit as st
from database import save_user_config, load_user_config, get_user_info, update_user_password, update_user_email, create_user_if_not_exists

def display_config_page():
    st.title("Configurações")

    with st.expander("Seleção de Moeda", expanded=False):
        st.markdown("**Selecione a Moeda Padrão para Exibição:**")
        currency_option = st.radio(
            "Moeda:",
            ["Real (R$)", "Dólar (US$)"],
            index=0, # Padrão: Real (R$)
            key="config_currency_selector",
            label_visibility="collapsed"
        )
        # Atualiza o session_state global para a moeda selecionada
        st.session_state['selected_currencies'] = [currency_option]

    with st.expander("Período Padrão", expanded=False):
        st.markdown("**Defina o Período Padrão ao Acessar o Sistema:**")
        
        # Opções de período disponíveis
        period_options = ["Semana Atual", "Hoje", "Última semana", "Últimos 30 dias", "Mostrar tudo"]
        
        # Carrega o período padrão salvo do banco de dados
        saved_period_index = load_user_config(st.session_state['username'], 'default_period_index', '2')
        try:
            saved_period_index = int(saved_period_index)
        except (ValueError, TypeError):
            saved_period_index = 2  # Fallback para "Última semana"
        
        # Inicializa o período padrão se não existir na sessão
        if 'default_period_index' not in st.session_state:
            st.session_state['default_period_index'] = saved_period_index
        
        # Mapeia o índice atual para o período
        current_period = period_options[st.session_state['default_period_index']]
        
        period_option = st.radio(
            "Período Padrão:",
            period_options,
            index=st.session_state['default_period_index'],
            key="config_period_selector",
            label_visibility="collapsed"
        )
        
        # Atualiza o índice do período padrão
        if period_option in period_options:
            st.session_state['default_period_index'] = period_options.index(period_option)
        
        # Mostra o período atual selecionado
        st.info(f"**Período atual:** {current_period}")
        st.info(f"**Novo período padrão:** {period_option}")
        
        # Botão para aplicar a mudança
        if st.button("Aplicar Período Padrão", key="apply_default_period"):
            # Salva no banco de dados
            period_index = str(period_options.index(period_option))
            if save_user_config(st.session_state['username'], 'default_period_index', period_index):
                st.session_state['date_range_option_index'] = period_options.index(period_option)
                st.success(f"Período padrão salvo e aplicado: {period_option}")
                st.rerun()
            else:
                st.error("Erro ao salvar configuração. Tente novamente.")

    with st.expander("Trocar Senha", expanded=False):
        # Buscar informações do usuário atual
        user_info = get_user_info(st.session_state['username'])
        
        # Mostrar e-mail atual se existir
        if user_info and user_info.get('email'):
            st.info(f"**E-mail atual:** {user_info['email']}")
        else:
            st.warning("⚠️ Nenhum e-mail cadastrado. Cadastre um e-mail para poder trocar a senha.")
        
        # Mostrar senha atual (mascarada)
        current_password = "••••••••"  # Senha mascarada para exibição
        st.info(f"**Senha atual:** {current_password}")
        
        with st.form("change_password_form"):
            st.write("Preencha os campos para trocar sua senha.")
            
            # Campo de e-mail como condição
            email = st.text_input("E-mail de Confirmação", 
                                 value=user_info.get('email', '') if user_info else '',
                                 key="change_password_email", 
                                 help="Digite seu e-mail para confirmar a troca de senha")
            
            # Campo da senha atual (preenchido automaticamente)
            old_password = st.text_input("Senha Atual", value="••••••••", type="password", key="old_password",
                                        help="Sua senha atual (preenchida automaticamente)")
            
            # Nova senha
            new_password = st.text_input("Nova Senha", type="password", key="new_password",
                                        help="Digite sua nova senha (mínimo 6 caracteres)")
            
            # Confirmar nova senha
            confirm_new_password = st.text_input("Confirmar Nova Senha", type="password", key="confirm_new_password",
                                                help="Digite novamente sua nova senha")
            
            # Validações
            col1, col2 = st.columns(2)
            with col1:
                if new_password:
                    if len(new_password) < 6:
                        st.error("❌ Nova senha deve ter pelo menos 6 caracteres")
                    else:
                        st.success("✅ Nova senha atende aos requisitos mínimos")
            
            with col2:
                if confirm_new_password and new_password:
                    if new_password != confirm_new_password:
                        st.error("❌ Senhas não coincidem")
                    else:
                        st.success("✅ Senhas coincidem")
            
            password_submitted = st.form_submit_button("Trocar Senha", type="primary")
            
            if password_submitted:
                # Validações antes de processar
                if not email:
                    st.error("❌ E-mail é obrigatório para trocar a senha")
                elif not new_password or len(new_password) < 6:
                    st.error("❌ Nova senha deve ter pelo menos 6 caracteres")
                elif new_password != confirm_new_password:
                    st.error("❌ Senhas não coincidem")
                else:
                    # Criar usuário se não existir na tabela users
                    if not user_info:
                        create_user_if_not_exists(st.session_state['username'], email, new_password, st.session_state['user_role'])
                        st.success(f"✅ Usuário criado e senha definida com sucesso!")
                    else:
                        # Atualizar e-mail se mudou
                        if email != user_info.get('email'):
                            if update_user_email(st.session_state['username'], email):
                                st.success("✅ E-mail atualizado com sucesso!")
                        
                        # Atualizar senha
                        if update_user_password(st.session_state['username'], new_password):
                            st.success(f"✅ Senha alterada com sucesso para o usuário {st.session_state['username']}")
                        else:
                            st.error("❌ Erro ao alterar senha. Tente novamente.")
                    
                    # Mostrar instruções para o usuário
                    st.info("💡 Os campos foram limpos. Você pode preencher novamente se desejar trocar a senha mais uma vez.")

    with st.expander("Trocar Nome de Usuário", expanded=False):
        with st.form("change_username_form"):
            st.write("Preencha os campos para trocar seu nome de usuário.")
            current_username = st.text_input("Nome de Usuário Atual", key="current_username")
            new_username = st.text_input("Novo Nome de Usuário", key="new_username")
            
            username_submitted = st.form_submit_button("Trocar Nome de Usuário")
            if username_submitted:
                st.warning("Funcionalidade de troca de nome de usuário ainda não implementada.")
                # Lógica de troca de nome de usuário virá aqui
