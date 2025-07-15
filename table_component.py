import streamlit as st
import pandas as pd
import numpy as np

def display_full_table(df: pd.DataFrame, user_role: str):
    # st.subheader("Tabela Completa de Dados")

    if df.empty:
        st.warning("Nenhum dado disponível para exibição.")
        return

    # O DataFrame filtrado é o mesmo que o original, pois a busca foi removida.
    df_filtered = df

    # --- Seleção de Colunas em Expander ---
    with st.expander("Seleção de Colunas", expanded=False):
        st.write("Use as opções abaixo para configurar a exibição da tabela.")
        
        all_columns = df_filtered.columns.tolist()
        
        # Definir colunas padrão para exibição inicial
        default_cols = ['dia', 'reference', 'club', 'playerName', 'agentName', 'localWins', 'localFee', 'hands']
        # Garantir que as colunas padrão existam no DataFrame
        default_cols = [col for col in default_cols if col in all_columns]

        # Inicializa o estado da sessão para as colunas selecionadas se não existir
        if 'selected_columns_multiselect' not in st.session_state:
            st.session_state['selected_columns_multiselect'] = default_cols

        col_select_all, col_clear_selection = st.columns([1, 5])

        with col_select_all:
            if st.button("Selecionar Todas", key="select_all_cols"):
                st.session_state['selected_columns_multiselect'] = all_columns
                st.rerun()

        with col_clear_selection:
            if st.button("Limpar Seleção", key="clear_all_cols"):
                st.session_state['selected_columns_multiselect'] = []
                st.rerun()

        selected_columns = st.multiselect(
            "Selecionar Colunas:",
            options=all_columns,
            default=st.session_state['selected_columns_multiselect'],
            help="Selecione as colunas que deseja exibir na tabela.",
            key="column_selector"
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
    # st.markdown("### Dados da Tabela")

    # --- Prepare DataFrame for Export (including Totals) ---
    df_export_with_totals = df_display.copy() # Start with the full selected data

    measurable_columns = [
        'localWins', 'localFee', 'hands',
        'dolarWins', 'dolarFee', 'dolarRakeback', 'dolarRebate', 'dolarAgentSett',
        'realWins', 'realFee', 'realRakeback', 'realRebate', 'realAgentSett',
        'realRevShare', 'realBPFProfit', 'deal', 'rebate'
    ]

    columns_to_sum = [col for col in measurable_columns if col in df_display.columns and pd.api.types.is_numeric_dtype(df_display[col])]

    if columns_to_sum:
        totals_row_data = {}
        # Initialize all columns in df_export_with_totals with empty string for the totals row
        for col in df_export_with_totals.columns:
            totals_row_data[col] = ""

        # Populate only the measurable columns with their sums
        for col_name in columns_to_sum:
            total_value = df_display[col_name].sum() # Sum from df_display (before pagination) - mantém total geral para exportação
            totals_row_data[col_name] = total_value

        # Add a label for the totals row, e.g., in the first column
        if not df_export_with_totals.empty and df_export_with_totals.columns[0] in totals_row_data:
            totals_row_data[df_export_with_totals.columns[0]] = "TOTAL GERAL"
        elif not df_export_with_totals.empty:
            # Fallback if first column is not suitable, try to find a string/object column
            found_label_col = False
            for col in df_export_with_totals.columns:
                if pd.api.types.is_string_dtype(df_export_with_totals[col]) or pd.api.types.is_object_dtype(df_export_with_totals[col]):
                    totals_row_data[col] = "TOTAL GERAL"
                    found_label_col = True
                    break
            if not found_label_col and not df_export_with_totals.empty: # If no suitable column found, put in first
                totals_row_data[df_export_with_totals.columns[0]] = "TOTAL GERAL"


        # Convert to DataFrame and concatenate
        totals_df = pd.DataFrame([totals_row_data])
        df_export_with_totals = pd.concat([df_export_with_totals, totals_df], ignore_index=True)

    # --- Exibição da Tabela e Opções Adicionais ---
    # st.markdown("### Dados da Tabela")

    # Botões de Download lado a lado usando colunas
    csv = df_export_with_totals.to_csv(index=False).encode('utf-8')
    import io
    excel_buffer = io.BytesIO()
    df_export_with_totals.to_excel(excel_buffer, index=False, engine='openpyxl')
    excel_buffer.seek(0) # Volta para o início do buffer

    # Cria 3 colunas, mas só usa a primeira para os botões (um ao lado do outro)
    col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
    with col1:
        btn_col_csv, btn_col_xlsx = st.columns(2)
        with btn_col_csv:
            st.download_button(
                label="Baixar dados como CSV",
                data=csv,
                file_name='dados_tabela.csv',
                mime='text/csv',
                help="Baixa os dados atualmente exibidos na tabela (filtrados e com colunas selecionadas) e os totais como um arquivo CSV."
            )
        with btn_col_xlsx:
            st.download_button(
                label="Baixar dados como XLSX",
                data=excel_buffer,
                file_name='dados_tabela.xlsx',
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                help="Baixa os dados atualmente exibidos na tabela (filtrados e com colunas selecionadas) e os totais como um arquivo XLSX."
            )
    # col2 e col3 ficam vazias para espaçamento/estética

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

    # --- Conversão para Numérico das Colunas Mensuráveis ---
    # Lista de colunas que devem ter seus totais exibidos
    measurable_columns = [
        'localWins', 'localFee', 'hands',
        'dolarWins', 'dolarFee', 'dolarRakeback', 'dolarRebate', 'dolarAgentSett',
        'realWins', 'realFee', 'realRakeback', 'realRebate', 'realAgentSett',
        'realRevShare', 'realBPFProfit', 'deal', 'rebate'
    ]

    # Converte colunas mensuráveis para numérico antes da paginação
    for col in measurable_columns:
        if col in df_display.columns and not pd.api.types.is_numeric_dtype(df_display[col]):
            try:
                df_display[col] = pd.to_numeric(df_display[col], errors='coerce')
                print(f"Coluna '{col}' convertida para numérico antes da paginação")
            except Exception as e:
                print(f"Erro ao converter coluna '{col}': {e}")

    start_row = (st.session_state['current_page'] - 1) * rows_per_page
    end_row = start_row + rows_per_page
    df_paginated = df_display.iloc[start_row:end_row]

    # Exibição da Tabela
    st.dataframe(df_paginated, use_container_width=True, hide_index=True)

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
            if st.button("⥂", help="Primeira Página", disabled=(st.session_state['current_page'] == 1 or disable_nav)):
                st.session_state['current_page'] = 1
                st.rerun()

        with nav_cols[1]:
            if st.button("⥆", help="Página Anterior", disabled=(st.session_state['current_page'] <= 1 or disable_nav)):
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
            if st.button("⥅", help="Próxima Página", disabled=(st.session_state['current_page'] >= total_pages or disable_nav)):
                st.session_state['current_page'] += 1
                st.rerun()

        with nav_cols[4]:
            if st.button("⥃", help="Última Página", disabled=(st.session_state['current_page'] == total_pages or disable_nav)):
                st.session_state['current_page'] = total_pages
                st.rerun()

    # --- Totais das Colunas Mensuráveis ---
    st.markdown("### Totais")
    
    # Filtra as colunas mensuráveis que estão presentes no df_display e são numéricas
    columns_to_sum = [col for col in measurable_columns if col in df_display.columns and pd.api.types.is_numeric_dtype(df_display[col])]
    
    print(f"Colunas para somar: {columns_to_sum}")
    print("=============================\n")

    if columns_to_sum:
        # Seção de totais da página atual
        st.markdown("#### 📄 Totais da Página Atual")
        
        # Cria colunas para exibir os totais, limitando a 4 por linha para melhor visualização
        cols_per_row = 4
        num_rows = int(np.ceil(len(columns_to_sum) / cols_per_row))

        for i in range(num_rows):
            current_cols = st.columns(cols_per_row)
            for j in range(cols_per_row):
                idx = i * cols_per_row + j
                if idx < len(columns_to_sum):
                    col_name = columns_to_sum[idx]
                    # Calcula o total apenas dos dados da página atual
                    total_value = df_paginated[col_name].sum()
                    
                    # Diagnóstico específico para valores N/A
                    print(f"DEBUG TOTAIS: Coluna '{col_name}' - Total: {total_value}")
                    print(f"  Valores únicos na página: {df_paginated[col_name].unique()}")
                    print(f"  Contagem de NaN: {df_paginated[col_name].isna().sum()}")
                    print(f"  Contagem de valores válidos: {df_paginated[col_name].notna().sum()}")
                    
                    # Formatação para valores monetários (exemplo simples)
                    try:
                        if pd.isna(total_value) or total_value is None:
                            formatted_value = "N/A"
                        elif 'dolar' in col_name.lower():
                            formatted_value = f"US$ {total_value:,.2f}"
                        elif 'real' in col_name.lower():
                            formatted_value = f"R$ {total_value:,.2f}"
                        else:
                            formatted_value = f"{total_value:,.0f}" # Para mãos, etc.
                    except (ValueError, TypeError):
                        formatted_value = "N/A"

                    with current_cols[j]:
                        st.metric(label=col_name, value=formatted_value)
        
        # Seção de totais gerais (apenas se houver paginação)
        if st.session_state.get('page_size') != "Todas" and total_pages > 1:
            st.markdown("#### 📊 Totais Gerais (Todos os Dados Filtrados)")
            
            for i in range(num_rows):
                current_cols = st.columns(cols_per_row)
                for j in range(cols_per_row):
                    idx = i * cols_per_row + j
                    if idx < len(columns_to_sum):
                        col_name = columns_to_sum[idx]
                        # Calcula o total de todos os dados filtrados
                        total_value = df_display[col_name].sum()
                        
                        # Formatação para valores monetários (exemplo simples)
                        try:
                            if pd.isna(total_value) or total_value is None:
                                formatted_value = "N/A"
                            elif 'dolar' in col_name.lower():
                                formatted_value = f"US$ {total_value:,.2f}"
                            elif 'real' in col_name.lower():
                                formatted_value = f"R$ {total_value:,.2f}"
                            else:
                                formatted_value = f"{total_value:,.0f}" # Para mãos, etc.
                        except (ValueError, TypeError):
                            formatted_value = "N/A"

                        with current_cols[j]:
                            st.metric(label=col_name, value=formatted_value, delta=None)
    else:
        st.info("Nenhuma coluna mensurável selecionada para exibir totais.")
