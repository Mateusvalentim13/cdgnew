import streamlit as st
import pandas as pd
import numpy as np

def exibir(dfs_por_arquivo):
    st.subheader("❄️ Dados Congelados")

    encontrou_congelamento = False

    for nome_arquivo, df in dfs_por_arquivo.items():
        if df.empty or 'timestamp' not in df.columns:
            continue

        colunas_validas = [
            col for col in df.columns
            if col not in ['timestamp', 'arquivo_origem'] and df[col].dtype in ['float64', 'int64']
        ]

        congelamentos = []

        for col in colunas_validas:
            serie = pd.to_numeric(df[col], errors='coerce')
            timestamps = df['timestamp']

            # Detecta blocos de valores repetidos consecutivos
            blocos = (serie != serie.shift()).cumsum()
            grupos = df.groupby([blocos, serie])

            for (_, valor), grupo in grupos:
                if len(grupo) > 1 and pd.notna(valor):
                    inicio = grupo['timestamp'].iloc[0]
                    fim = grupo['timestamp'].iloc[-1]
                    duracao = fim - inicio
                    congelamentos.append({
                        'timestamp_inicio': inicio,
                        'timestamp_fim': fim,
                        'duração': duracao,
                        'coluna': col,
                        'valor_congelado': valor,
                        'arquivo_origem': nome_arquivo
                    })

        if congelamentos:
            encontrou_congelamento = True
            df_congelado = pd.DataFrame(congelamentos)
            st.markdown(f"### 📄 Arquivo: `{nome_arquivo}`")
            st.dataframe(df_congelado, use_container_width=True)
            st.caption(f"Detectado {len(df_congelado)} intervalo(s) com valores congelados.")
    
    if not encontrou_congelamento:
        st.success("✅ Nenhum dado congelado detectado.")
