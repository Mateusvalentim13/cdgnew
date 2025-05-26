import streamlit as st
import pandas as pd
import numpy as np

def exibir(dfs_por_arquivo, limiar_variacao):
    st.subheader("✅ Disponibilidade dos Instrumentos")

    houve_dados = False

    for nome_arquivo, df_total in dfs_por_arquivo.items():
        if df_total.empty:
            continue

        col_digitais = [col for col in df_total.columns if col.lower().endswith(('_digit', '_hz', '_mm', '_kpa'))]
        if not col_digitais:
            continue

        df_total[col_digitais] = df_total[col_digitais].apply(pd.to_numeric, errors='coerce')
        df_total.replace([-999, -998], np.nan, inplace=True)

        total_linhas = len(df_total)
        total_lacunas = df_total[col_digitais].isna().sum().sum()
        disponibilidade = 100 * (1 - (total_lacunas / (total_linhas * len(col_digitais)))) if total_linhas > 0 else 0

        st.markdown(f"### 📄 Arquivo: `{nome_arquivo}`")
        st.table(pd.DataFrame({
            "Total Leituras": [total_linhas * len(col_digitais)],
            "Falhas": [total_lacunas],
            "Disponibilidade": [f"{disponibilidade:.2f}%" if total_linhas > 0 else "N/A"]
        }))

        # Por instrumento
        instrumentos_disp = {}
        for col in col_digitais:
            total = df_total[col].notna().sum() + df_total[col].isna().sum()
            falhas = df_total[col].isna().sum()
            disponibilidade_ind = 100 * (1 - falhas / total) if total > 0 else 0
            instrumentos_disp[col] = disponibilidade_ind

        with st.expander(f"📊 Detalhamento por Instrumento - `{nome_arquivo}`"):
            ordem = st.selectbox("Ordenar por:", ["Maior porcentagem", "Menor porcentagem"], key=f"ordem_{nome_arquivo}")
            filtro_busca = st.text_input("🔍 Buscar instrumento:", key=f"filtro_{nome_arquivo}")
            df_indisp = pd.DataFrame(instrumentos_disp.items(), columns=["Instrumento", "Disponibilidade (%)"])
            if filtro_busca:
                df_indisp = df_indisp[df_indisp["Instrumento"].str.contains(filtro_busca, case=False)]
            df_indisp = df_indisp.sort_values(by="Disponibilidade (%)", ascending=(ordem == "Menor porcentagem"))
            st.dataframe(df_indisp.style.format({"Disponibilidade (%)": "{:.2f}%"}), use_container_width=True)

        houve_dados = True

    if not houve_dados:
        st.success("✅ Nenhum dado de disponibilidade encontrado.")
