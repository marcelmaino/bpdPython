import streamlit as st

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

    with st.expander("Trocar Senha", expanded=False):
        with st.form("change_password_form"):
            st.write("Preencha os campos para trocar sua senha.")
            old_password = st.text_input("Senha Antiga", type="password", key="old_password")
            new_password = st.text_input("Nova Senha", type="password", key="new_password")
            confirm_new_password = st.text_input("Confirmar Nova Senha", type="password", key="confirm_new_password")
            
            password_submitted = st.form_submit_button("Trocar Senha")
            if password_submitted:
                st.warning("Funcionalidade de troca de senha ainda não implementada.")
                # Lógica de troca de senha virá aqui

    with st.expander("Trocar Nome de Usuário", expanded=False):
        with st.form("change_username_form"):
            st.write("Preencha os campos para trocar seu nome de usuário.")
            current_username = st.text_input("Nome de Usuário Atual", key="current_username")
            new_username = st.text_input("Novo Nome de Usuário", key="new_username")
            
            username_submitted = st.form_submit_button("Trocar Nome de Usuário")
            if username_submitted:
                st.warning("Funcionalidade de troca de nome de usuário ainda não implementada.")
                # Lógica de troca de nome de usuário virá aqui
