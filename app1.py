import streamlit as st
from datetime import time
import pandas as pd
import base64
from fpdf import FPDF
from aba import aba_arquivos, aba_bateria, aba_congelamento, aba_continuidade, aba_mudanca_de_patamar, aba_falhas, aba_disponibilidade, aba_relatorio, aba_qualidade_sinal
from utils.auth import tela_login
from utils.encoded_image import encoded_image

st.set_page_config(page_title="GeoWise - Health Check", layout="wide")
pd.set_option("styler.render.max_elements", 2_000_000)

# Inicializar estado da sessão
if "logado" not in st.session_state:
    st.session_state["logado"] = False
if "ultima_contagem_falhas" not in st.session_state:
    st.session_state["ultima_contagem_falhas"] = 0

# Tela de login
if not st.session_state["logado"]:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        tela_login()
    st.stop()

# Exibir logo
st.image(base64.b64decode(encoded_image), width=600)

# Sidebar
st.sidebar.title("GeoWise - Health Check")
arquivos_enviados = st.sidebar.file_uploader(
    "Selecione os arquivos .DAT",
    type=["dat"],
    accept_multiple_files=True,
    key="uploader_arquivos_arquivos"
)

# Tabs
abas = st.tabs([
    "📁 Arquivos",
    "🔴 Falhas de comunicação",
    "📈 Mudança de patamar",
    "✅ Disponibilidade",
    "🔋 Status das Baterias",
    "❄️ Dados Congelados",
    "⏰ Continuidade Temporal",
    "📶 Qualidade do Sinal",
    "📄 Relatórios"
    
])

# Carregamento dos arquivos
with abas[0]:
    dfs_por_arquivo = {}

    if arquivos_enviados:
        nomes_arquivos = [arquivo.name for arquivo in arquivos_enviados]
        st.subheader("Arquivos Carregados:")
        st.write(nomes_arquivos)

        chart_type = st.sidebar.radio(
            "Tipo de gráfico (bateria)", ["Linha"], index=0,
            key="tipo_grafico_aba_arquivos"
        )
        hora_inicio = st.sidebar.time_input("Hora de início", value=time(0, 0))
        hora_fim = st.sidebar.time_input("Hora de fim", value=time(23, 59))
        limiar_variacao = st.sidebar.number_input(
            "Limiar de variação percentual (%)",
            min_value=1.0,
            max_value=100.0,
            value=10.0,
            step=0.5
        ) / 100

        dfs_por_arquivo = aba_arquivos.exibir(
            arquivos_enviados,
            hora_inicio,
            hora_fim,
            limiar_variacao
        )

        for nome_arquivo, df in dfs_por_arquivo.items():
            if not df.empty and "timestamp" in df.columns:
                st.markdown(f"### 🕒 Intervalo de datas detectado no arquivo `{nome_arquivo}`")
                st.write(df["timestamp"].min(), "→", df["timestamp"].max())

    else:
        st.info("Nenhum arquivo carregado ainda.")
        st.markdown("---")
        st.markdown("👈 Use a barra lateral para carregar arquivos .DAT")

# Aplicar filtro de data/hora
if dfs_por_arquivo:
    for nome_arquivo, df in dfs_por_arquivo.items():
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
            df.dropna(subset=['timestamp'], inplace=True)

    todos_ts = pd.concat([df['timestamp'] for df in dfs_por_arquivo.values() if 'timestamp' in df.columns])
    data_min = todos_ts.min().date()
    data_max = todos_ts.max().date()
    data_inicio = st.sidebar.date_input("Data de início", value=data_min, min_value=data_min, max_value=data_max)
    data_fim = st.sidebar.date_input("Data de fim", value=data_max, min_value=data_min, max_value=data_max)
    filtro_data_inicial = pd.to_datetime(f"{data_inicio} {hora_inicio}")
    filtro_data_final = pd.to_datetime(f"{data_fim} {hora_fim}")

    for nome_arquivo in dfs_por_arquivo:
        if 'timestamp' in dfs_por_arquivo[nome_arquivo].columns:
            dfs_por_arquivo[nome_arquivo]['timestamp'] = pd.to_datetime(
                dfs_por_arquivo[nome_arquivo]['timestamp'], errors='coerce')
            dfs_por_arquivo[nome_arquivo] = dfs_por_arquivo[nome_arquivo].dropna(subset=['timestamp'])

            dfs_por_arquivo[nome_arquivo] = dfs_por_arquivo[nome_arquivo][
                (dfs_por_arquivo[nome_arquivo]['timestamp'] >= filtro_data_inicial) &
                (dfs_por_arquivo[nome_arquivo]['timestamp'] <= filtro_data_final)
            ]
        else:
            st.warning(f"⚠️ O arquivo `{nome_arquivo}` não contém a coluna 'timestamp'. Ele será ignorado nos filtros por data.")

# Execução das abas
if dfs_por_arquivo:
    with abas[1]:
        aba_falhas.exibir(dfs_por_arquivo, limiar_variacao)
    with abas[2]:
        aba_mudanca_de_patamar.exibir(dfs_por_arquivo, limiar_variacao)
    with abas[3]:
        aba_disponibilidade.exibir(dfs_por_arquivo, limiar_variacao)
    with abas[4]:
        aba_bateria.exibir(dfs_por_arquivo, chart_type)
    with abas[5]:
        aba_congelamento.exibir(dfs_por_arquivo)
    with abas[6]:
        aba_continuidade.exibir(dfs_por_arquivo)
    with abas[7]:
        aba_qualidade_sinal.exibir(dfs_por_arquivo)
    with abas[8]:
        aba_relatorio.exibir_relatorio_falhas(dfs_por_arquivo)
