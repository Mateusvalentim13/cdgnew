import streamlit as st
import pandas as pd
from utils.destacar_qtd_leituras import destacar_falhas

def exibir(dfs_por_arquivo, limiar_variacao):
    st.subheader("🔴 Falhas de comunicação")

    algum_arquivo_tem_falhas = False  # flag para decidir se exibe mensagem geral

    for nome_arquivo, df_total in dfs_por_arquivo.items():
        col_digit_cols = [col for col in df_total.columns if col.lower().endswith(('_digit', '_hz', '_mm', '_kpa'))]

        df_falhas = pd.DataFrame()
        for col in col_digit_cols:
            df_total[col] = pd.to_numeric(df_total[col], errors='coerce')
            falhas = df_total[df_total[col].isin([-999.0, -998.0])].copy()
            if not falhas.empty:
                falhas['coluna'] = col
                falhas['arquivo_origem'] = nome_arquivo
                df_falhas = pd.concat([df_falhas, falhas], ignore_index=True)

        if df_falhas.empty:
            continue

        algum_arquivo_tem_falhas = True
        st.markdown(f"### 📄 Arquivo: `{nome_arquivo}`")

        num_cells = df_falhas.shape[0] * df_falhas.shape[1]
        if num_cells <= 500_000:
            styled_df = df_falhas.style.format(
                lambda x: str(int(x)) if isinstance(x, float) and x.is_integer() else x
            ).map(
                destacar_falhas,
                subset=[c for c in df_falhas.columns if c not in ['timestamp', 'arquivo_origem', 'coluna']]
            )
            st.dataframe(styled_df, use_container_width=True)
        else:
            st.info("🔍 Muitas células para aplicar estilo. Exibindo sem destaque.")
            st.dataframe(df_falhas, use_container_width=True)

    if not algum_arquivo_tem_falhas:
        st.success("✅ Nenhuma falha de comunicação encontrada em nenhum dos arquivos.")
