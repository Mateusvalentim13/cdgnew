# data_loader.py
import pandas as pd
import csv
from io import StringIO
import streamlit as st
from utils import destacar_qtd_leituras

def exibir(arquivos, hora_inicio, hora_fim, limiar_variacao):
    if not arquivos:
        st.markdown(
            "<h4 style='padding-top: 2rem;'>Use a barra lateral para carregar os arquivos e configurar os filtros.</h4>",
            unsafe_allow_html=True
        )
        return None

    dfs_por_arquivo = carregar_dados(arquivos)

    # Aqui você pode aplicar filtros de data/hora se necessário

    return dfs_por_arquivo


def carregar_dados(arquivos):
    dfs_por_arquivo = {}
    for arquivo in arquivos:
        df = processar_dat(arquivo)
        if not df.empty:
            dfs_por_arquivo[arquivo.name] = df
    return dfs_por_arquivo


def processar_dat(arquivo):
    try:
        texto = arquivo.read().decode("utf-8", errors='ignore')
        f = StringIO(texto)
        linhas = list(csv.reader(f, delimiter=','))

        linha_colunas_idx = None
        possiveis_nomes = ['timestamp', 'data', 'datahora', 'tempo', 'datetime']

       
        for i, linha in enumerate(linhas[:20]):
            linha_normalizada = [
                c.strip().lower().replace('"', '').replace(',', '') for c in linha
            ]
            if any(p in linha_normalizada for p in possiveis_nomes):
                linha_colunas_idx = i
                break

        if linha_colunas_idx is None:
            st.error(f"❌ Cabeçalho com campo de tempo ('timestamp', 'data', etc.) não encontrado em `{arquivo.name}`.")
            return pd.DataFrame()

        colunas_raw = linhas[linha_colunas_idx]
        colunas = [c.strip().lower().replace('"', '').replace(',', '') for c in colunas_raw]

        dados = linhas[linha_colunas_idx + 1:]
        dados_validos = [linha for linha in dados if len(linha) == len(colunas)]

        if len(dados_validos) < len(dados):
            st.warning(f"{len(dados) - len(dados_validos)} linhas ignoradas em `{arquivo.name}` por erro de estrutura.")

        df = pd.DataFrame(dados_validos, columns=colunas)
        df['arquivo_origem'] = arquivo.name

        for c in df.columns:
            if c in possiveis_nomes:
                df.rename(columns={c: 'timestamp'}, inplace=True)
                break

        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'], format="%Y-%m-%d %H:%M:%S", errors='coerce')

        return df

    except Exception as e:
        st.error(f"❌ Erro ao processar `{arquivo.name}`: {e}")
        return pd.DataFrame()




