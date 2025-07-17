import streamlit as st
import pandas as pd

def display_metric_cards(df: pd.DataFrame, selected_currencies: list):
    st.markdown("### Métricas Principais")

    # Diagnóstico dos dados recebidos
    print(f"\n=== DIAGNÓSTICO MÉTRICAS ===")
    print(f"DataFrame recebido: {len(df)} linhas")
    print(f"Colunas disponíveis: {list(df.columns)}")
    print(f"Moedas selecionadas: {selected_currencies}")
    
    if not df.empty:
        print("Primeiras linhas dos dados:")
        print(df[['dia', 'playerName', 'realWins', 'dolarWins', 'hands']].head(3))
    
    if df.empty:
        st.warning("Nenhum dado disponível para calcular as métricas.")
        return

    # Inicializa os totais
    total_hands = 0
    total_wins_real = 0
    total_wins_dolar = 0
    total_fee_real = 0
    total_fee_dolar = 0
    total_rakeback_real = 0
    total_rakeback_dolar = 0
    total_rebate_real = 0
    total_rebate_dolar = 0

    # Calcula os totais das colunas relevantes
    print("\n=== CÁLCULOS DOS TOTAIS ===")
    
    if 'hands' in df.columns:
        # Tratar valores inválidos na coluna hands
        hands_clean = pd.to_numeric(df['hands'], errors='coerce')
        total_hands = hands_clean.sum()
        print(f"Total hands: {total_hands} (tipo: {type(total_hands)})")
    else:
        print("Coluna 'hands' não encontrada")
        
    if 'realWins' in df.columns:
        total_wins_real = pd.to_numeric(df['realWins'], errors='coerce').sum()
        print(f"Total realWins: {total_wins_real} (tipo: {type(total_wins_real)})")
    else:
        print("Coluna 'realWins' não encontrada")
        
    if 'dolarWins' in df.columns:
        total_wins_dolar = pd.to_numeric(df['dolarWins'], errors='coerce').sum()
        print(f"Total dolarWins: {total_wins_dolar} (tipo: {type(total_wins_dolar)})")
    else:
        print("Coluna 'dolarWins' não encontrada")
        
    if 'realFee' in df.columns:
        total_fee_real = pd.to_numeric(df['realFee'], errors='coerce').sum()
        print(f"Total realFee: {total_fee_real} (tipo: {type(total_fee_real)})")
    else:
        print("Coluna 'realFee' não encontrada")
        
    if 'dolarFee' in df.columns:
        total_fee_dolar = pd.to_numeric(df['dolarFee'], errors='coerce').sum()
        print(f"Total dolarFee: {total_fee_dolar} (tipo: {type(total_fee_dolar)})")
    else:
        print("Coluna 'dolarFee' não encontrada")
        
    if 'realRakeback' in df.columns:
        total_rakeback_real = pd.to_numeric(df['realRakeback'], errors='coerce').sum()
        print(f"Total realRakeback: {total_rakeback_real} (tipo: {type(total_rakeback_real)})")
    else:
        print("Coluna 'realRakeback' não encontrada")
        
    if 'dolarRakeback' in df.columns:
        total_rakeback_dolar = pd.to_numeric(df['dolarRakeback'], errors='coerce').sum()
        print(f"Total dolarRakeback: {total_rakeback_dolar} (tipo: {type(total_rakeback_dolar)})")
    else:
        print("Coluna 'dolarRakeback' não encontrada")
        
    if 'realRebate' in df.columns:
        total_rebate_real = pd.to_numeric(df['realRebate'], errors='coerce').sum()
        print(f"Total realRebate: {total_rebate_real} (tipo: {type(total_rebate_real)})")
    else:
        print("Coluna 'realRebate' não encontrada")
        
    if 'dolarRebate' in df.columns:
        total_rebate_dolar = pd.to_numeric(df['dolarRebate'], errors='coerce').sum()
        print(f"Total dolarRebate: {total_rebate_dolar} (tipo: {type(total_rebate_dolar)})")
    else:
        print("Coluna 'dolarRebate' não encontrada")
    
    print("=============================\n")

    # --- Cards de Métricas Melhorados ---
    col1, col2, col3, col4, col5 = st.columns(5)

    # Card 1: Total de Mãos Jogadas
    with col1:
        hands_display = int(total_hands) if pd.notna(total_hands) else 0
        with st.container():
            st.markdown(f'''
            <div class="metric-card-improved">
                <div class="metric-content">
                    <div class="metric-label">Total de Mãos Jogadas</div>
                    <div class="metric-value">{hands_display:,}</div>
                    <div class="metric-description">Número total de mãos jogadas</div>
                </div>
            </div>
            ''', unsafe_allow_html=True)

    # Card 2: Ganhos
    with col2:
        wins_value = 0
        wins_label = "Ganhos"
        if "Real (R$)" in selected_currencies and "Dólar (US$)" in selected_currencies:
            wins_value = total_wins_real + total_wins_dolar
            wins_label = "Ganhos (R$ + US$)"
            formatted_wins = f"R$ {total_wins_real:,.2f} + US$ {total_wins_dolar:,.2f}"
        elif "Real (R$)" in selected_currencies:
            wins_value = total_wins_real if pd.notna(total_wins_real) else 0
            formatted_wins = f"R$ {wins_value:,.2f}"
        elif "Dólar (US$)" in selected_currencies:
            wins_value = total_wins_dolar if pd.notna(total_wins_dolar) else 0
            formatted_wins = f"US$ {wins_value:,.2f}"
        else:
            formatted_wins = "N/A"

        print(f"DEBUG GANHOS: wins_value={wins_value}, formatted_wins='{formatted_wins}'")

        with st.container():
            st.markdown(f'''
            <div class="metric-card-improved">
                <div class="metric-content">
                    <div class="metric-label">{wins_label}</div>
                    <div class="metric-value">{formatted_wins}</div>
                    <div class="metric-description">Total de ganhos nas moedas selecionadas</div>
                </div>
            </div>
            ''', unsafe_allow_html=True)

    # Card 3: Rakeback
    with col3:
        rakeback_value = 0
        rakeback_label = "Total de Rakeback"
        if "Real (R$)" in selected_currencies and "Dólar (US$)" in selected_currencies:
            rakeback_value = total_rakeback_real + total_rakeback_dolar
            rakeback_label = "Rakeback (R$ + US$)"
            formatted_rakeback = f"R$ {total_rakeback_real:,.2f} + US$ {total_rakeback_dolar:,.2f}"
        elif "Real (R$)" in selected_currencies:
            rakeback_value = total_rakeback_real if pd.notna(total_rakeback_real) else 0
            formatted_rakeback = f"R$ {rakeback_value:,.2f}"
        elif "Dólar (US$)" in selected_currencies:
            rakeback_value = total_rakeback_dolar if pd.notna(total_rakeback_dolar) else 0
            formatted_rakeback = f"US$ {rakeback_value:,.2f}"
        else:
            formatted_rakeback = "N/A"

        print(f"DEBUG RAKEBACK: rakeback_value={rakeback_value}, formatted_rakeback='{formatted_rakeback}'")

        with st.container():
            st.markdown(f'''
            <div class="metric-card-improved">
                <div class="metric-content">
                    <div class="metric-label">{rakeback_label}</div>
                    <div class="metric-value">{formatted_rakeback}</div>
                    <div class="metric-description">Total de rakeback nas moedas selecionadas</div>
                </div>
            </div>
            ''', unsafe_allow_html=True)

    # Card 4: Rebate
    with col4:
        rebate_value = 0
        rebate_label = "Total de Rebate"
        if "Real (R$)" in selected_currencies and "Dólar (US$)" in selected_currencies:
            rebate_value = total_rebate_real + total_rebate_dolar
            rebate_label = "Rebate (R$ + US$)"
            formatted_rebate = f"R$ {total_rebate_real:,.2f} + US$ {total_rebate_dolar:,.2f}"
        elif "Real (R$)" in selected_currencies:
            rebate_value = total_rebate_real if pd.notna(total_rebate_real) else 0
            formatted_rebate = f"R$ {rebate_value:,.2f}"
        elif "Dólar (US$)" in selected_currencies:
            rebate_value = total_rebate_dolar if pd.notna(total_rebate_dolar) else 0
            formatted_rebate = f"US$ {rebate_value:,.2f}"
        else:
            formatted_rebate = "N/A"

        with st.container():
            st.markdown(f'''
            <div class="metric-card-improved">
                <div class="metric-content">
                    <div class="metric-label">{rebate_label}</div>
                    <div class="metric-value">{formatted_rebate}</div>
                    <div class="metric-description">Total de rebate nas moedas selecionadas</div>
                </div>
            </div>
            ''', unsafe_allow_html=True)

    # Card 5: Balanço Final
    with col5:
        final_balance_value = 0
        final_balance_label = "Balanço Final"
        if "Real (R$)" in selected_currencies and "Dólar (US$)" in selected_currencies:
            final_balance_value = (total_wins_real - total_fee_real + total_rakeback_real) + \
                                  (total_wins_dolar - total_fee_dolar + total_rakeback_dolar)
            final_balance_label = "Balanço Final (R$ + US$)"
            formatted_balance = f"R$ {total_wins_real - total_fee_real + total_rakeback_real:,.2f} + US$ {total_wins_dolar - total_fee_dolar + total_rakeback_dolar:,.2f}"
        elif "Real (R$)" in selected_currencies:
            final_balance_value = total_wins_real - total_fee_real + total_rakeback_real
            formatted_balance = f"R$ {final_balance_value:,.2f}"
        elif "Dólar (US$)" in selected_currencies:
            final_balance_value = total_wins_dolar - total_fee_dolar + total_rakeback_dolar
            formatted_balance = f"US$ {final_balance_value:,.2f}"
        else:
            formatted_balance = "N/A"

        # Determinar cor baseado no valor
        if final_balance_value >= 0:
            card_class = "metric-card-improved positive"
        else:
            card_class = "metric-card-improved negative"

        with st.container():
            st.markdown(f'''
            <div class="{card_class}">
                <div class="metric-content">
                    <div class="metric-label">{final_balance_label}</div>
                    <div class="metric-value">{formatted_balance}</div>
                    <div class="metric-description">Balanço final (Ganhos - Taxas + Rakeback)</div>
                </div>
            </div>
            ''', unsafe_allow_html=True)