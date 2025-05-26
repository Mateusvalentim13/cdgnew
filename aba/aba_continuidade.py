import streamlit as st
import pandas as pd

def exibir(dfs_por_arquivo):
    st.subheader("⏰ Quebras na Ordem Cronológica dos Timestamps")

    encontrou_quebra = False

    for nome_arquivo, df in dfs_por_arquivo.items():
        if df.empty or 'timestamp' not in df.columns:
            continue

        df = df.copy()
        df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
        df = df.dropna(subset=['timestamp'])

        df['timestamp_anterior'] = df['timestamp'].shift(1)
        df['linha'] = df.index

        quebras = df[df['timestamp'] < df['timestamp_anterior']][
            ['linha', 'timestamp_anterior', 'timestamp']
        ].copy()

        if not quebras.empty:
            encontrou_quebra = True
            quebras.insert(0, 'arquivo', nome_arquivo)
            quebras.rename(columns={
                'linha': 'Linha',
                'timestamp_anterior': 'Timestamp anterior',
                'timestamp': 'Timestamp atual'
            }, inplace=True)

            st.markdown(f"### 📄 Arquivo: `{nome_arquivo}`")
            st.dataframe(quebras, use_container_width=True)

    if not encontrou_quebra:
        st.success("✅ Nenhuma quebra de ordem cronológica detectada.")
