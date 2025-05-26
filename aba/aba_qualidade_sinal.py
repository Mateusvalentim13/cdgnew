import streamlit as st
import pandas as pd

def destacar_sinal(valor):
    try:
        num = float(valor)
        if num == -999:
            return ''
        if num > 75:
            return 'background-color: red; color: white;'
    except (ValueError, TypeError):
        return ''
    return ''

def exibir(dfs_por_arquivo):
    st.title("Qualidade do Sinal")
    st.write("Níveis de sinal **RSSIB** e **RSSIL**. Valores acima de 75 indicam sinal **ruim**.")

    for nome_arquivo, df in dfs_por_arquivo.items():
        st.subheader(f"📄 {nome_arquivo}")

        # Selecionar colunas de sinal
        colunas_sinal = [
            col for col in df.columns
            if isinstance(col, str) and (
                col.strip().upper().strip("'\"").endswith("RSSIB") or
                col.strip().upper().strip("'\"").endswith("RSSIL")
            )
        ]

        if not colunas_sinal:
            st.info("Nenhuma coluna de RSSIB ou RSSIL encontrada.")
            continue

        df_sinal = df[colunas_sinal].copy()

        # Tratar valores nulos/ruins
        df_sinal = df_sinal.applymap(lambda x: pd.NA if str(x).strip().lower() in ['none', '-999'] else x)

        # Remover colunas sem falhas
        colunas_com_falha = [
            col for col in df_sinal.columns
            if pd.to_numeric(df_sinal[col], errors='coerce').gt(75).any()
        ]
        df_sinal = df_sinal[colunas_com_falha]

        if df_sinal.empty or df_sinal.shape[1] == 0:
            st.info("Nenhum instrumento com falhas encontrado.")
            continue

        # Adicionar timestamp
        for ts_col in ['timestamp', 'TIMESTAMP', 'TS']:
            if ts_col in df.columns:
                df_sinal.insert(0, 'timestamp', df[ts_col])
                break

        # Ordenar falhas primeiro
        falha_mask = df_sinal[colunas_com_falha].applymap(
            lambda x: float(x) > 75 if pd.notna(x) and str(x).replace('.', '', 1).isdigit() else False
        )
        df_sinal["_tem_falha"] = falha_mask.any(axis=1)
        df_sinal.sort_values(by="_tem_falha", ascending=False, inplace=True)
        df_sinal.drop(columns=["_tem_falha"], inplace=True)

        # Estilo e exibição
        styled = df_sinal.style.map(destacar_sinal, subset=colunas_com_falha).format(na_rep="")
        st.dataframe(styled, use_container_width=True)
