import streamlit as st
import pandas as pd
import numpy as np
from utils.destacar_qtd_leituras import destacar_mudanca

def exibir(dfs_por_arquivo, limiar_variacao):
    st.subheader("📈 Mudança de Patamar")

    encontrou_dados = False

    for nome_arquivo, df_patamar in dfs_por_arquivo.items():
        if df_patamar.empty:
            continue

        colunas_valores = [col for col in df_patamar.columns if col not in ["timestamp", "arquivo_origem", "coluna"]]
        df_patamar_filtrado = df_patamar.copy()

        for col_val in colunas_valores:
            if col_val in df_patamar_filtrado.columns:
                df_patamar_filtrado[col_val] = pd.to_numeric(
                    df_patamar_filtrado[col_val], errors='coerce'
                ).replace(-999, np.nan)

        df_patamar_filtrado = df_patamar_filtrado.dropna(subset=colunas_valores, how='all')
        df_patamar_display = df_patamar_filtrado.drop(columns=["arquivo_origem", "coluna"], errors='ignore').copy()
        df_patamar_display = df_patamar_display.drop_duplicates(subset=['timestamp'], keep='first').reset_index(drop=True)

        if df_patamar_display.empty:
            continue

        encontrou_dados = True
        st.markdown(f"### 🟧 Mudança de Patamar no Arquivo `{nome_arquivo}` (> {limiar_variacao * 100:.1f}%)")

        linhas_por_pagina = st.slider(
            f"Linhas por página - {nome_arquivo}", 10, 200, 100, step=10, key=f"{nome_arquivo}_slider"
        )
        pagina_atual = st.number_input(
            f"Página - {nome_arquivo}", min_value=1, value=1, step=1, key=f"{nome_arquivo}_page"
        )
        inicio = (pagina_atual - 1) * linhas_por_pagina
        fim = inicio + linhas_por_pagina

        df_paginado = df_patamar_display.iloc[inicio:fim].fillna('')

        try:
            estilo_patamar = df_paginado.style.format(
                lambda x: f"{x:.3f}".rstrip("0").rstrip(".") if isinstance(x, (float, np.number)) and pd.notna(x) else x
            ).map(destacar_mudanca)
            st.dataframe(estilo_patamar, use_container_width=True)
        except Exception as e:
            st.error(f"Erro ao aplicar estilo no arquivo `{nome_arquivo}`: {e}")
            st.dataframe(df_paginado, use_container_width=True)

    if not encontrou_dados:
        st.success("✅ Nenhuma mudança de patamar detectada.")
