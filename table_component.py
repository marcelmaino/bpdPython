import streamlit as st
import pandas as pd
import numpy as np

def display_full_table(df: pd.DataFrame, user_role: str):
    st.subheader("Tabela Completa de Dados")

    if df.empty:
        st.warning("Nenhum dado disponível para exibição.")
        return

    # --- Opções de Configuração da Tabela ---
    st.write("Use as opções abaixo para configurar a exibição da tabela.")

    # O DataFrame filtrado é o mesmo que o original, pois a busca foi removida.
    df_filtered = df

    # --- Seleção de Colunas ---
    all_columns = df_filtered.columns.tolist()
    
    # Definir colunas padrão para exibição inicial
    default_cols = ['dia', 'reference', 'club', 'playerName', 'agentName', 'localWins', 'localFee', 'hands']
    # Garantir que as colunas padrão existam no DataFrame
    default_cols = [col for col in default_cols if col in all_columns]

    selected_columns = st.multiselect(
        "Selecionar Colunas:",
        options=all_columns,
        default=default_cols,
        help="Selecione as colunas que deseja exibir na tabela."
    )

    if not selected_columns:
        st.warning("Por favor, selecione pelo menos uma coluna para exibir.")
        return

    df_display = df_filtered[selected_columns]

    # --- Configuração de Paginação ---
    total_rows = len(df_display)
    page_size_options = [20, 50, 100, 1000, "Todas"]
    
    # Garante que a sessão tenha um valor padrão para 'page_size'
    if 'page_size' not in st.session_state or st.session_state['page_size'] not in page_size_options:
        st.session_state['page_size'] = 50

    # --- Exibição da Tabela e Opções Adicionais ---
    st.markdown("### Dados da Tabela")

    # Botão de Download
    csv = df_display.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Baixar dados como CSV",
        data=csv,
        file_name='dados_tabela.csv',
        mime='text/csv',
        help="Baixa os dados atualmente exibidos na tabela (filtrados e com colunas selecionadas) como um arquivo CSV."
    )

    # Define a página atual, garantindo que ela seja reiniciada se os filtros mudarem
    if 'current_page' not in st.session_state:
        st.session_state['current_page'] = 1

    # Lógica de paginação
    if st.session_state.get('page_size') == "Todas":
        rows_per_page = total_rows
        total_pages = 1
        st.session_state['current_page'] = 1 # Reseta para a página 1
    else:
        rows_per_page = st.session_state['page_size']
        total_pages = int(np.ceil(total_rows / rows_per_page)) if total_rows > 0 else 1
    
    # Garante que a página atual não seja maior que o total de páginas
    if st.session_state['current_page'] > total_pages:
        st.session_state['current_page'] = total_pages

    start_row = (st.session_state['current_page'] - 1) * rows_per_page
    end_row = start_row + rows_per_page
    df_paginated = df_display.iloc[start_row:end_row]

    # Exibição da Tabela
    st.dataframe(df_paginated, use_container_width=True, height=700)

    # --- Controles de Paginação Visuais ---
    st.markdown("<hr style='margin: 1em 0;'>", unsafe_allow_html=True)
    
    col_info, col_size, col_nav = st.columns([2, 2, 3])

    with col_info:
        st.info(f"Exibindo {len(df_paginated)} de {total_rows} | Página {st.session_state['current_page']} de {total_pages}")

    with col_size:
        # Layout para colocar o rótulo ao lado do seletor
        label_col, select_col = st.columns([1, 2])

        with label_col:
            st.markdown("<div style='text-align: right; padding-top: 8px;'>Linhas por página:</div>", unsafe_allow_html=True)

        with select_col:
            # Atualiza o page_size na sessão e reseta a página atual para 1
            def on_page_size_change():
                st.session_state['page_size'] = st.session_state['page_size_select']
                st.session_state['current_page'] = 1

            st.selectbox(
                "Linhas por página:",
                options=page_size_options,
                key='page_size_select',
                index=page_size_options.index(st.session_state['page_size']),
                on_change=on_page_size_change,
                label_visibility="collapsed"
            )

    with col_nav:
        # Desabilita a navegação se "Todas" estiver selecionado
        disable_nav = st.session_state.get('page_size') == "Todas"

        # Layout para os botões de navegação
        nav_cols = st.columns(5)
        
        with nav_cols[0]:
            if st.button("⏮️", help="Primeira Página", disabled=(st.session_state['current_page'] == 1 or disable_nav)):
                st.session_state['current_page'] = 1
                st.rerun()

        with nav_cols[1]:
            if st.button("⬅️", help="Página Anterior", disabled=(st.session_state['current_page'] <= 1 or disable_nav)):
                st.session_state['current_page'] -= 1
                st.rerun()

        with nav_cols[2]:
            # Campo de entrada para a página atual
            def on_page_input_change():
                page_input = st.session_state.get('page_input', 1)
                if 1 <= page_input <= total_pages:
                    st.session_state['current_page'] = page_input

            st.number_input(
                "Página",
                min_value=1,
                max_value=total_pages,
                value=st.session_state['current_page'],
                on_change=on_page_input_change,
                key='page_input',
                label_visibility="collapsed",
                disabled=disable_nav
            )

        with nav_cols[3]:
            if st.button("➡️", help="Próxima Página", disabled=(st.session_state['current_page'] >= total_pages or disable_nav)):
                st.session_state['current_page'] += 1
                st.rerun()

        with nav_cols[4]:
            if st.button("⏭️", help="Última Página", disabled=(st.session_state['current_page'] == total_pages or disable_nav)):
                st.session_state['current_page'] = total_pages
                st.rerun()

    # --- Totais das Colunas Mensuráveis ---
    st.markdown("### Totais")
    
    # Lista de colunas que devem ter seus totais exibidos
    # Certifique-se de que estas colunas são numéricas no seu DataFrame
    measurable_columns = [
        'localWins', 'localFee', 'hands',
        'dolarWins', 'dolarFee', 'dolarRakeback', 'dolarRebate', 'dolarAgentSett',
        'realWins', 'realFee', 'realRakeback', 'realRebate', 'realAgentSett',
        'realRevShare', 'realBPFProfit', 'deal', 'rebate'
    ]

    # Filtra as colunas mensuráveis que estão presentes no df_display e são numéricas
    columns_to_sum = [col for col in measurable_columns if col in df_display.columns and pd.api.types.is_numeric_dtype(df_display[col])]

    if columns_to_sum:
        # Cria colunas para exibir os totais, limitando a 4 por linha para melhor visualização
        cols_per_row = 4
        num_rows = int(np.ceil(len(columns_to_sum) / cols_per_row))

        for i in range(num_rows):
            current_cols = st.columns(cols_per_row)
            for j in range(cols_per_row):
                idx = i * cols_per_row + j
                if idx < len(columns_to_sum):
                    col_name = columns_to_sum[idx]
                    total_value = df_display[col_name].sum()
                    
                    # Formatação para valores monetários (exemplo simples)
                    if 'dolar' in col_name.lower():
                        formatted_value = f"US$ {total_value:,.2f}"
                    elif 'real' in col_name.lower():
                        formatted_value = f"R$ {total_value:,.2f}"
                    else:
                        formatted_value = f"{total_value:,.0f}" # Para mãos, etc.

                    with current_cols[j]:
                        st.metric(label=col_name, value=formatted_value)
    else:
        st.info("Nenhuma coluna mensurável selecionada para exibir totais.")
